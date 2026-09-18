<?php

namespace App\Http\Controllers;

use App\Jobs\ProcessAutoClipJob;
use App\Models\VideoClip;
use App\Models\VideoProject;
use App\Services\VideoProcessorService;
use Illuminate\Http\Request;
use Inertia\Inertia;
use Inertia\Response;

class VideoClipController extends Controller
{
    /**
     * Display the Studio Dashboard
     */
    public function index(): Response
    {
        $projects = VideoProject::with('clips')
            ->orderBy('created_at', 'desc')
            ->take(10)
            ->get();

        return Inertia::render('Dashboard', [
            'recentProjects' => $projects,
            'hasApiKey' => !empty(env('GEMINI_API_KEY')),
        ]);
    }

    /**
     * Start auto-clip pipeline for a video URL
     */
    public function store(Request $request, VideoProcessorService $service)
    {
        $request->validate([
            'video_url' => 'required|url',
        ]);

        $project = VideoProject::create([
            'video_url' => $request->video_url,
            'status' => 'pending',
            'progress' => 5,
            'status_message' => 'Menginisialisasi pipeline unduh dan analisis video...',
        ]);

        // Launch background processing asynchronously so HTTP request returns instantly
        $artisan = base_path('artisan');
        if (strtoupper(substr(PHP_OS, 0, 3)) === 'WIN') {
            pclose(popen("start /B php \"{$artisan}\" project:process {$project->id} > NUL 2>&1", "r"));
        } else {
            exec("php \"{$artisan}\" project:process {$project->id} > /dev/null 2>&1 &");
        }

        return response()->json([
            'success' => true,
            'project' => $project->load('clips')
        ]);
    }

    /**
     * Upload and analyze a local short video file
     */
    public function uploadVideo(Request $request, VideoProcessorService $service)
    {
        @set_time_limit(300);
        @ini_set('max_execution_time', '300');

        $request->validate([
            'video_file' => 'required|file|mimes:mp4,mov,webm,mkv,avi|max:524288',
            'channel_name' => 'nullable|string|max:100',
            'custom_title' => 'nullable|string|max:150',
        ]);

        $file = $request->file('video_file');
        $originalName = $file->getClientOriginalName();
        $userTitle = $request->input('custom_title');
        
        if ($userTitle && trim($userTitle)) {
            $projectTitle = trim($userTitle);
        } else {
            $cleanTitle = pathinfo($originalName, PATHINFO_FILENAME);
            $cleanTitle = str_replace(['_', '-'], ' ', $cleanTitle);
            $projectTitle = ucwords($cleanTitle);
        }

        $project = VideoProject::create([
            'video_url' => 'upload://' . $originalName,
            'title' => $projectTitle,
            'channel' => $request->input('channel_name', 'Original Creator'),
            'status' => 'analyzing',
            'progress' => 15,
            'status_message' => 'Mengekstrak audio & menganalisis transkrip ucapan...',
        ]);

        $projectDir = storage_path("app/public/projects/{$project->id}");
        if (!is_dir($projectDir)) {
            mkdir($projectDir, 0755, true);
        }

        $extension = $file->getClientOriginalExtension() ?: 'mp4';
        $filename = "source_{$project->id}.{$extension}";
        $file->move($projectDir, $filename);

        $localFilePath = "{$projectDir}/{$filename}";
        $publicVideoUrl = "/storage/projects/{$project->id}/{$filename}";

        $project->update([
            'video_path' => $publicVideoUrl,
        ]);

        try {
            $service->processLocalVideo($project, $localFilePath, $userTitle);

            return response()->json([
                'success' => true,
                'project' => $project->fresh()->load('clips')
            ]);
        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'error' => $e->getMessage(),
                'project' => $project->fresh()
            ], 500);
        }
    }

    /**
     * Poll project status and progress
     */
    public function show(int $id)
    {
        $project = VideoProject::with('clips')->findOrFail($id);

        return response()->json([
            'success' => true,
            'project' => $project
        ]);
    }

    /**
     * Render an AI-detected clip or re-render with new aspect ratio
     */
    public function renderClip(Request $request, int $clipId, VideoProcessorService $service)
    {
        @set_time_limit(300);
        @ini_set('max_execution_time', '300');

        $request->validate([
            'aspect_ratio' => 'nullable|in:9:16,16:9,1:1',
        ]);

        $clip = VideoClip::findOrFail($clipId);
        $aspectRatio = $request->input('aspect_ratio', $clip->aspect_ratio ?: '9:16');

        try {
            $result = $service->renderClip($clip, $aspectRatio);
            return response()->json([
                'success' => true,
                'clip' => $clip->fresh()
            ]);
        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'error' => $e->getMessage()
            ], 500);
        }
    }

    /**
     * Render an AI detected clip with auto-meme sound effects and punch-zoom
     */
    public function renderMemeClip(Request $request, int $clipId, VideoProcessorService $service)
    {
        @set_time_limit(300);
        @ini_set('max_execution_time', '300');

        $request->validate([
            'aspect_ratio' => 'nullable|in:9:16,16:9,1:1',
            'custom_cues' => 'nullable|array',
            'intensity' => 'nullable|in:santai,rame,barbar',
        ]);

        $clip = VideoClip::findOrFail($clipId);
        $aspectRatio = $request->input('aspect_ratio', $clip->aspect_ratio ?: '9:16');
        $customCues = $request->input('custom_cues', []);
        $intensity = $request->input('intensity', 'rame');

        try {
            $result = $service->renderMemeClip($clip, $aspectRatio, $customCues, $intensity);
            return response()->json([
                'success' => true,
                'clip' => $clip->fresh()
            ]);
        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'error' => $e->getMessage()
            ], 500);
        }
    }

    /**
     * Create and render a custom/manual clip
     */
    public function createCustomClip(Request $request, int $projectId, VideoProcessorService $service)
    {
        @set_time_limit(300);
        @ini_set('max_execution_time', '300');

        $request->validate([
            'title' => 'required|string|max:100',
            'start_time' => 'required|numeric|min:0',
            'end_time' => 'required|numeric|gt:start_time',
            'aspect_ratio' => 'required|in:9:16,16:9,1:1',
        ]);

        $project = VideoProject::findOrFail($projectId);

        $duration = $request->end_time - $request->start_time;

        $clip = VideoClip::create([
            'video_project_id' => $project->id,
            'title' => $request->title,
            'start_time' => $request->start_time,
            'end_time' => $request->end_time,
            'duration' => $duration,
            'virality_score' => 90,
            'hook' => 'Custom User Clip',
            'reason' => 'Dipilih secara manual oleh pengguna.',
            'aspect_ratio' => $request->aspect_ratio,
            'status' => 'pending',
        ]);

        try {
            $service->renderClip($clip, $request->aspect_ratio);
            return response()->json([
                'success' => true,
                'clip' => $clip->fresh()
            ]);
        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'error' => $e->getMessage()
            ], 500);
        }
    }

    /**
     * Delete a project
     */
    public function destroy(int $id)
    {
        $project = VideoProject::findOrFail($id);
        $project->delete();

        return response()->json(['success' => true]);
    }
}

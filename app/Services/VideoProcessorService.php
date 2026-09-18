<?php

namespace App\Services;

use App\Models\VideoProject;
use App\Models\VideoClip;
use Illuminate\Support\Facades\Log;
use Symfony\Component\Process\Process;

class VideoProcessorService
{
    protected string $basePath;
    protected string $pythonPath = 'python';

    public function __construct()
    {
        $this->basePath = base_path();
    }

    /**
     * Build process environment with Windows system variables
     */
    protected function getProcessEnv(): array
    {
        return array_merge($_SERVER, $_ENV, [
            'SYSTEMROOT' => getenv('SystemRoot') ?: 'C:\\Windows',
            'WINDIR' => getenv('WINDIR') ?: 'C:\\Windows',
            'PATH' => getenv('PATH') ?: 'C:\\Windows\\system32;C:\\Windows',
            'PYTHONUNBUFFERED' => '1',
            'PYTHONWARNINGS' => 'ignore',
        ]);
    }

    /**
     * Run full auto-clip pipeline for a project
     */
    public function processProject(VideoProject $project): void
    {
        $projectDir = storage_path("app/public/projects/{$project->id}");
        if (!is_dir($projectDir)) {
            mkdir($projectDir, 0755, true);
        }

        try {
            // 1. Download YouTube Video & Subtitles
            $project->update([
                'status' => 'downloading',
                'progress' => 25,
                'status_message' => 'Mengunduh stream video & metadata YouTube...'
            ]);

            $downloadScript = base_path('execution/yt_downloader.py');
            $process = new Process([
                $this->pythonPath,
                $downloadScript,
                '--url', $project->video_url,
                '--output-dir', $projectDir
            ], null, $this->getProcessEnv());
            $process->setTimeout(600);
            $process->run();

            $metadataFile = "{$projectDir}/metadata.json";
            if (!file_exists($metadataFile)) {
                $err = $process->getErrorOutput() ?: $process->getOutput();
                throw new \Exception("Gagal mengunduh video: " . substr($err, -200));
            }

            $metadataOutput = json_decode(file_get_contents($metadataFile), true);
            if (!$metadataOutput || empty($metadataOutput['video_path'])) {
                throw new \Exception("File metadata video tidak valid.");
            }

            // Relative video URL for public access
            $videoFilename = basename($metadataOutput['video_path']);
            $publicVideoUrl = "/storage/projects/{$project->id}/{$videoFilename}";

            $project->update([
                'video_id' => $metadataOutput['video_id'] ?? 'video',
                'title' => $metadataOutput['title'] ?? 'Video YouTube',
                'channel' => $metadataOutput['uploader'] ?? 'Channel',
                'thumbnail' => $metadataOutput['thumbnail'] ?? '',
                'duration' => $metadataOutput['duration'] ?? 60.0,
                'video_path' => $publicVideoUrl,
                'metadata' => $metadataOutput,
                'progress' => 60,
                'status' => 'analyzing',
                'status_message' => 'AI sedang menganalisis dialog & mengekstrak hook viral...'
            ]);

            // 2. AI Highlight & Viral Moment Extraction
            $aiScript = base_path('execution/ai_highlight_extractor.py');
            $apiKey = env('GEMINI_API_KEY', '');
            
            $aiArgs = [$this->pythonPath, $aiScript, '--project-dir', $projectDir];
            if (!empty($apiKey)) {
                $aiArgs[] = '--api-key';
                $aiArgs[] = $apiKey;
            }

            $aiProcess = new Process($aiArgs, null, $this->getProcessEnv());
            $aiProcess->setTimeout(180);
            $aiProcess->run();

            $highlightsFile = "{$projectDir}/highlights.json";
            $clips = [];
            if (file_exists($highlightsFile)) {
                $clips = json_decode(file_get_contents($highlightsFile), true) ?: [];
            }

            // Clear old pending clips if retrying
            $project->clips()->where('status', 'pending')->delete();

            // Save highlight clips into DB
            foreach ($clips as $clipData) {
                VideoClip::create([
                    'video_project_id' => $project->id,
                    'title' => $clipData['title'] ?? 'Viral Highlight',
                    'start_time' => (float) $clipData['start_time'],
                    'end_time' => (float) $clipData['end_time'],
                    'duration' => (float) ($clipData['duration'] ?? ($clipData['end_time'] - $clipData['start_time'])),
                    'virality_score' => (int) ($clipData['virality_score'] ?? 85),
                    'hook' => $clipData['hook'] ?? '',
                    'reason' => $clipData['reason'] ?? '',
                    'caption' => $clipData['caption'] ?? '',
                    'hashtags' => $clipData['hashtags'] ?? ['#shorts', '#viral', '#trending'],
                    'meme_cues' => $clipData['meme_cues'] ?? null,
                    'aspect_ratio' => '9:16',
                    'status' => 'pending',
                ]);
            }

            $project->update([
                'status' => 'ready',
                'progress' => 100,
                'status_message' => 'Momen viral berhasil dideteksi! Klip siap di-render.',
                'highlights' => $clips
            ]);

        } catch (\Exception $e) {
            Log::error("Video processing error for project {$project->id}: " . $e->getMessage());
            $project->update([
                'status' => 'failed',
                'progress' => 0,
                'status_message' => 'Error: ' . $e->getMessage()
            ]);
        }
    }

    /**
     * Render a specific clip using FFmpeg
     */
    public function renderClip(VideoClip $clip, string $aspectRatio = '9:16'): array
    {
        $project = $clip->project;
        $projectDir = storage_path("app/public/projects/{$project->id}");
        $metadataFile = "{$projectDir}/metadata.json";

        if (!file_exists($metadataFile)) {
            throw new \Exception("Project source files not found.");
        }

        $metadata = json_decode(file_get_contents($metadataFile), true);
        $inputVideo = $metadata['video_path'];

        if (!file_exists($inputVideo)) {
            $candidate = $projectDir . '/' . basename($inputVideo);
            if (file_exists($candidate)) {
                $inputVideo = $candidate;
            }
        }

        $clipFilename = "clip_{$clip->id}_{$aspectRatio}_" . time() . ".mp4";
        $clipFilename = str_replace(':', '-', $clipFilename);
        $outputFile = "{$projectDir}/{$clipFilename}";

        $clip->update([
            'status' => 'rendering',
            'aspect_ratio' => $aspectRatio
        ]);

        $cutterScript = base_path('execution/video_cutter.py');
        $process = new Process([
            $this->pythonPath,
            $cutterScript,
            '--input-video', $inputVideo,
            '--start', (string) $clip->start_time,
            '--end', (string) $clip->end_time,
            '--output', $outputFile,
            '--aspect-ratio', $aspectRatio
        ], null, $this->getProcessEnv());

        $process->setTimeout(300);
        $process->run();

        if (!file_exists($outputFile) || filesize($outputFile) === 0) {
            $clip->update(['status' => 'failed']);
            $err = $process->getErrorOutput() ?: $process->getOutput();
            throw new \Exception("Gagal me-render klip: " . substr($err, -200));
        }

        $fileSizeMb = round(filesize($outputFile) / (1024 * 1024), 2);
        $publicClipUrl = "/storage/projects/{$project->id}/{$clipFilename}";
        
        $clip->update([
            'status' => 'completed',
            'clip_path' => $publicClipUrl,
            'file_size_mb' => $fileSizeMb,
        ]);

        return [
            'success' => true,
            'clip_url' => $publicClipUrl,
            'file_size_mb' => $fileSizeMb
        ];
    }

    /**
     * Process a locally uploaded video: extract audio, transcribe speech, generate contextual YouTube Shorts captions
     */
    public function processLocalVideo(VideoProject $project, string $localVideoPath, ?string $customTitle = null): void
    {
        $projectDir = storage_path("app/public/projects/{$project->id}");
        if (!is_dir($projectDir)) {
            mkdir($projectDir, 0755, true);
        }

        try {
            $project->update([
                'status' => 'analyzing',
                'progress' => 40,
                'status_message' => 'Mengekstrak audio & menganalisis dialog ucapan...'
            ]);

            $analyzerScript = base_path('execution/local_video_analyzer.py');
            $apiKey = env('GEMINI_API_KEY', '');

            $args = [
                $this->pythonPath,
                $analyzerScript,
                '--video-path', $localVideoPath,
                '--project-dir', $projectDir,
                '--channel-name', $project->channel ?: 'Original Creator',
            ];

            if (!empty($customTitle)) {
                $args[] = '--custom-title';
                $args[] = $customTitle;
            }

            if (!empty($apiKey)) {
                $args[] = '--api-key';
                $args[] = $apiKey;
            }

            $process = new Process($args, null, $this->getProcessEnv());
            $process->setTimeout(300);
            $process->run();

            $metadataFile = "{$projectDir}/metadata.json";
            if (!file_exists($metadataFile)) {
                $err = $process->getErrorOutput() ?: $process->getOutput();
                throw new \Exception("Gagal menganalisis video lokal: " . substr($err, -200));
            }

            $result = json_decode(file_get_contents($metadataFile), true);
            if (!$result) {
                throw new \Exception("Hasil analisis metadata tidak valid.");
            }

            $duration = (float) ($result['duration'] ?? 30.0);
            $title = $result['title'] ?? $project->title;

            // Clear old clips if any
            $project->clips()->delete();

            // Create primary clip for the uploaded short video
            $clip = VideoClip::create([
                'video_project_id' => $project->id,
                'title' => $title,
                'start_time' => 0.0,
                'end_time' => $duration,
                'duration' => $duration,
                'virality_score' => 98,
                'hook' => $result['transcript'] ? mb_substr($result['transcript'], 0, 80) : $title,
                'reason' => 'Transkrip ucapan berhasil dianalisis dengan caption 100% sinkron isi video.',
                'caption' => $result['caption'] ?? '',
                'hashtags' => $result['hashtags'] ?? ['#shorts', '#viral', '#trending'],
                'meme_cues' => $result['meme_cues'] ?? null,
                'aspect_ratio' => '9:16',
                'status' => 'pending',
            ]);

            $highlights = [[
                'title' => $title,
                'start_time' => 0.0,
                'end_time' => $duration,
                'duration' => $duration,
                'virality_score' => 98,
                'hook' => $clip->hook,
                'reason' => $clip->reason,
                'caption' => $clip->caption,
                'hashtags' => $clip->hashtags,
                'meme_cues' => $clip->meme_cues,
            ]];

            $project->update([
                'title' => $title,
                'duration' => $duration,
                'status' => 'ready',
                'progress' => 100,
                'status_message' => 'Transkripsi audio & caption YouTube Shorts berhasil dibuat!',
                'metadata' => $result,
                'highlights' => $highlights,
            ]);

        } catch (\Exception $e) {
            Log::error("Local video processing error for project {$project->id}: " . $e->getMessage());
            $project->update([
                'status' => 'failed',
                'progress' => 0,
                'status_message' => 'Error: ' . $e->getMessage()
            ]);
            throw $e;
        }
    }

    /**
     * Render a clip with auto-meme sound effects & dynamic punch-zoom
     */
    public function renderMemeClip(VideoClip $clip, string $aspectRatio = '9:16', array $customCues = [], string $intensity = 'rame'): array
    {
        $project = $clip->project;
        $projectDir = storage_path("app/public/projects/{$project->id}");
        $metadataFile = "{$projectDir}/metadata.json";

        if (!file_exists($metadataFile)) {
            throw new \Exception("File sumber proyek tidak ditemukan.");
        }

        $metadata = json_decode(file_get_contents($metadataFile), true);
        $inputVideo = $metadata['video_path'];

        if (!file_exists($inputVideo)) {
            $candidate = $projectDir . '/' . basename($inputVideo);
            if (file_exists($candidate)) {
                $inputVideo = $candidate;
            }
        }

        // Pastikan asset SFX sudah siap
        $manifestFile = storage_path('app/public/memes/sfx/manifest.json');
        if (!file_exists($manifestFile)) {
            $setupScript = base_path('execution/setup_meme_assets.py');
            $setupProc = new Process([$this->pythonPath, $setupScript], null, $this->getProcessEnv());
            $setupProc->run();
        }

        // Tentukan meme timeline yang akan digunakan
        $cues = !empty($customCues) ? $customCues : ($clip->meme_cues ?: []);
        if (empty($cues)) {
            $dur = (float) $clip->duration;
            $cues = [
                ['time' => 1.5, 'effect' => 'vine_boom', 'punch_zoom' => true, 'screen_shake' => true, 'duration' => 0.6],
                ['time' => round(min($dur * 0.35, 12.0), 1), 'effect' => 'metal_pipe', 'punch_zoom' => true, 'screen_shake' => true, 'duration' => 0.5],
                ['time' => round(min($dur * 0.65, 22.0), 1), 'effect' => 'taco_bell', 'punch_zoom' => true, 'screen_shake' => true, 'duration' => 0.5],
                ['time' => round(min($dur * 0.88, 30.0), 1), 'effect' => 'laugh_wheeze', 'punch_zoom' => false, 'screen_shake' => false, 'duration' => 0.5]
            ];
        }

        $clipFilename = "clip_{$clip->id}_meme_{$aspectRatio}_{$intensity}_" . time() . ".mp4";
        $clipFilename = str_replace(':', '-', $clipFilename);
        $outputFile = "{$projectDir}/{$clipFilename}";
        $timelineJsonFile = "{$projectDir}/timeline_meme_{$clip->id}.json";
        file_put_contents($timelineJsonFile, json_encode($cues, JSON_UNESCAPED_SLASHES));

        $clip->update(['status' => 'rendering']);

        $memeScript = base_path('execution/video_meme_editor.py');
        $sfxDir = storage_path('app/public/memes/sfx');

        $process = new Process([
            $this->pythonPath,
            $memeScript,
            '--input-video', $inputVideo,
            '--start', (string) $clip->start_time,
            '--end', (string) $clip->end_time,
            '--output', $outputFile,
            '--aspect-ratio', $aspectRatio,
            '--meme-timeline', $timelineJsonFile,
            '--sfx-dir', $sfxDir,
            '--intensity', $intensity,
        ], null, $this->getProcessEnv());

        $process->setTimeout(300);
        $process->run();

        if (!file_exists($outputFile) || filesize($outputFile) === 0) {
            $clip->update(['status' => 'failed']);
            $err = $process->getErrorOutput() ?: $process->getOutput();
            throw new \Exception("Gagal me-render Auto-Meme: " . substr($err, -250));
        }

        $fileSizeMb = round(filesize($outputFile) / (1024 * 1024), 2);
        $publicClipUrl = "/storage/projects/{$project->id}/{$clipFilename}";

        $clip->update([
            'status' => 'completed',
            'meme_clip_path' => $publicClipUrl,
            'meme_file_size_mb' => $fileSizeMb,
            'meme_cues' => $cues,
        ]);

        return [
            'success' => true,
            'clip_url' => $publicClipUrl,
            'meme_clip_url' => $publicClipUrl,
            'meme_file_size_mb' => $fileSizeMb,
            'cues_applied' => $cues,
        ];
    }
}


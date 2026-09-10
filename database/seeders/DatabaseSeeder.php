<?php

namespace Database\Seeders;

use App\Models\VideoProject;
use App\Models\VideoClip;
use Illuminate\Database\Seeder;

class DatabaseSeeder extends Seeder
{
    /**
     * Seed the application's database.
     */
    public function run(): void
    {
        $project = VideoProject::create([
            'id' => 1,
            'video_url' => 'https://www.youtube.com/watch?v=jNQXAC9IVRw',
            'video_id' => 'jNQXAC9IVRw',
            'title' => 'Me at the zoo - YouTube First Historic Video',
            'channel' => 'jawed',
            'thumbnail' => 'https://i.ytimg.com/vi/jNQXAC9IVRw/maxresdefault.jpg',
            'duration' => 19.0,
            'status' => 'ready',
            'progress' => 100,
            'status_message' => 'Highlights detected successfully! Ready to render clips.',
            'video_path' => '/storage/projects/1/jNQXAC9IVRw.mp4',
        ]);

        VideoClip::create([
            'video_project_id' => $project->id,
            'title' => 'Opening Hook: Jawed & The Elephants',
            'start_time' => 0.0,
            'end_time' => 10.0,
            'duration' => 10.0,
            'virality_score' => 96,
            'hook' => 'Alright, so here we are in front of the elephants...',
            'reason' => 'Momen bersejarah pertama di YouTube dengan opening santai dan engaging.',
            'aspect_ratio' => '9:16',
            'status' => 'completed',
            'clip_path' => '/storage/projects/1/clip_1_9-16.mp4',
            'file_size_mb' => 2.83,
        ]);

        VideoClip::create([
            'video_project_id' => $project->id,
            'title' => 'The Trunk Observation Punchline',
            'start_time' => 7.0,
            'end_time' => 18.0,
            'duration' => 11.0,
            'virality_score' => 91,
            'hook' => 'The cool thing about these guys is that they have really, really long trunks...',
            'reason' => 'Punchline penutup video yang khas dan singkat.',
            'aspect_ratio' => '9:16',
            'status' => 'pending',
        ]);
    }
}

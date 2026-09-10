<?php

use Illuminate\Foundation\Inspiring;
use Illuminate\Support\Facades\Artisan;
use App\Models\VideoProject;
use App\Services\VideoProcessorService;

Artisan::command('inspire', function () {
    $this->comment(Inspiring::quote());
})->purpose('Display an inspiring quote');

Artisan::command('project:process {id}', function (int $id, VideoProcessorService $service) {
    $project = VideoProject::find($id);
    if (!$project) {
        $this->error("Project {$id} not found");
        return 1;
    }
    $this->info("Processing project {$id}...");
    $service->processProject($project);
    $this->info("Project {$id} completed!");
    return 0;
})->purpose('Process YouTube video auto-clip pipeline asynchronously');


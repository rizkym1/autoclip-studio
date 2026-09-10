<?php

namespace App\Jobs;

use App\Models\VideoProject;
use App\Services\VideoProcessorService;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Foundation\Queue\Queueable;

class ProcessAutoClipJob implements ShouldQueue
{
    use Queueable;

    public int $timeout = 600;

    public function __construct(public VideoProject $project)
    {
    }

    public function handle(VideoProcessorService $service): void
    {
        $service->processProject($this->project);
    }
}

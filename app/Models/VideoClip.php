<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class VideoClip extends Model
{
    use HasFactory;

    protected $guarded = [];

    protected $casts = [
        'start_time' => 'float',
        'end_time' => 'float',
        'duration' => 'float',
        'virality_score' => 'integer',
        'file_size_mb' => 'float',
        'meme_file_size_mb' => 'float',
        'hashtags' => 'array',
        'meme_cues' => 'array',
    ];

    public function project(): BelongsTo
    {
        return $this->belongsTo(VideoProject::class, 'video_project_id');
    }
}

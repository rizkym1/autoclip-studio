<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\HasMany;

class VideoProject extends Model
{
    use HasFactory;

    protected $guarded = [];

    protected $casts = [
        'metadata' => 'array',
        'highlights' => 'array',
        'duration' => 'float',
        'progress' => 'integer',
    ];

    public function clips(): HasMany
    {
        return $this->hasMany(VideoClip::class);
    }
}

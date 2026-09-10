<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        Schema::table('video_clips', function (Blueprint $table) {
            $table->string('meme_clip_path')->nullable()->after('clip_path');
            $table->float('meme_file_size_mb')->nullable()->after('meme_clip_path');
            $table->json('meme_cues')->nullable()->after('meme_file_size_mb');
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::table('video_clips', function (Blueprint $table) {
            $table->dropColumn(['meme_clip_path', 'meme_file_size_mb', 'meme_cues']);
        });
    }
};

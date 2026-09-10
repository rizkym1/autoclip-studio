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
        Schema::create('video_projects', function (Blueprint $table) {
            $table->id();
            $table->string('video_url');
            $table->string('video_id')->nullable();
            $table->string('title')->nullable();
            $table->string('channel')->nullable();
            $table->text('thumbnail')->nullable();
            $table->float('duration')->default(0);
            $table->string('status')->default('pending'); // pending, downloading, analyzing, ready, failed
            $table->integer('progress')->default(0);
            $table->string('status_message')->default('Initializing project...');
            $table->string('video_path')->nullable();
            $table->json('metadata')->nullable();
            $table->json('highlights')->nullable();
            $table->timestamps();
        });

        Schema::create('video_clips', function (Blueprint $table) {
            $table->id();
            $table->foreignId('video_project_id')->constrained('video_projects')->onDelete('cascade');
            $table->string('title');
            $table->float('start_time');
            $table->float('end_time');
            $table->float('duration');
            $table->integer('virality_score')->default(85);
            $table->text('hook')->nullable();
            $table->text('reason')->nullable();
            $table->string('aspect_ratio')->default('9:16');
            $table->string('status')->default('pending'); // pending, rendering, completed, failed
            $table->string('clip_path')->nullable();
            $table->float('file_size_mb')->nullable();
            $table->timestamps();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('video_clips');
        Schema::dropIfExists('video_projects');
    }
};

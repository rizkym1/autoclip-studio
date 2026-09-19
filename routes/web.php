<?php

use App\Http\Controllers\VideoClipController;
use Illuminate\Support\Facades\Route;

// Studio Dashboard
Route::get('/', [VideoClipController::class, 'index'])->name('home');

// Project Management APIs
Route::post('/api/projects', [VideoClipController::class, 'store'])->name('projects.store');
Route::post('/api/upload-video', [VideoClipController::class, 'uploadVideo'])->name('videos.upload');
Route::get('/api/projects/{id}', [VideoClipController::class, 'show'])->name('projects.show');
Route::delete('/api/projects/{id}', [VideoClipController::class, 'destroy'])->name('projects.destroy');

// Clip Rendering APIs
Route::post('/api/clips/{id}/render', [VideoClipController::class, 'renderClip'])->name('clips.render');
Route::post('/api/clips/{id}/render-meme', [VideoClipController::class, 'renderMemeClip'])->name('clips.render_meme');
Route::put('/api/clips/{id}/cues', [VideoClipController::class, 'updateMemeCues'])->name('clips.update_cues');
Route::post('/api/projects/{id}/custom-clip', [VideoClipController::class, 'createCustomClip'])->name('clips.custom');

<?php

/**
 * AutoClip Studio - Robust PHP Built-in Server Router
 */

$uri = urldecode(
    parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH) ?? ''
);

$publicPath = __DIR__ . '/public';
$filePath = $publicPath . $uri;

// Serve existing static assets from public/ directory
if ($uri !== '/' && file_exists($filePath) && !is_dir($filePath)) {
    $ext = strtolower(pathinfo($filePath, PATHINFO_EXTENSION));
    $mimes = [
        'css'   => 'text/css',
        'js'    => 'application/javascript',
        'json'  => 'application/json',
        'png'   => 'image/png',
        'jpg'   => 'image/jpeg',
        'jpeg'  => 'image/jpeg',
        'webp'  => 'image/webp',
        'gif'   => 'image/gif',
        'svg'   => 'image/svg+xml',
        'ico'   => 'image/x-icon',
        'mp4'   => 'video/mp4',
        'mov'   => 'video/quicktime',
        'webm'  => 'video/webm',
        'mkv'   => 'video/x-matroska',
        'woff'  => 'font/woff',
        'woff2' => 'font/woff2',
        'ttf'   => 'font/ttf',
        'vtt'   => 'text/vtt',
    ];

    if (isset($mimes[$ext])) {
        header("Content-Type: {$mimes[$ext]}");
    }
    header('Content-Length: ' . filesize($filePath));
    readfile($filePath);
    exit;
}

// Route all dynamic application requests to Laravel
require_once $publicPath . '/index.php';

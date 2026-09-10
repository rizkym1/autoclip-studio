#!/usr/bin/env python3
"""
Tier 3 Muscle: Deterministic Video Cutter & Smart Aspect Ratio Renderer
Optimized for high-speed multi-threaded FFmpeg rendering.
"""

import sys
import os
import json
import argparse
import subprocess
import imageio_ffmpeg

def cut_video(input_video, start_time, end_time, output_file, aspect_ratio='9:16'):
    if not os.path.exists(input_video):
        print(json.dumps({'error': f"Input video not found: {input_video}"}), file=sys.stderr)
        sys.exit(1)

    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()

    start_sec = float(start_time)
    end_sec = float(end_time)
    duration = end_sec - start_sec

    if duration <= 0:
        print(json.dumps({'error': "Invalid duration: end_time must be greater than start_time"}), file=sys.stderr)
        sys.exit(1)

    # Base FFmpeg fast-seek command
    cmd = [
        ffmpeg_exe,
        '-y',
        '-ss', str(start_sec),
        '-t', str(duration),
        '-i', input_video,
        '-threads', '0',
    ]

    # Filter graph optimized for speed & aesthetic blur
    if aspect_ratio == '9:16':
        # Fast downscaled blur for instant processing
        filter_complex = (
            "[0:v]scale=270:480:force_original_aspect_ratio=increase,crop=270:480,boxblur=8:2,scale=1080:1920:flags=fast_bilinear[bg];"
            "[0:v]scale=1080:-2:force_original_aspect_ratio=decrease[fg];"
            "[bg][fg]overlay=(W-w)/2:(H-h)/2[v]"
        )
        cmd.extend([
            '-filter_complex', filter_complex,
            '-map', '[v]',
            '-map', '0:a?',
            '-c:v', 'libx264',
            '-preset', 'veryfast',
            '-crf', '23',
            '-c:a', 'aac',
            '-b:a', '128k',
            '-movflags', '+faststart',
            output_file
        ])
    elif aspect_ratio == '1:1':
        filter_complex = (
            "[0:v]scale=1080:1080:force_original_aspect_ratio=increase,crop=1080:1080[v]"
        )
        cmd.extend([
            '-filter_complex', filter_complex,
            '-map', '[v]',
            '-map', '0:a?',
            '-c:v', 'libx264',
            '-preset', 'veryfast',
            '-crf', '23',
            '-c:a', 'aac',
            '-b:a', '128k',
            '-movflags', '+faststart',
            output_file
        ])
    else:
        # 16:9 Standard landscape
        cmd.extend([
            '-c:v', 'libx264',
            '-preset', 'veryfast',
            '-crf', '22',
            '-c:a', 'aac',
            '-b:a', '128k',
            '-movflags', '+faststart',
            output_file
        ])

    try:
        process = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )

        file_size = os.path.getsize(output_file) if os.path.exists(output_file) else 0

        res = {
            'success': True,
            'output_file': output_file,
            'aspect_ratio': aspect_ratio,
            'start_time': start_sec,
            'end_time': end_sec,
            'duration': round(duration, 2),
            'file_size_bytes': file_size,
            'file_size_mb': round(file_size / (1024 * 1024), 2)
        }
        print(json.dumps(res))
        return res

    except subprocess.CalledProcessError as e:
        err_res = {
            'success': False,
            'error': f"FFmpeg error: {e.stderr[-300:] if e.stderr else str(e)}"
        }
        print(json.dumps(err_res), file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Cut and format video clip with FFmpeg')
    parser.add_argument('--input-video', required=True, help='Path to source video file')
    parser.add_argument('--start', required=True, type=float, help='Start time in seconds')
    parser.add_argument('--end', required=True, type=float, help='End time in seconds')
    parser.add_argument('--output', required=True, help='Path to destination MP4 file')
    parser.add_argument('--aspect-ratio', default='9:16', choices=['9:16', '16:9', '1:1'], help='Output aspect ratio')
    args = parser.parse_args()

    cut_video(args.input_video, args.start, args.end, args.output, args.aspect_ratio)

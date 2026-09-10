#!/usr/bin/env python3
"""
Tier 3 Muscle: Deterministic YouTube & Media Downloader with Auto Subtitles
Downloads high-quality video streams and auto subtitles (.vtt) for speech timestamp analysis.
"""

import sys
import os
import json
import warnings
import argparse

warnings.filterwarnings("ignore")
os.environ['PYTHONWARNINGS'] = 'ignore'

import yt_dlp
import imageio_ffmpeg

def download_video(url, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    
    # Configure resilient yt-dlp options with auto-subtitles
    ydl_opts = {
        'format': 'bestvideo[ext=mp4][height<=1080]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': os.path.join(output_dir, '%(id)s.%(ext)s'),
        'ffmpeg_location': ffmpeg_exe,
        'merge_output_format': 'mp4',
        'quiet': True,
        'no_warnings': True,
        'noplaylist': True,
        'extract_flat': False,
        'writeautomaticsub': True,
        'writesubtitles': True,
        'subtitleslangs': ['id', 'id-orig', 'en', 'en-orig'],
        'subtitlesformat': 'vtt',
        'ignoreerrors': True,
        'socket_timeout': 30,
        'retries': 3,
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'ios', 'web'],
            }
        }
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            if not info:
                raise Exception("Could not extract video metadata from URL")

            video_id = info.get('id', 'video')
            title = info.get('title', 'Unknown Video')
            duration = info.get('duration', 0)
            thumbnail = info.get('thumbnail', '')
            uploader = info.get('uploader', info.get('channel', 'Unknown Channel'))
            description = info.get('description', '')

            video_file = os.path.join(output_dir, f"{video_id}.mp4")
            
            if not os.path.exists(video_file):
                for f in os.listdir(output_dir):
                    if f.startswith(video_id) and f.endswith('.mp4'):
                        video_file = os.path.join(output_dir, f)
                        break
                if not os.path.exists(video_file):
                    for f in os.listdir(output_dir):
                        if f.endswith('.mp4'):
                            video_file = os.path.join(output_dir, f)
                            break

            metadata = {
                'success': True,
                'video_id': video_id,
                'title': title,
                'duration': duration or 60.0,
                'duration_formatted': f"{int(duration // 60):02d}:{int(duration % 60):02d}" if duration else "01:00",
                'thumbnail': thumbnail,
                'uploader': uploader,
                'channel': uploader,
                'description': description[:500] if description else '',
                'video_path': video_file,
            }

            metadata_path = os.path.join(output_dir, 'metadata.json')
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)

            print(json.dumps(metadata))
            return metadata

    except Exception as e:
        err_res = {
            'success': False,
            'error': str(e)
        }
        print(json.dumps(err_res))
        sys.exit(1)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Download YouTube Video and metadata')
    parser.add_argument('--url', required=True, help='YouTube Video URL')
    parser.add_argument('--output-dir', required=True, help='Destination directory')
    args = parser.parse_args()

    download_video(args.url, args.output_dir)

#!/usr/bin/env python3
"""
Tier 3 Muscle: Deterministic High-Density Video Meme & SFX Editor
Orchestrates FFmpeg filter complexes to inject viral sound effects, dynamic punch-zooms,
and camera screen shakes with millisecond precision on short-form videos (9:16, 16:9, 1:1).
Supports multi-level intensity: santai, rame, and barbar.
"""

import os
import sys
import json
import argparse
import subprocess
import imageio_ffmpeg

HEAVY_SHAKE_SOUNDS = {
    'vine_boom', 'metal_pipe', 'taco_bell', 'fart_reverb', 'emotional_damage', 'bonk'
}

def check_has_audio(input_file, ffmpeg_exe):
    """Checks if the source video has an active audio stream"""
    try:
        cmd = [
            ffmpeg_exe,
            '-i', input_file,
            '-t', '0.1',
            '-vn',
            '-f', 'null',
            '-'
        ]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return "Audio:" in res.stderr
    except Exception:
        return True

def edit_video_with_memes(
    input_video,
    start_time,
    end_time,
    output_file,
    aspect_ratio='9:16',
    meme_cues=None,
    sfx_dir=None,
    intensity='rame'
):
    if not os.path.exists(input_video):
        print(json.dumps({'error': f"Input video not found: {input_video}"}), file=sys.stderr)
        sys.exit(1)

    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()

    start_sec = max(0.0, float(start_time))
    end_sec = float(end_time)
    duration = end_sec - start_sec

    if duration <= 0:
        print(json.dumps({'error': "Invalid duration: end_time must be greater than start_time"}), file=sys.stderr)
        sys.exit(1)

    # Locate SFX directory
    if not sfx_dir or not os.path.exists(sfx_dir):
        curr = os.path.dirname(os.path.abspath(__file__))
        sfx_dir = os.path.abspath(os.path.join(curr, '..', 'storage', 'app', 'public', 'memes', 'sfx'))

    # Parse meme cues
    cues = []
    if meme_cues:
        if isinstance(meme_cues, str):
            try:
                if os.path.exists(meme_cues):
                    with open(meme_cues, 'r', encoding='utf-8') as f:
                        cues = json.load(f)
                else:
                    cues = json.loads(meme_cues)
            except Exception as e:
                print(f"Warning: Failed to parse meme_cues: {e}", file=sys.stderr)
                cues = []
        elif isinstance(meme_cues, list):
            cues = meme_cues

    # Filter cues based on intensity
    if intensity == 'santai' and len(cues) > 3:
        # Keep only hook and climax
        cues = [cues[0], cues[-1]]
    elif intensity == 'rame' and len(cues) > 6:
        cues = cues[:6]

    # Validate and normalize cues within clip range (relative 0.0 to duration)
    valid_cues = []
    for c in cues:
        raw_t = float(c.get('time', c.get('offset', c.get('timestamp', 0.0))))
        if raw_t >= start_sec and raw_t <= end_sec:
            rel_t = raw_t - start_sec
        elif raw_t >= 0.0 and raw_t <= duration:
            rel_t = raw_t
        else:
            continue

        effect = str(c.get('effect', c.get('sound', 'vine_boom'))).lower()
        if not effect.endswith('.wav') and not effect.endswith('.mp3'):
            sound_file = f"{effect}.wav"
        else:
            sound_file = effect

        sound_path = os.path.join(sfx_dir, sound_file)
        if not os.path.exists(sound_path):
            sound_path = os.path.join(sfx_dir, 'vine_boom.wav')
            sound_file = 'vine_boom.wav'
            effect = 'vine_boom'

        punch_zoom = bool(c.get('punch_zoom', True))
        
        # Screen shake: explicitly passed or auto-enabled for heavy bass/impact
        screen_shake = bool(c.get('screen_shake', effect in HEAVY_SHAKE_SOUNDS))
        zoom_dur = float(c.get('duration', 0.65 if intensity == 'barbar' else 0.8))
        vol = float(c.get('volume', 1.0))

        valid_cues.append({
            'time': round(rel_t, 2),
            'sound_path': sound_path,
            'sound_name': effect,
            'punch_zoom': punch_zoom,
            'screen_shake': screen_shake,
            'zoom_duration': zoom_dur,
            'volume': vol
        })

    # Sort cues chronologically
    valid_cues.sort(key=lambda x: x['time'])

    # Group sound inputs to avoid opening the same sound file multiple times
    unique_sounds = {}
    sound_inputs = []
    for cue in valid_cues:
        sp = cue['sound_path']
        if sp not in unique_sounds and os.path.exists(sp):
            unique_sounds[sp] = len(sound_inputs) + 1  # input index 1, 2, ...
            sound_inputs.append(sp)

    has_audio = check_has_audio(input_video, ffmpeg_exe)

    # Base FFmpeg command
    cmd = [
        ffmpeg_exe,
        '-y',
        '-ss', str(start_sec),
        '-t', str(duration),
        '-i', input_video,
    ]

    # Add each unique sound effect file as input
    for sp in sound_inputs:
        cmd.extend(['-i', sp])

    # If original video has no audio, add a silent audio input
    silent_input_idx = None
    if not has_audio:
        cmd.extend(['-f', 'lavfi', '-i', f'anullsrc=r=44100:cl=stereo:d={duration}'])
        silent_input_idx = len(sound_inputs) + 1

    # Construct video filter complex
    filter_parts = []

    # 1. Aspect Ratio Canvas
    if aspect_ratio == '9:16':
        filter_parts.append(
            "[0:v]scale=270:480:force_original_aspect_ratio=increase,crop=270:480,boxblur=8:2,scale=1080:1920:flags=fast_bilinear[bg]"
        )
        filter_parts.append(
            "[0:v]scale=1080:-2:force_original_aspect_ratio=decrease[fg]"
        )
        filter_parts.append(
            "[bg][fg]overlay=(W-w)/2:(H-h)/2[base_v]"
        )
    elif aspect_ratio == '1:1':
        filter_parts.append(
            "[0:v]scale=1080:1080:force_original_aspect_ratio=increase,crop=1080:1080[base_v]"
        )
    else:
        # 16:9 landscape
        filter_parts.append(
            "[0:v]scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2[base_v]"
        )

    # 2. Dynamic Camera Effects (Punch Zoom & Screen Shake)
    zoom_cues = [c for c in valid_cues if c['punch_zoom'] and not c['screen_shake']]
    shake_cues = [c for c in valid_cues if c['screen_shake']]

    split_count = 1 + (1 if zoom_cues else 0) + (1 if shake_cues else 0)
    current_v = "[base_v]"

    if split_count > 1:
        split_labels = [f"[v_branch_{i}]" for i in range(split_count)]
        filter_parts.append(f"[base_v]split={split_count}{''.join(split_labels)}")
        current_v = split_labels[0]
        branch_idx = 1

        # A. Apply Punch Zoom if any
        if zoom_cues:
            z_branch = split_labels[branch_idx]
            branch_idx += 1
            z_enables = [
                f"between(t\\,{zc['time']:.2f}\\,{min(duration, zc['time'] + zc['zoom_duration']):.2f})"
                for zc in zoom_cues
            ]
            z_expr = "+".join(z_enables)
            if aspect_ratio == '9:16':
                filter_parts.append(f"{z_branch}crop=in_w*0.78:in_h*0.78:(in_w-out_w)/2:(in_h-out_h)/2,scale=1080:1920[v_zoomed]")
            else:
                filter_parts.append(f"{z_branch}crop=in_w*0.78:in_h*0.78:(in_w-out_w)/2:(in_h-out_h)/2,scale=1920:1080[v_zoomed]")
            filter_parts.append(f"{current_v}[v_zoomed]overlay=0:0:enable={z_expr}[v_after_zoom]")
            current_v = "[v_after_zoom]"

        # B. Apply Screen Shake if any
        if shake_cues:
            s_branch = split_labels[branch_idx]
            branch_idx += 1
            s_enables = [
                f"between(t\\,{sc['time']:.2f}\\,{min(duration, sc['time'] + min(0.5, sc['zoom_duration'])):.2f})"
                for sc in shake_cues
            ]
            s_expr = "+".join(s_enables)
            if aspect_ratio == '9:16':
                filter_parts.append(f"{s_branch}crop=w=1040:h=1880:x='20+20*sin(t*65)':y='20+20*cos(t*65)',scale=1080:1920[v_shaken]")
            else:
                filter_parts.append(f"{s_branch}crop=w=1860:h=1040:x='30+25*sin(t*65)':y='20+20*cos(t*65)',scale=1920:1080[v_shaken]")
            filter_parts.append(f"{current_v}[v_shaken]overlay=0:0:enable={s_expr}[v_after_shake]")
            current_v = "[v_after_shake]"

    filter_parts.append(f"{current_v}null[final_v]")

    # 3. Audio Multi-Channel SFX Mixing
    audio_mix_inputs = []
    base_audio_label = "[0:a]" if has_audio else f"[{silent_input_idx}:a]"
    audio_mix_inputs.append("[base_a]")
    filter_parts.append(f"{base_audio_label}volume=1.0[base_a]")

    if sound_inputs and valid_cues:
        sound_usage = {}
        for c in valid_cues:
            inp_idx = unique_sounds.get(c['sound_path'])
            if inp_idx:
                sound_usage[inp_idx] = sound_usage.get(inp_idx, 0) + 1

        split_branches = {}
        for inp_idx, count in sound_usage.items():
            if count > 1:
                branches = [f"[sfx_{inp_idx}_{b}]" for b in range(count)]
                filter_parts.append(f"[{inp_idx}:a]asplit={count}{''.join(branches)}")
                split_branches[inp_idx] = branches
            else:
                split_branches[inp_idx] = [f"[{inp_idx}:a]"]

        cue_branches_tracker = {}
        for idx, cue in enumerate(valid_cues):
            inp_idx = unique_sounds.get(cue['sound_path'])
            if not inp_idx:
                continue

            used_idx = cue_branches_tracker.get(inp_idx, 0)
            branch_label = split_branches[inp_idx][used_idx]
            cue_branches_tracker[inp_idx] = used_idx + 1

            delay_ms = max(0, int(cue['time'] * 1000))
            vol = cue['volume']
            out_label = f"[delayed_sfx_{idx}]"
            filter_parts.append(
                f"{branch_label}adelay={delay_ms}|{delay_ms},volume={vol:.2f}{out_label}"
            )
            audio_mix_inputs.append(out_label)

    if len(audio_mix_inputs) > 1:
        total_inputs = len(audio_mix_inputs)
        filter_parts.append(
            f"{''.join(audio_mix_inputs)}amix=inputs={total_inputs}:duration=first:dropout_transition=2[final_a]"
        )
    else:
        filter_parts.append("[base_a]null[final_a]")

    full_filter_complex = ";".join(filter_parts)

    cmd.extend([
        '-filter_complex', full_filter_complex,
        '-map', '[final_v]',
        '-map', '[final_a]',
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
            'intensity': intensity,
            'start_time': start_sec,
            'end_time': end_sec,
            'duration': round(duration, 2),
            'meme_count': len(valid_cues),
            'punch_zooms': len(zoom_cues),
            'screen_shakes': len(shake_cues),
            'cues_applied': valid_cues,
            'file_size_bytes': file_size,
            'file_size_mb': round(file_size / (1024 * 1024), 2)
        }
        print(json.dumps(res, indent=2))
        return res

    except subprocess.CalledProcessError as e:
        err_res = {
            'success': False,
            'error': f"FFmpeg error: {e.stderr[-400:] if e.stderr else str(e)}"
        }
        print(json.dumps(err_res), file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Render video clip with dynamic punch-zoom, screen shake and meme soundboard')
    parser.add_argument('--input-video', required=True, help='Path to source video file')
    parser.add_argument('--start', required=False, type=float, default=0.0, help='Start time in seconds')
    parser.add_argument('--end', required=True, type=float, help='End time in seconds')
    parser.add_argument('--output', required=True, help='Path to destination MP4 file')
    parser.add_argument('--aspect-ratio', default='9:16', choices=['9:16', '16:9', '1:1'], help='Output aspect ratio')
    parser.add_argument('--meme-timeline', required=False, default=None, help='JSON array or filepath of meme cues')
    parser.add_argument('--sfx-dir', required=False, default=None, help='Directory containing SFX wav files')
    parser.add_argument('--intensity', default='rame', choices=['santai', 'rame', 'barbar'], help='Meme density level')
    args = parser.parse_args()

    edit_video_with_memes(
        args.input_video,
        args.start,
        args.end,
        args.output,
        args.aspect_ratio,
        args.meme_timeline,
        args.sfx_dir,
        args.intensity
    )

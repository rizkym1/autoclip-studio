#!/usr/bin/env python3
"""
Tier 3 Muscle: Local Short Video Speech-to-Text & Viral Shorts Copywriting Engine
Extracts audio from uploaded video files, transcribes spoken dialogue,
and generates ultra-engaging, casual (bahasa gaul santai) YouTube Shorts / TikTok captions matching the video content 100%.
"""

import sys
import os
import re
import json
import math
import wave
import struct
import subprocess
import argparse
import imageio_ffmpeg

if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

def detect_audio_meme_peaks(wav_path, duration):
    """Calculates RMS audio energy envelope and detects 4-8 multi-peak action moments & comedic valleys"""
    default_cues = [
        {'time': 1.5, 'effect': 'vine_boom', 'punch_zoom': True, 'screen_shake': True, 'reason': 'Hook awal video'},
        {'time': round(min(duration * 0.35, 12.0), 1), 'effect': 'metal_pipe', 'punch_zoom': True, 'screen_shake': True, 'reason': 'Momen blunder / aksi'},
        {'time': round(min(duration * 0.65, 22.0), 1), 'effect': 'taco_bell', 'punch_zoom': True, 'screen_shake': True, 'reason': 'Momen klimaks / hit'},
        {'time': round(min(duration * 0.85, 28.0), 1), 'effect': 'laugh_wheeze', 'punch_zoom': False, 'screen_shake': False, 'reason': 'Ending lucu'}
    ]
    if not os.path.exists(wav_path):
        return default_cues

    try:
        with wave.open(wav_path, 'rb') as wf:
            framerate = wf.getframerate()
            nchannels = wf.getnchannels()
            sampwidth = wf.getsampwidth()
            nframes = wf.getnframes()
            
            chunk_size = max(1, int(framerate * 0.25))
            rms_values = []
            
            while True:
                frames = wf.readframes(chunk_size)
                if not frames:
                    break
                if sampwidth == 2:
                    count = len(frames) // 2
                    shorts = struct.unpack(f"<{count}h", frames)
                    samples = [shorts[i] / 32768.0 for i in range(0, count, nchannels)]
                else:
                    samples = [0.0]
                
                if samples:
                    rms = math.sqrt(sum(s * s for s in samples) / len(samples))
                else:
                    rms = 0.0
                rms_values.append(rms)

        if not rms_values:
            return default_cues

        avg_rms = sum(rms_values) / len(rms_values)
        step = 0.25
        cues = []

        # Always start with an energetic hook at ~1.2s - 2.0s
        cues.append({
            'time': 1.5,
            'effect': 'vine_boom',
            'punch_zoom': True,
            'screen_shake': True,
            'reason': 'Hook awal pembuka video'
        })

        # Sound rotation pools
        heavy_hits = ['metal_pipe', 'taco_bell', 'vine_boom', 'emotional_damage', 'bonk']
        hype_sounds = ['run', 'anime_wow', 'bonk', 'emotional_damage']
        awkward_sounds = ['huh', 'windows_error', 'bruh', 'cricket']
        ending_sounds = ['laugh_wheeze', 'fart_reverb', 'directed_by']

        heavy_idx = 0
        hype_idx = 0
        awkward_idx = 0

        # Scan for peaks with minimum 2.5s separation
        last_cue_time = 1.5
        for idx in range(2, len(rms_values) - 2):
            t = idx * step
            if t < 3.0 or t > (duration - 2.0):
                continue
            if (t - last_cue_time) < 2.5:
                continue

            val = rms_values[idx]
            prev_val = rms_values[idx - 1]
            next_val = rms_values[idx + 1]

            # Local maximum peak
            if val > prev_val and val > next_val:
                if val > (avg_rms * 1.35):
                    # Heavy action peak -> Screen Shake + Punch Zoom
                    sound = heavy_hits[heavy_idx % len(heavy_hits)]
                    heavy_idx += 1
                    cues.append({
                        'time': round(t, 1),
                        'effect': sound,
                        'punch_zoom': True,
                        'screen_shake': True,
                        'reason': f'Lonjakan aksi/audio heboh di {round(t, 1)}s'
                    })
                    last_cue_time = t
                elif val > (avg_rms * 1.05):
                    # Medium action peak
                    sound = hype_sounds[hype_idx % len(hype_sounds)]
                    hype_idx += 1
                    cues.append({
                        'time': round(t, 1),
                        'effect': sound,
                        'punch_zoom': True,
                        'screen_shake': False,
                        'reason': f'Momen seru di {round(t, 1)}s'
                    })
                    last_cue_time = t

            # Awkward silence / sudden drop
            elif val < (avg_rms * 0.35) and avg_rms > 0.02 and (t - last_cue_time) >= 3.5:
                sound = awkward_sounds[awkward_idx % len(awkward_sounds)]
                awkward_idx += 1
                cues.append({
                    'time': round(t, 1),
                    'effect': sound,
                    'punch_zoom': False,
                    'screen_shake': False,
                    'reason': f'Jeda hening/canggung di {round(t, 1)}s'
                })
                last_cue_time = t

        # Add ending outro meme if clip is longer than 15s and gap allows
        if duration >= 15.0 and (duration - last_cue_time) >= 2.5:
            cues.append({
                'time': round(duration - 1.8, 1),
                'effect': ending_sounds[0],
                'punch_zoom': False,
                'screen_shake': False,
                'reason': 'Ending penutup kocak'
            })

        cues.sort(key=lambda x: x['time'])
        return cues if len(cues) >= 2 else default_cues
    except Exception as e:
        print(f"Audio peak detection notice: {e}", file=sys.stderr)
        return default_cues

def extract_audio(video_path, output_wav):
    """Extracts mono 16kHz WAV audio using FFmpeg"""
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    cmd = [
        ffmpeg_exe,
        '-y',
        '-i', video_path,
        '-vn',
        '-acodec', 'pcm_s16le',
        '-ar', '16000',
        '-ac', '1',
        output_wav
    ]
    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    return output_wav

def get_video_duration(video_path):
    """Gets video duration using FFprobe / FFmpeg"""
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    cmd = [ffmpeg_exe, '-i', video_path]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    m = re.search(r'Duration:\s*(\d{2}):(\d{2}):(\d{2}\.\d+)', res.stderr)
    if m:
        h, mi, sec = int(m.group(1)), int(m.group(2)), float(m.group(3))
        return round(h * 3600 + mi * 60 + sec, 2)
    return 30.0

def clean_transcript_text(text):
    """Cleans up raw transcript, removes garbage repeating numbers or symbols"""
    if not text or not isinstance(text, str):
        return ""
    t = text.strip()
    # Filter out repeating digits / punctuation like '1. 1. 3. 4.' or '1 2 3'
    if re.match(r'^[\s\d\.\,\!\?\-]+$', t):
        return ""
    if len(t) < 3:
        return ""
    return t

def transcribe_with_google_sr(wav_path):
    """Transcribes audio using Google SpeechRecognition with language fallback"""
    try:
        import speech_recognition as sr
        r = sr.Recognizer()
        with sr.AudioFile(wav_path) as source:
            try:
                r.adjust_for_ambient_noise(source, duration=0.2)
            except Exception:
                pass
            audio_data = r.record(source)

        # 1. Try English (common for voice commands / global audio)
        try:
            text = r.recognize_google(audio_data, language='en-US')
            clean = clean_transcript_text(text)
            if clean:
                return clean
        except Exception:
            pass

        # 2. Try Indonesian
        try:
            text = r.recognize_google(audio_data, language='id-ID')
            clean = clean_transcript_text(text)
            if clean:
                return clean
        except Exception:
            pass

    except Exception as e:
        print(f"Google SR notice: {e}", file=sys.stderr)
    return ""

def transcribe_with_whisper(wav_path):
    """Transcribes audio using local faster-whisper model"""
    try:
        from faster_whisper import WhisperModel
        model = WhisperModel("tiny", device="cpu", compute_type="int8")
        segments, info = model.transcribe(wav_path, beam_size=3)
        text_parts = [segment.text.strip() for segment in segments if segment.text.strip()]
        full_text = " ".join(text_parts).strip()
        clean = clean_transcript_text(full_text)
        if clean:
            return clean
    except Exception as e:
        print(f"Faster-whisper notice: {e}", file=sys.stderr)
    return ""

def transcribe_audio_master(wav_path):
    """Master transcription pipeline: runs Google STT and Whisper, picks best real speech"""
    google_text = transcribe_with_google_sr(wav_path)
    whisper_text = transcribe_with_whisper(wav_path)

    candidates = [t for t in [google_text, whisper_text] if t and len(t) > 2]
    if not candidates:
        return ""

    # Sort by number of words to pick the most descriptive sentence
    candidates.sort(key=lambda x: len(x.split()), reverse=True)
    return candidates[0]

def build_anti_copyright_caption(synopsis, hook, discussion_q, channel_name, video_source):
    """Constructs a casual, high-converting YouTube Shorts caption with Fair Use"""
    channel_credit = channel_name.strip() if (channel_name and channel_name.strip() and channel_name != 'Original Creator') else "Original Creator"
    video_source_title = video_source.strip() if video_source and not video_source.lower().startswith('source') else "Original Content"

    clean_hook = hook.strip(' "\'')
    hook_str = f'"{clean_hook}"' if clean_hook else ""

    parts = [synopsis]
    if hook_str:
        parts.append(hook_str)
    parts.append(f"💬 {discussion_q}")
    parts.append(
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📌 CREDITS & SOURCE:\n"
        f"🎬 Video: {video_source_title}\n"
        f"👤 Creator / Source: @{channel_credit}\n\n"
        "⚠️ FAIR USE DISCLAIMER:\n"
        "Video ini digunakan untuk tujuan hiburan, komentar, dan edukasi (Fair Use Section 107 Copyright Act 1976). Hak cipta sepenuhnya milik pemilik konten asli."
    )

    return "\n\n".join(parts)

def generate_contextual_caption(transcript, user_topic, duration, api_key=None, channel_name="Original Creator"):
    """Generates viral, casual (bahasa gaul santai) YouTube Shorts captions matching the speech or visual theme"""
    clean_t = clean_transcript_text(transcript)
    topic = user_topic.strip() if user_topic and not user_topic.lower().startswith('source') else ""

    # If Gemini API key is available
    if api_key:
        try:
            from google import genai
            client = genai.Client(api_key=api_key)

            context_desc = f"Dialog Ucapan di Video: \"{clean_t}\"" if clean_t else f"Topik Video: \"{topic}\""
            prompt = f"""
Kamu adalah Content Creator & Video Strategist viral top YouTube Shorts & TikTok di Indonesia.
Video berdurasi {duration} detik baru saja diunggah.
{context_desc}

Instruksi Gaya Bahasa:
- Gunakan Bahasa Indonesia GAUL, SANTAI, EKSPRESIF, dan KEKINIAN (ala kreator Shorts/TikTok asli, seperti: 'gokil', 'asli ngakak', 'bisa-bisanya', 'wkwk', 'gaes', 'endingnya', 'relate banget').
- DILARANG KERAS menggunakan bahasa baku/kaku seperti 'cuplikan momen pilihan berdurasi X detik...', 'momen menarik di video ini saat...', 'visual dan aksi seru yang sayang banget...'.
- Judul harus sangat catchy, memancing rasa penasaran, di bawah 60 karakter, ditambah emoji & #shorts.

Format Response JSON ONLY:
{{
  "title": "...",
  "hook": "...",
  "synopsis": "2-3 kalimat seru, santai, dan menjelaskan apa yang terjadi di video tanpa kaku",
  "discussion_question": "pertanyaan santai pemicu komentar penonton",
  "hashtags": ["#shorts", "#viral", "#ngakak", "#fyp", ...],
  "meme_cues": [
    {{"time": 2.5, "effect": "vine_boom", "punch_zoom": true, "reason": "Momen awal pembuka / aksi"}},
    {{"time": 8.0, "effect": "bonk", "punch_zoom": true, "reason": "Momen klimaks / kejutan"}}
  ]
}}
"""
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
            )
            resp_text = response.text.strip()
            if resp_text.startswith("```json"):
                resp_text = resp_text[7:]
            if resp_text.startswith("```"):
                resp_text = resp_text[3:]
            if resp_text.endswith("```"):
                resp_text = resp_text[:-3]

            data = json.loads(resp_text.strip())
            title = data.get('title')
            hook = data.get('hook', clean_t or "Momen Pilihan")
            synopsis = data.get('synopsis')
            disc_q = data.get('discussion_question')
            hashtags = data.get('hashtags', ["#shorts", "#viral", "#trending", "#fyp"])
            gemini_cues = data.get('meme_cues', [])

            if title and synopsis:
                caption = build_anti_copyright_caption(synopsis, hook, disc_q, channel_name, topic or title.replace(' #shorts', ''))
                return {
                    "title": title,
                    "hook": hook,
                    "synopsis": synopsis,
                    "discussion_question": disc_q,
                    "caption": caption,
                    "hashtags": hashtags,
                    "transcript": clean_t or "Audio non-vokal / instrumental",
                    "meme_cues": gemini_cues
                }
        except Exception as e:
            print(f"Gemini API notice: {e}", file=sys.stderr)

    # Deterministic Casual & Viral Copywriting Engine (Bahasa Santai / Gaul)
    lower_t = clean_t.lower()
    lower_topic = topic.lower()

    # 1. Gaming / Mobile Legends (MLBB) / Maniac / Savage Detection
    gaming_keywords = ['maniac', 'savage', 'mobile legends', 'mlbb', 'gameplay', 'game', 'gaming', 'triple kill', 'wipe out', 'legendary', 'hero', 'fast hand', 'by one', 'war', 'fanny', 'ling', 'gusion', 'hayabusa', 'lancelot', 'chou']
    is_gaming = any(kw in lower_t for kw in gaming_keywords) or any(kw in lower_topic for kw in gaming_keywords) or 'game' in lower_topic

    if is_gaming:
        if 'savage' in lower_t or 'savage' in lower_topic:
            title = "Detik-detik SAVAGE di Mobile Legends! 🔥 Auto Rata 1 Tim! 😱 #shorts"
            hook = "Momen SAVAGE Epic Mobile Legends — Fast Hand Gila-gilaan!"
            synopsis = "Gokil banget detik-detik dapet SAVAGE di Land of Dawn! 🔥 Positioning rapih, fast hand, dan eksekusi war super bersih bikin musuh langsung rata. Tonton gameplay gilanya sampe abis gaes! ⚔️🎮"
            disc_q = "Siapa nih user hero ini juga? Kasih rating gameplay tadi 1-10 di kolom komentar ya! 👇🔥"
        else:
            title = "Detik-detik Dapet MANIAC di Mobile Legends! 🔥 Rata Semua! 😱 #shorts"
            hook = "Momen Maniac Mobile Legends — Fast Hand & War Gila-gilaan!"
            synopsis = "Detik-detik momen seru dapet MANIAC di Land of Dawn! 🔥 Positioning rapih, fast hand, dan eksekusi pas war bener-bener bikin musuh auto rata. Nyaris dapet Savage gak nih gaes? Tonton sampe abis ya! ⚔️🎮"
            disc_q = "Siapa nih yang sering dapet Maniac tapi di-sampah pas mau Savage? Coba absen dan curhat di kolom komentar! 👇🤣"

        hashtags = ["#shorts", "#mobilelegends", "#mlbb", "#maniac", "#savage", "#mlbbindonesia", "#gameplay", "#mlbbcreatorcamp", "#fyp", "#gaming"]

    elif 'google' in lower_t or 'katy perry' in lower_t or 'siri' in lower_t or 'alexa' in lower_t:
        if 'katy perry' in lower_t or 'play' in lower_t or 'lagu' in lower_t or 'music' in lower_t:
            title = "Disuruh Play Katy Perry, Responnya Malah Gini 😂😭 #shorts"
            hook = "Pas minta Google putar lagu, endingnya bikin ngakak wkwk!"
            synopsis = f"Bisa-bisanya pas dibilang \"{clean_t}\" responnya langsung bikin kaget wkwk 🤣 Tonton sampe abis biar paham serunya gaes!"
            disc_q = "Siapa nih yang di rumah suka iseng jailin Google Assistant juga? Coba absen di komentar! 👇🤣"
        else:
            title = "Detik-detik Google Assistant Ditantang 😂💀 #shorts"
            hook = f"\"{clean_t}\""
            synopsis = f"Gokil sih, pas dikasih perintah \"{clean_t}\" reaksinya bener-bener gak terduga! 😂🔥 Tonton sampe selesai ya!"
            disc_q = "Pernah nyobain hal yang sama gak ke Google? Coba komen di bawah! 👇"
        hashtags = ["#shorts", "#lucu", "#ngakak", "#googleassistant", "#viral", "#fyp", "#videolucu", "#trending"]

    elif clean_t:
        # Dialogue detected in casual speech
        first_words = " ".join(clean_t.split()[:7])
        if topic:
            title = f"{topic} — \"{first_words}\" 😂🔥 #shorts"
        else:
            title = f"Gak Nyangka! Pas Dibilang \"{first_words}\"... 😱 #shorts"

        hook = f"\"{clean_t}\""
        synopsis = f"Asli seru banget pas denger perbincangannya: \"{clean_t}\" 🤣 Reaksinya bener-bener di luar dugaan, tonton sampe abis gaes!"
        disc_q = "Menurut kalian gimana momen di video ini? Relate banget gak sih? Komen di bawah ya! 👇🔥"
        hashtags = ["#shorts", "#viral", "#trending", "#fyp", "#foryou", "#videoviral", "#reels", "#ngakak"]

    elif topic:
        title = f"Detik-detik {topic} yang Bikin Melongo 😱🔥 #shorts"
        hook = f"Momen seru {topic} yang wajib kalian tonton!"
        synopsis = f"Gokil banget aksi {topic} di video ini! Visual dan momennya bener-bener bikin kagum, tonton sampe abis ya!"
        disc_q = "Gimana pendapat kalian setelah liat video ini? Kasih nilai 1-10 di kolom komentar ya! 👇✨"
        hashtags = ["#shorts", "#viral", "#trending", "#fyp", "#foryou", "#reels"]

    else:
        title = "Endingnya Bener-bener di Luar Dugaan! 😭🔥 #shorts"
        hook = "Tonton sampe detik terakhir biar gak penasaran!"
        synopsis = "Asli gokil banget momen di video ini! Dari awal sampe akhir bener-bener bikin kaget dan penasaran, wajib tonton sampe abis gaes!"
        disc_q = "Kira-kira siapa yang paham maksud ending video ini? Coba tebak di kolom komentar! 👇🗿"
        hashtags = ["#shorts", "#viral", "#trending", "#fyp", "#foryou", "#videolucu", "#ngakak"]

    video_source_title = topic or title.replace(' #shorts', '')
    caption = build_anti_copyright_caption(synopsis, hook, disc_q, channel_name, video_source_title)

    return {
        "title": title,
        "hook": hook,
        "synopsis": synopsis,
        "discussion_question": disc_q,
        "caption": caption,
        "hashtags": hashtags,
        "transcript": clean_t or "Audio non-vokal / instrumental"
    }

def analyze_local_video(video_path, project_dir, api_key=None, channel_name="Original Creator", custom_title=None):
    if not os.path.exists(video_path):
        print(json.dumps({'error': f"Video file not found: {video_path}"}), file=sys.stderr)
        sys.exit(1)

    os.makedirs(project_dir, exist_ok=True)
    duration = get_video_duration(video_path)

    # 1. Extract audio & detect energy peaks for memes
    wav_path = os.path.join(project_dir, 'audio_temp.wav')
    transcript = ""
    audio_cues = []
    try:
        extract_audio(video_path, wav_path)
        transcript = transcribe_audio_master(wav_path)
        audio_cues = detect_audio_meme_peaks(wav_path, duration)
    except Exception as e:
        print(f"Audio extraction warning: {e}", file=sys.stderr)
        audio_cues = detect_audio_meme_peaks("", duration)
    finally:
        if os.path.exists(wav_path):
            try:
                os.remove(wav_path)
            except Exception:
                pass

    # 2. Generate contextual casual captions
    gemini_key = api_key or os.environ.get('GEMINI_API_KEY')
    result = generate_contextual_caption(transcript, custom_title, duration, gemini_key, channel_name)
    
    # Merge detected audio peaks if Gemini didn't return meme cues
    if not result.get('meme_cues'):
        result['meme_cues'] = audio_cues

    result['duration'] = duration
    result['video_path'] = video_path

    # Save to metadata.json
    meta = {
        'success': True,
        'title': result['title'],
        'duration': duration,
        'channel': channel_name,
        'video_path': video_path,
        'transcript': transcript,
        'caption': result['caption'],
        'hashtags': result['hashtags'],
        'meme_cues': result['meme_cues']
    }

    with open(os.path.join(project_dir, 'metadata.json'), 'w', encoding='utf-8') as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)

    print(json.dumps(result, ensure_ascii=False))
    return result

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Analyze local short video and generate accurate YouTube Shorts captions')
    parser.add_argument('--video-path', required=True, help='Path to uploaded MP4/MOV file')
    parser.add_argument('--project-dir', required=True, help='Destination directory for project metadata')
    parser.add_argument('--api-key', required=False, default=None, help='Gemini API key')
    parser.add_argument('--channel-name', required=False, default='Original Creator', help='Creator / Channel Name')
    parser.add_argument('--custom-title', required=False, default=None, help='User provided title/topic hint')
    args = parser.parse_args()

    analyze_local_video(args.video_path, args.project_dir, args.api_key, args.channel_name, args.custom_title)

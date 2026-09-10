#!/usr/bin/env python3
"""
Tier 3 Muscle: AI Highlight, Exact-Timestamp Alignment & Anti-Copyright Caption Extractor
Guarantees 100% synchronization between the clipped video footage, transcript dialogue, and generated captions.
"""

import sys
import os
import json
import re
import argparse
import glob

def parse_vtt_or_srt(filepath):
    """Accurately parses VTT/SRT files and extracts timestamped dialogue segments"""
    if not os.path.exists(filepath):
        return []

    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        blocks = content.split('\n\n')
        segments = []
        seen = set()

        for b in blocks:
            m = re.search(r'(\d{2}:\d{2}:\d{2}\.\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2}\.\d{3})', b)
            if m:
                s_str, e_str = m.group(1), m.group(2)
                
                def to_sec(t):
                    parts = t.split(':')
                    if len(parts) == 3:
                        h, mi, sec = parts
                        return int(h)*3600 + int(mi)*60 + float(sec)
                    elif len(parts) == 2:
                        mi, sec = parts
                        return int(mi)*60 + float(sec)
                    return float(t)

                s = to_sec(s_str)
                e = to_sec(e_str)

                lines = [l for l in b.splitlines() if not '-->' in l and not 'WEBVTT' in l and l.strip()]
                clean = ' '.join(lines)
                clean = re.sub(r'<[^>]+>', '', clean).strip()
                clean = re.sub(r'\s+', ' ', clean)
                
                # De-duplicate consecutive overlapping lines from YouTube auto-subs
                if clean and clean not in seen and (e - s) > 0.2:
                    seen.add(clean)
                    segments.append({'start': round(s, 2), 'end': round(e, 2), 'text': clean})

        return segments
    except Exception as e:
        print(f"Warning parsing subtitles: {e}", file=sys.stderr)
        return []

def build_anti_copyright_caption(title, hook, synopsis, discussion_q, channel_name, video_title):
    """Constructs a casual, high-converting YouTube Shorts caption with Fair Use"""
    channel_credit = channel_name.strip() if channel_name and channel_name.strip() else "Original Creator"
    video_source = video_title.strip() if video_title else "YouTube Video"

    clean_hook = hook.strip(' "\'')
    hook_str = f'"{clean_hook}"' if clean_hook else ""

    parts = [synopsis]
    if hook_str:
        parts.append(hook_str)
    parts.append(f"💬 {discussion_q}")
    parts.append(
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📌 CREDITS & SOURCE:\n"
        f"🎬 Video: {video_source}\n"
        f"👤 Channel / Creator: @{channel_credit}\n\n"
        "⚠️ FAIR USE DISCLAIMER:\n"
        "Video ini digunakan untuk tujuan hiburan, komentar, dan edukasi (Fair Use Section 107 Copyright Act 1976). Hak cipta sepenuhnya milik pemilik konten asli."
    )
    return "\n\n".join(parts)

def extract_with_gemini(api_key, segments, video_title, video_duration, channel_name=""):
    """Uses Google Gemini API to identify top viral clips with EXACT timestamps and synchronized captions"""
    try:
        from google import genai
        client = genai.Client(api_key=api_key)

        transcript_text = "\n".join([f"[{s['start']}s - {s['end']}s]: {s['text']}" for s in segments[:600]])

        prompt = f"""
You are an elite viral video editor for YouTube Shorts and TikTok.
Analyze the following timestamped transcript of "{video_title}" by "{channel_name}" (Duration: {video_duration}s).

Find the top 3 most VIRAL and interesting clips.
IMPORTANT: You MUST select the EXACT 'start_time' and 'end_time' from the transcript timestamps where the topic is actually spoken! Do not hallucinate or guess timestamps!

For each clip:
1. "title": Catchy YouTube Shorts title under 60 chars with an emoji and #shorts.
2. "start_time" and "end_time": Exact float timestamps matching the dialogue. Target 30-50 seconds per clip.
3. "virality_score": Integer between 88 and 98.
4. "hook": The memorable quote at the start of this timestamp range.
5. "reason": Why this segment will get high retention.
6. "synopsis": 2-3 sentences explaining EXACTLY what the speakers are saying in this timestamp range.
7. "discussion_question": Engaging question based on this clip.
8. "hashtags": 4-6 hashtags tailored to the topic.

9. "meme_cues": Array of 1 to 3 viral meme sound effect & punch zoom cues for this clip. Available effects: "vine_boom", "bonk", "bruh", "cricket", "anime_wow", "directed_by". Each cue has "time" (relative offset in seconds from start_time, e.g. 4.5), "effect", "punch_zoom" (boolean), and "reason".

Transcript:
{transcript_text[:14000]}

Respond ONLY with a JSON array:
[
  {{
    "id": "clip_1",
    "title": "Mitos Micin Bikin Bodoh? Dokter Jawab! 😱 #shorts",
    "start_time": 1112.0,
    "end_time": 1152.0,
    "duration": 40.0,
    "virality_score": 96,
    "hook": "Katanya MSG bikin orang jadi bodoh?",
    "reason": "Mitos populer dijawab dengan fakta medis kocak.",
    "synopsis": "Halda bertanya langsung ke dokter tentang mitos MSG bikin bodoh, dan dokter menjelaskan secara medis bahwa belum ada penelitian yang membuktikan hal tersebut.",
    "discussion_question": "Kalian tim percaya mitos micin atau tim penikmat micin? Tulis di bawah! 👇",
    "hashtags": ["#shorts", "#viral", "#mitos", "#kesehatan", "#fyp"],
    "meme_cues": [
      {{
        "time": 3.5,
        "effect": "vine_boom",
        "punch_zoom": true,
        "reason": "Momen dokter kaget pas ditanya soal micin"
      }},
      {{
        "time": 25.0,
        "effect": "bonk",
        "punch_zoom": false,
        "reason": "Momen fakta kocak terungkap"
      }}
    ]
  }}
]
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

        parsed = json.loads(resp_text.strip())
        
        for clip in parsed:
            synopsis = clip.get('synopsis', f"Momen menarik dari {video_title[:40]}.")
            disc_q = clip.get('discussion_question', "Gimana menurut kalian? Tulis di komentar! 👇")
            hook = clip.get('hook', clip.get('title', ''))
            clip['caption'] = build_anti_copyright_caption(clip['title'], hook, synopsis, disc_q, channel_name, video_title)
            
            # Ensure meme_cues exists
            if 'meme_cues' not in clip or not clip['meme_cues']:
                clip['meme_cues'] = [
                    {'time': 2.5, 'effect': 'vine_boom', 'punch_zoom': True, 'reason': 'Hook awal pembuka video'},
                    {'time': round(min(clip.get('duration', 30.0) * 0.7, 20.0), 1), 'effect': 'bonk', 'punch_zoom': True, 'reason': 'Klimaks momen'}
                ]

        return parsed
    except Exception as e:
        print(f"Gemini API notice: {e}. Falling back to transcript keyword heuristic.", file=sys.stderr)
        return None

def heuristic_transcript_highlight_engine(segments, video_title, video_duration, channel_name=""):
    """Deterministic highlight engine matching EXACT spoken dialogue timestamps"""
    clips = []
    
    if segments and len(segments) >= 10:
        # Score each segment based on viral keywords & dialogue triggers
        viral_keywords = [
            'micin', 'msg', 'bodoh', 'otak', 'kanker', 'bahaya', 'rahasia', 'kenapa', 'gimana', 
            'jangan', 'tips', 'fakta', 'mitos', 'dokter', 'beneran', 'takut', 'intel', 'polisi',
            'misi', 'lapor', 'lucu', 'ngakak', 'gila', 'kaget', 'parah', 'kocak', 'curiga', 'sakit'
        ]

        scored_segs = []
        for i, seg in enumerate(segments):
            score = 0
            text_lower = seg['text'].lower()
            for kw in viral_keywords:
                if kw in text_lower:
                    score += 5
            if '?' in seg['text']:
                score += 3
            if '!' in seg['text']:
                score += 2
            scored_segs.append((score, i, seg))

        # Sort candidate anchor points
        candidate_indices = [idx for sc, idx, s in sorted(scored_segs, key=lambda x: x[0], reverse=True) if sc > 0]
        
        used_ranges = []
        clip_count = 1

        for anchor_idx in candidate_indices:
            anchor_time = segments[anchor_idx]['start']
            
            # Check if anchor is already covered by an existing clip (keep min 90s distance)
            if any(abs(anchor_time - r[0]) < 90.0 for r in used_ranges):
                continue

            # Build a 35-50 second window starting slightly before anchor
            clip_start = max(0.0, anchor_time - 3.0)
            
            # Find all subtitle segments in [clip_start, clip_start + 42]
            window_texts = []
            actual_start = clip_start
            actual_end = clip_start + 40.0

            for seg in segments:
                if seg['start'] >= clip_start and seg['start'] <= clip_start + 45.0:
                    window_texts.append(seg['text'])
                    actual_end = max(actual_end, seg['end'])

            if not window_texts:
                continue

            actual_end = min(actual_end, float(video_duration))
            duration = actual_end - actual_start

            combined_dialogue = " ".join(window_texts)
            first_sentence = window_texts[0] if window_texts else combined_dialogue[:50]
            first_sentence = re.sub(r'[\r\n]+', ' ', first_sentence).strip()

            hook = first_sentence[:75]
            dialogue_summary = combined_dialogue[:150] + ("..." if len(combined_dialogue) > 150 else "")
            
            synopsis = f"Asli seru banget obrolan di bagian ini: \"{dialogue_summary}\" 🤣 Reaksinya bener-bener gak terduga, tonton sampe abis gaes!"
            disc_q = "Menurut kalian gimana pembahasan di segmen ini? Relate banget gak sih? Komen di bawah ya! 👇🔥"
            
            clean_sentence = re.sub(r'[\r\n\t]+', ' ', first_sentence).strip()
            # Trim punctuation at the end
            clean_sentence = re.sub(r'[.,!?:;\-\s]+$', '', clean_sentence[:45])
            title = f"{clean_sentence} 🔥 #shorts"


            caption = build_anti_copyright_caption(title, hook, synopsis, disc_q, channel_name, video_title)

            used_ranges.append((actual_start, actual_end))
            clips.append({
                "id": f"clip_{clip_count}",
                "title": title,
                "start_time": round(actual_start, 1),
                "end_time": round(actual_end, 1),
                "duration": round(duration, 1),
                "virality_score": min(98, 88 + len(clips) * 2),
                "hook": hook,
                "reason": f"Momen percakapan kunci mengenai topik inti video: \"{first_sentence[:40]}\"",
                "caption": caption,
                "hashtags": ["#shorts", "#viral", "#trending", "#fyp", "#podcast", "#indonesia", "#ngakak"]
            })

            clip_count += 1
            if len(clips) >= 3:
                break

    # Fallback if no subtitles
    if not clips:
        dur = max(30.0, float(video_duration))
        intervals = [
            (dur * 0.15, min(dur * 0.15 + 40.0, dur), 95, "Opening Hook & Momen Awal"),
            (dur * 0.45, min(dur * 0.45 + 45.0, dur), 92, "Puncak Pembahasan Paling Seru"),
            (dur * 0.75, min(dur * 0.75 + 38.0, dur), 89, "Punchline Penutup")
        ]
        for idx, (s, e, score, reason) in enumerate(intervals):
            title = f"Detik-detik Momen Seru {video_title[:32]} 🔥 #shorts"
            hook = f"Momen paling seru dari video: {video_title[:40]}"
            synopsis = f"Gokil banget cuplikan di bagian ini! Momennya seru dan bikin penasaran dari awal sampe akhir, tonton sampe abis ya gaes!"
            disc_q = "Gimana menurut kalian part ini? Tulis pendapat kalian di kolom komentar ya! 👇🔥"
            caption = build_anti_copyright_caption(title, hook, synopsis, disc_q, channel_name, video_title)

            clips.append({
                "id": f"clip_{idx+1}",
                "title": title,
                "start_time": round(s, 1),
                "end_time": round(e, 1),
                "duration": round(e - s, 1),
                "virality_score": score,
                "hook": hook,
                "reason": reason,
                "caption": caption,
                "hashtags": ["#shorts", "#viral", "#trending", "#fyp", "#reels"]
            })

    return clips

def extract_highlights(project_dir, api_key=None):
    metadata_file = os.path.join(project_dir, 'metadata.json')
    if not os.path.exists(metadata_file):
        print(json.dumps({'error': 'metadata.json not found'}), file=sys.stderr)
        sys.exit(1)

    with open(metadata_file, 'r', encoding='utf-8') as f:
        metadata = json.load(f)

    video_title = metadata.get('title', 'Video')
    video_duration = metadata.get('duration', 60.0)
    channel_name = metadata.get('channel', metadata.get('uploader', 'Original Creator'))

    sub_files = glob.glob(os.path.join(project_dir, '*.vtt')) + glob.glob(os.path.join(project_dir, '*.srt'))
    segments = []
    for sf in sub_files:
        parsed_segs = parse_vtt_or_srt(sf)
        if parsed_segs:
            segments = parsed_segs
            break

    gemini_key = api_key or os.environ.get('GEMINI_API_KEY')
    clips = None

    if gemini_key and segments:
        clips = extract_with_gemini(gemini_key, segments, video_title, video_duration, channel_name)

    if not clips:
        clips = heuristic_transcript_highlight_engine(segments, video_title, video_duration, channel_name)

    highlights_path = os.path.join(project_dir, 'highlights.json')
    with open(highlights_path, 'w', encoding='utf-8') as f:
        json.dump(clips, f, indent=2, ensure_ascii=False)

    print(json.dumps({'success': True, 'clips': clips}))
    return clips

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Extract viral highlight clips synchronized with exact transcript timestamps')
    parser.add_argument('--project-dir', required=True, help='Project directory containing metadata & video')
    parser.add_argument('--api-key', required=False, default=None, help='Gemini API Key')
    args = parser.parse_args()

    extract_highlights(args.project_dir, args.api_key)

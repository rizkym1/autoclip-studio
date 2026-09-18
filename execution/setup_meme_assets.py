#!/usr/bin/env python3
"""
Tier 3 Muscle: Expanded Meme & SFX Soundboard Asset Setup
Provides 14 iconic viral sound effects (Vine Boom, Metal Pipe, Taco Bell, Bruh, Bonk, 
Cricket, Anime Wow, Directed By, Emotional Damage, Windows Error, Fart Reverb, Huh?, Run, Laugh Wheeze)
locally in storage/app/public/memes/sfx/ with zero external runtime dependencies.
"""

import os
import sys
import math
import wave
import struct
import json

SAMPLE_RATE = 44100

def get_sfx_dir(base_dir=None):
    if base_dir:
        target = os.path.join(base_dir, 'storage', 'app', 'public', 'memes', 'sfx')
    else:
        curr = os.path.dirname(os.path.abspath(__file__))
        target = os.path.abspath(os.path.join(curr, '..', 'storage', 'app', 'public', 'memes', 'sfx'))
    os.makedirs(target, exist_ok=True)
    return target

def write_wav(filepath, samples, sample_rate=SAMPLE_RATE):
    """Writes float samples (-1.0 to 1.0) into a standard 16-bit PCM WAV file"""
    with wave.open(filepath, 'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        packed = bytearray()
        for s in samples:
            clamped = max(-1.0, min(1.0, s))
            val = int(clamped * 32767.0)
            packed.extend(struct.pack('<h', val))
        wf.writeframes(packed)

# 1. Vine Boom
def synthesize_vine_boom(filepath):
    duration = 1.8
    total_samples = int(SAMPLE_RATE * duration)
    samples = []
    import random
    rng = random.Random(42)

    for i in range(total_samples):
        t = i / SAMPLE_RATE
        transient = math.sin(2 * math.pi * 120 * (1.0 - t * 5.0)) if t < 0.2 else 0
        noise = (rng.random() * 2 - 1) * math.exp(-t * 25)
        freq = 55.0 * math.exp(-t * 0.8)
        sub = math.sin(2 * math.pi * freq * t)
        sat = 0.4 * math.sin(4 * math.pi * freq * t)
        envelope = math.exp(-t * 1.6)
        val = (transient * 0.5 + noise * 0.4 + sub * 0.85 + sat * 0.3) * envelope
        val = math.tanh(val * 1.5)
        samples.append(val)

    write_wav(filepath, samples)

# 2. Bonk
def synthesize_bonk(filepath):
    duration = 0.45
    total_samples = int(SAMPLE_RATE * duration)
    samples = []

    for i in range(total_samples):
        t = i / SAMPLE_RATE
        freq = 220 + 660 * math.exp(-t * 30)
        env = math.exp(-t * 12)
        tone1 = math.sin(2 * math.pi * freq * t)
        tone2 = 0.3 * math.sin(2 * math.pi * (freq * 2.4) * t)
        tone3 = 0.2 * math.sin(2 * math.pi * (freq * 4.1) * t)
        val = (tone1 + tone2 + tone3) * env
        samples.append(val)

    write_wav(filepath, samples)

# 3. Bruh
def synthesize_bruh(filepath):
    duration = 1.1
    total_samples = int(SAMPLE_RATE * duration)
    samples = []

    for i in range(total_samples):
        t = i / SAMPLE_RATE
        pitch = 140.0 * math.exp(-t * 0.6)
        env = math.sin(math.pi * (t / duration) ** 0.5) if t < duration else 0
        f0 = math.sin(2 * math.pi * pitch * t)
        f1 = 0.6 * math.sin(2 * math.pi * (pitch * 3.2) * t)
        f2 = 0.4 * math.sin(2 * math.pi * (pitch * 6.5) * t)
        val = (f0 + f1 + f2) * env * 0.85
        samples.append(val)

    write_wav(filepath, samples)

# 4. Cricket
def synthesize_cricket(filepath):
    duration = 2.4
    total_samples = int(SAMPLE_RATE * duration)
    samples = [0.0] * total_samples
    chirp_times = [0.2, 0.32, 0.44, 1.1, 1.22, 1.34, 1.8, 1.92]
    chirp_dur = 0.06
    pulse_samples = int(chirp_dur * SAMPLE_RATE)

    for start_t in chirp_times:
        start_idx = int(start_t * SAMPLE_RATE)
        for j in range(pulse_samples):
            idx = start_idx + j
            if idx >= total_samples:
                break
            t_pulse = j / SAMPLE_RATE
            osc = math.sin(2 * math.pi * 4300 * t_pulse)
            env = math.sin(math.pi * (t_pulse / chirp_dur))
            samples[idx] += osc * env * 0.6

    write_wav(filepath, samples)

# 5. Anime Wow
def synthesize_anime_wow(filepath):
    duration = 1.9
    total_samples = int(SAMPLE_RATE * duration)
    samples = [0.0] * total_samples
    notes = [523.25, 659.25, 783.99, 1046.50, 1318.51, 1567.98]
    stagger = 0.08

    for note_idx, freq in enumerate(notes):
        start_t = note_idx * stagger
        start_idx = int(start_t * SAMPLE_RATE)
        note_dur = duration - start_t
        for j in range(int(note_dur * SAMPLE_RATE)):
            idx = start_idx + j
            if idx >= total_samples:
                break
            t_note = j / SAMPLE_RATE
            env = math.exp(-t_note * 2.8)
            tone = math.sin(2 * math.pi * freq * t_note)
            shimmer = 0.3 * math.sin(2 * math.pi * (freq * 2) * t_note)
            samples[idx] += (tone + shimmer) * env * 0.28

    write_wav(filepath, samples)

# 6. Directed By Weide Outro
def synthesize_directed_by(filepath):
    duration = 3.2
    total_samples = int(SAMPLE_RATE * duration)
    samples = [0.0] * total_samples
    melody = [
        (0.0, 0.22, 466.16),
        (0.25, 0.22, 523.25),
        (0.50, 0.22, 587.33),
        (0.75, 0.35, 698.46),
        (1.15, 0.25, 587.33),
        (1.45, 0.25, 523.25),
        (1.75, 0.50, 466.16),
    ]

    for start_t, dur, freq in melody:
        start_idx = int(start_t * SAMPLE_RATE)
        for j in range(int(dur * SAMPLE_RATE)):
            idx = start_idx + j
            if idx >= total_samples:
                break
            t_note = j / SAMPLE_RATE
            env = math.sin(math.pi * (t_note / dur))
            clarinet = (
                math.sin(2 * math.pi * freq * t_note)
                + 0.5 * math.sin(2 * math.pi * 3 * freq * t_note)
                + 0.2 * math.sin(2 * math.pi * 5 * freq * t_note)
            )
            samples[idx] += clarinet * env * 0.35

    write_wav(filepath, samples)

# 7. Metal Pipe Falling (Iconic Clang & Hollow Metallic Reverb)
def synthesize_metal_pipe(filepath):
    duration = 2.2
    total_samples = int(SAMPLE_RATE * duration)
    samples = []
    import random
    rng = random.Random(99)

    inharmonic_freqs = [820, 1140, 1680, 2250, 3100, 4350]
    for i in range(total_samples):
        t = i / SAMPLE_RATE
        # Heavy chaotic transient at t < 0.1
        clang_noise = (rng.random() * 2 - 1) * math.exp(-t * 18) if t < 0.3 else 0
        
        # Inharmonic resonant metal body
        body = 0.0
        for idx, freq in enumerate(inharmonic_freqs):
            decay = 3.0 + idx * 0.8
            body += math.sin(2 * math.pi * freq * t + math.sin(t * 12)) * math.exp(-t * decay) * 0.2
        
        # Hollow ringing pipe tail
        hollow = math.sin(2 * math.pi * 480 * t) * math.exp(-t * 1.5) * 0.35
        hollow2 = math.sin(2 * math.pi * 720 * t) * math.exp(-t * 2.0) * 0.25

        val = (clang_noise * 0.5 + body + hollow + hollow2)
        val = math.tanh(val * 1.4)
        samples.append(val)

    write_wav(filepath, samples)

# 8. Taco Bell Bong (Deep Bronze Gong Bell)
def synthesize_taco_bell(filepath):
    duration = 2.4
    total_samples = int(SAMPLE_RATE * duration)
    samples = []

    bell_freqs = [293.66, 587.33, 880.0, 1174.66, 1760.0]
    for i in range(total_samples):
        t = i / SAMPLE_RATE
        val = 0.0
        for idx, freq in enumerate(bell_freqs):
            decay = 1.2 + idx * 0.6
            amp = 0.45 / (idx + 1)
            val += math.sin(2 * math.pi * freq * t) * math.exp(-t * decay) * amp
        
        # Shimmering bronze overtone modulation
        shimmer = math.sin(2 * math.pi * 2350 * t) * math.exp(-t * 4.0) * 0.15
        strike = math.sin(2 * math.pi * 90 * (1.0 - t * 8.0)) * math.exp(-t * 20) if t < 0.15 else 0
        
        tot = (val + shimmer + strike)
        samples.append(math.tanh(tot * 1.3))

    write_wav(filepath, samples)

# 9. Emotional Damage (Heavy Bass Hit & Dramatic Vocal Accent)
def synthesize_emotional_damage(filepath):
    duration = 1.4
    total_samples = int(SAMPLE_RATE * duration)
    samples = []

    for i in range(total_samples):
        t = i / SAMPLE_RATE
        # Deep dramatic boom
        bass = math.sin(2 * math.pi * (70 * math.exp(-t * 1.2)) * t) * math.exp(-t * 2.0)
        # Metallic string orchestra stab simulation
        orchestra = (
            math.sin(2 * math.pi * 330 * t) +
            0.7 * math.sin(2 * math.pi * 392 * t) +
            0.5 * math.sin(2 * math.pi * 493.88 * t)
        ) * math.exp(-t * 3.5) * 0.4
        
        val = (bass * 0.7 + orchestra)
        samples.append(math.tanh(val * 1.5))

    write_wav(filepath, samples)

# 10. Windows Error Sound (Classic Chord Exclamation)
def synthesize_windows_error(filepath):
    duration = 0.85
    total_samples = int(SAMPLE_RATE * duration)
    samples = [0.0] * total_samples

    # Two-tone exclamation: Low Ding then High Chord Ding
    tones = [
        (0.0, 0.15, [440.0]),             # A4 intro
        (0.12, 0.65, [523.25, 659.25, 783.99]) # C-E-G major triad chord
    ]

    for start_t, dur, chord in tones:
        s_idx = int(start_t * SAMPLE_RATE)
        for j in range(int(dur * SAMPLE_RATE)):
            idx = s_idx + j
            if idx >= total_samples:
                break
            t_loc = j / SAMPLE_RATE
            env = math.exp(-t_loc * 3.8)
            tone_sum = sum(math.sin(2 * math.pi * f * t_loc) for f in chord) * (0.35 / len(chord))
            samples[idx] += tone_sum * env

    write_wav(filepath, samples)

# 11. Fart with Reverb (Shitpost Bass Reverb)
def synthesize_fart_reverb(filepath):
    duration = 1.9
    total_samples = int(SAMPLE_RATE * duration)
    samples = []
    import random
    rng = random.Random(7)

    for i in range(total_samples):
        t = i / SAMPLE_RATE
        # Buzzy squelch transient at t < 0.35
        if t < 0.35:
            buzz_f = 75 + 40 * math.sin(2 * math.pi * 30 * t)
            squelch = math.copysign(1.0, math.sin(2 * math.pi * buzz_f * t)) * (1.0 - t / 0.35)
        else:
            squelch = 0.0

        # Massive boom reverb tail
        reverb_tail = (
            math.sin(2 * math.pi * 45 * t) * 0.5 +
            math.sin(2 * math.pi * 68 * t) * 0.3 +
            (rng.random() * 2 - 1) * 0.15
        ) * math.exp(-max(0, t - 0.25) * 1.8)

        val = (squelch * 0.6 + reverb_tail * 0.75)
        samples.append(math.tanh(val * 1.6))

    write_wav(filepath, samples)

# 12. Huh? / What? Cat Sound (Questioning vocal inflection)
def synthesize_huh(filepath):
    duration = 0.75
    total_samples = int(SAMPLE_RATE * duration)
    samples = []

    for i in range(total_samples):
        t = i / SAMPLE_RATE
        # Pitch starts around 300Hz, dips to 220Hz, then rises to 380Hz (curious scoop)
        pitch = 300.0 - 80.0 * math.sin(math.pi * t / duration) + 100.0 * (t / duration) ** 2
        env = math.sin(math.pi * (t / duration)) ** 0.8
        f0 = math.sin(2 * math.pi * pitch * t)
        f1 = 0.4 * math.sin(2 * math.pi * pitch * 2.2 * t)
        val = (f0 + f1) * env * 0.8
        samples.append(val)

    write_wav(filepath, samples)

# 13. Run! (Urgent synth pulse intro)
def synthesize_run(filepath):
    duration = 1.7
    total_samples = int(SAMPLE_RATE * duration)
    samples = [0.0] * total_samples

    pulses = [0.0, 0.25, 0.50, 0.75, 1.05]
    for p_t in pulses:
        s_idx = int(p_t * SAMPLE_RATE)
        for j in range(int(0.2 * SAMPLE_RATE)):
            idx = s_idx + j
            if idx >= total_samples:
                break
            t_loc = j / SAMPLE_RATE
            bass = math.sin(2 * math.pi * 65 * t_loc) * math.exp(-t_loc * 12)
            noise = math.sin(2 * math.pi * 180 * t_loc) * math.exp(-t_loc * 15) * 0.4
            samples[idx] += (bass + noise) * 0.8

    write_wav(filepath, samples)

# 14. Laugh Wheeze (Staccato breathy giggle)
def synthesize_laugh_wheeze(filepath):
    duration = 1.8
    total_samples = int(SAMPLE_RATE * duration)
    samples = [0.0] * total_samples
    ha_times = [0.1, 0.26, 0.42, 0.58, 0.74, 1.0, 1.3]

    for h_t in ha_times:
        s_idx = int(h_t * SAMPLE_RATE)
        for j in range(int(0.12 * SAMPLE_RATE)):
            idx = s_idx + j
            if idx >= total_samples:
                break
            t_loc = j / SAMPLE_RATE
            freq = 420.0 + 80.0 * math.sin(t_loc * 20)
            env = math.sin(math.pi * (t_loc / 0.12))
            samples[idx] += math.sin(2 * math.pi * freq * t_loc) * env * 0.45

    write_wav(filepath, samples)

ASSET_REGISTRY = {
    'vine_boom': {
        'name': 'Vine Boom (Shock & Bass Thud)',
        'filename': 'vine_boom.wav',
        'generator': synthesize_vine_boom,
        'tag': 'punchline',
        'duration': 1.8
    },
    'metal_pipe': {
        'name': 'Metal Pipe Falling (Clang)',
        'filename': 'metal_pipe.wav',
        'generator': synthesize_metal_pipe,
        'tag': 'blunder',
        'duration': 2.2
    },
    'taco_bell': {
        'name': 'Taco Bell Bong (Bronze Bell)',
        'filename': 'taco_bell.wav',
        'generator': synthesize_taco_bell,
        'tag': 'fail',
        'duration': 2.4
    },
    'bonk': {
        'name': 'Cartoon Bonk',
        'filename': 'bonk.wav',
        'generator': synthesize_bonk,
        'tag': 'fail',
        'duration': 0.45
    },
    'bruh': {
        'name': 'Deep Bruh Sound',
        'filename': 'bruh.wav',
        'generator': synthesize_bruh,
        'tag': 'blunder',
        'duration': 1.1
    },
    'emotional_damage': {
        'name': 'Emotional Damage Stab',
        'filename': 'emotional_damage.wav',
        'generator': synthesize_emotional_damage,
        'tag': 'blunder',
        'duration': 1.4
    },
    'windows_error': {
        'name': 'Windows Error Ding',
        'filename': 'windows_error.wav',
        'generator': synthesize_windows_error,
        'tag': 'awkward',
        'duration': 0.85
    },
    'fart_reverb': {
        'name': 'Fart With Reverb',
        'filename': 'fart_reverb.wav',
        'generator': synthesize_fart_reverb,
        'tag': 'shitpost',
        'duration': 1.9
    },
    'huh': {
        'name': 'Huh? Question Cat',
        'filename': 'huh.wav',
        'generator': synthesize_huh,
        'tag': 'awkward',
        'duration': 0.75
    },
    'run': {
        'name': 'Run! Panic Bass Stabs',
        'filename': 'run.wav',
        'generator': synthesize_run,
        'tag': 'hype',
        'duration': 1.7
    },
    'laugh_wheeze': {
        'name': 'Wheeze Laugh',
        'filename': 'laugh_wheeze.wav',
        'generator': synthesize_laugh_wheeze,
        'tag': 'funny',
        'duration': 1.8
    },
    'cricket': {
        'name': 'Awkward Silence Cricket',
        'filename': 'cricket.wav',
        'generator': synthesize_cricket,
        'tag': 'awkward',
        'duration': 2.4
    },
    'anime_wow': {
        'name': 'Anime Wow & Chime',
        'filename': 'anime_wow.wav',
        'generator': synthesize_anime_wow,
        'tag': 'epic',
        'duration': 1.9
    },
    'directed_by': {
        'name': 'Directed by Weide Outro',
        'filename': 'directed_by.wav',
        'generator': synthesize_directed_by,
        'tag': 'outro',
        'duration': 3.2
    }
}

def setup_assets(force=False, base_dir=None):
    sfx_dir = get_sfx_dir(base_dir)
    results = {}
    
    for key, info in ASSET_REGISTRY.items():
        dest = os.path.join(sfx_dir, info['filename'])
        if not os.path.exists(dest) or force:
            info['generator'](dest)
            results[key] = {'status': 'generated', 'path': dest}
        else:
            results[key] = {'status': 'exists', 'path': dest}

    manifest_path = os.path.join(sfx_dir, 'manifest.json')
    manifest_data = {
        key: {
            'name': val['name'],
            'filename': val['filename'],
            'tag': val['tag'],
            'duration': val['duration'],
            'url': f"/storage/memes/sfx/{val['filename']}"
        }
        for key, val in ASSET_REGISTRY.items()
    }
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest_data, f, indent=2)

    return manifest_data

if __name__ == '__main__':
    manifest = setup_assets(force=True)
    print(json.dumps({'success': True, 'count': len(manifest), 'manifest': manifest}, indent=2))

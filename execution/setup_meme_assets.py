#!/usr/bin/env python3
"""
Tier 3 Muscle: Meme & SFX Soundboard Asset Setup
Ensures all viral sound effects (Vine Boom, Bruh, Bonk, Cricket, Anime Wow, Directed By)
are locally available in storage/app/public/memes/sfx/ with zero external runtime dependencies.
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
        # Default relative to execution script
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

def synthesize_vine_boom(filepath):
    """Generates an earth-shaking sub-bass impact boom (Vine Boom vibe)"""
    duration = 1.8
    total_samples = int(SAMPLE_RATE * duration)
    samples = []
    
    import random
    rng = random.Random(42)

    for i in range(total_samples):
        t = i / SAMPLE_RATE
        
        # Transient punch at t=0
        transient = math.sin(2 * math.pi * 120 * (1.0 - t * 5.0)) if t < 0.2 else 0
        noise = (rng.random() * 2 - 1) * math.exp(-t * 25)
        
        # Sub-bass rumble (55Hz -> 38Hz)
        freq = 55.0 * math.exp(-t * 0.8)
        sub = math.sin(2 * math.pi * freq * t)
        
        # Second harmonic saturation
        sat = 0.4 * math.sin(4 * math.pi * freq * t)
        
        # Exponential volume envelope
        envelope = math.exp(-t * 1.6)
        
        val = (transient * 0.5 + noise * 0.4 + sub * 0.85 + sat * 0.3) * envelope
        val = math.tanh(val * 1.5)
        samples.append(val)

    write_wav(filepath, samples)

def synthesize_bonk(filepath):
    """Generates a cartoon metallic/wooden bonk impact"""
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

def synthesize_bruh(filepath):
    """Generates an awkward low-tone vocal/resonance ('bruh' drop)"""
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

def synthesize_cricket(filepath):
    """Generates an awkward silence cricket chirp"""
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

def synthesize_anime_wow(filepath):
    """Generates a sparkling, magical fairy chime / WOW reveal sound"""
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

def synthesize_directed_by(filepath):
    """Generates a bouncy comedic outro fanfare (Directed by Weide comedic motif)"""
    duration = 3.2
    total_samples = int(SAMPLE_RATE * duration)
    samples = [0.0] * total_samples

    melody = [
        (0.0, 0.22, 466.16),  # Bb4
        (0.25, 0.22, 523.25), # C5
        (0.50, 0.22, 587.33), # D5
        (0.75, 0.35, 698.46), # F5
        (1.15, 0.25, 587.33), # D5
        (1.45, 0.25, 523.25), # C5
        (1.75, 0.50, 466.16), # Bb4
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

ASSET_REGISTRY = {
    'vine_boom': {
        'name': 'Vine Boom (Shock & Bass Thud)',
        'filename': 'vine_boom.wav',
        'generator': synthesize_vine_boom,
        'tag': 'punchline',
        'duration': 1.8
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

    # Save asset manifest for API and UI consumption
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
    manifest = setup_assets()
    print(json.dumps({'success': True, 'count': len(manifest), 'manifest': manifest}, indent=2))

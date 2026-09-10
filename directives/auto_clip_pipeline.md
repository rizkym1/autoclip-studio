# SOP: AI Video Auto-Clip & YouTube Shorts Pipeline

Dokumen ini adalah Prosedur Standar Operasional (SOP) permanen untuk sistem **AutoClip Studio** — memproses video mentah panjang menjadi klip video pendek viral berformat vertikal (9:16) yang **100% tersinkronisasi dengan dialog ucapan** dan mematuhi aturan **Anti-Copyright & Fair Use YouTube Shorts**.

---

## 1. Prinsip Utama (Core Directives)

> [!IMPORTANT]
> ### 1. Sinkronisasi Mutlak Antara Ucapan, Judul & Klip Video (Zero-Mismatch Rule)
> * Setiap video yang diproses **WAJIB** mengekstrak transkrip ucapan (subtitle `.vtt` / `.srt`) dengan timestamp milidetik.
> * Penentuan detik potong (`start_time` dan `end_time`) **HARUS TEPAT** pada detik saat pembicara mengucapkan topik/kalimat tersebut.
> * Judul dan sinopsis caption **HARUS MENCERMINKAN SECARA NYATA** dialog yang terucap di rentang detik klip tersebut (dilarang menggunakan persentase potongan acak).

> [!IMPORTANT]
> ### 2. Standar Anti-Copyright & Fair Use (YouTube Shorts Kit)
> Setiap klip yang dihasilkan **WAJIB** menyertakan paket metadata lengkap:
> 1. **Judul Catchy (< 60 karakter)** dengan emoji dan tag `#shorts`.
> 2. **Sinopsis Naratif Kontekstual** yang menjelaskan inti percakapan di klip tersebut.
> 3. **Pertanyaan Diskusi (CTA)** untuk memicu debat & komentar penonton.
> 4. **Atribusi Lengkap Creator**:
>    - `📌 CREDITS & SOURCE:`
>    - `🎬 Video: [Judul Video Lengkap]`
>    - `👤 Channel: @[Nama Channel Asli]`
> 5. **Fair Use Disclaimer Resmi** (Section 107 of Copyright Act 1976).
> 6. **Hashtags SEO Relevan** sesuai topik spesifik video.

---

## 2. Alur Eksekusi 3-Tier Tools (The Muscle)

### Tahap 1: Video Download & Transcript Stream
* **Script**: `execution/yt_downloader.py`
* **Input**: URL Video, Output Path
* **Ketentuan**:
  - Mengunduh stream video MP4 terbaik (maks 1080p).
  - Mengunduh otomatis subtitle/transkrip kata-per-kata (`--write-auto-sub --sub-langs "id,id-orig,en,en-orig" --sub-format vtt`).
  - Menyimpan `metadata.json` lengkap dengan nama channel, judul asli, dan durasi.

### Tahap 2: Exact Timestamp Dialogue Matching & AI Strategy
* **Script**: `execution/ai_highlight_extractor.py`
* **Input**: Direktori project (`metadata.json` dan file `.vtt`)
* **Engine**:
  1. Parse milidetik file `.vtt` untuk memetakan seluruh dialog ucapan.
  2. Temukan momen puncak percakapan (pertanyaan menarik, punchline komedi, tips rahasia, atau perdebatan seru).
  3. Kunci rentang `start_time` dan `end_time` (ideal 30–50 detik) tepat pada awal kalimat pembicara hingga akhir punchline.
  4. Susun Judul, Sinopsis, Kredit Channel, Fair Use Disclaimer, dan Tagar SEO.
* **Output**: `highlights.json` berisi klip yang 100% sinkron.

### Tahap 3: Fast Multi-Core FFmpeg Smart Renderer
* **Script**: `execution/video_cutter.py`
* **Input**: Input Video, `start_time`, `end_time`, `aspect_ratio`, Output Path
* **Engine**:
  - Multi-threaded CPU rendering (`-threads 0` dan `-preset veryfast`).
  - Format `9:16`: Canvas vertikal dengan background blur halus (*downscaled fast-blur*) + video utama di tengah.
  - Timeout protection: Backend PHP disetel `set_time_limit(300)` untuk mencegah eksekusi terputus.

---

## 3. Standar Antarmuka (21st.dev Craft UI)
* Mengadopsi palet Pitch Dark (`#09090b`), card layer `#121215`, dan *hairline border* (`border-zinc-800`).
* Tipografi: **Geist** & **Geist Mono** untuk kejelasan angka timestamp dan teks.
* Dilengkapi modul **YouTube Shorts Kit** dengan tombol **`📋 Copy All for Shorts`** (1-Click Copy ke YouTube Studio).

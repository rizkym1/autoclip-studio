import React, { useState, useEffect, useRef } from 'react';
import { 
    Sparkles, 
    Video, 
    Scissors, 
    Download, 
    Play, 
    Pause, 
    RefreshCw, 
    Flame, 
    Clock, 
    CheckCircle2, 
    AlertCircle, 
    Layers, 
    Smartphone, 
    Monitor, 
    Square, 
    ExternalLink, 
    Trash2, 
    Zap, 
    Sliders, 
    TrendingUp, 
    Film, 
    ArrowRight, 
    CornerDownLeft, 
    Check, 
    ChevronDown, 
    ChevronUp, 
    Copy, 
    Share2, 
    Hash, 
    FileText,
    ShieldCheck,
    UploadCloud,
    FileVideo,
    Mic,
    X,
    Radio
} from 'lucide-react';
import confetti from 'canvas-confetti';

export default function Dashboard({ recentProjects = [], hasApiKey = false }) {
    const [inputMode, setInputMode] = useState('url'); // 'url' | 'upload'
    const [videoUrl, setVideoUrl] = useState('');
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [uploadFile, setUploadFile] = useState(null);
    const [uploadChannel, setUploadChannel] = useState('');
    const [uploadTitleHint, setUploadTitleHint] = useState('');
    const [isUploading, setIsUploading] = useState(false);
    const [uploadProgress, setUploadProgress] = useState(0);
    const [isDragging, setIsDragging] = useState(false);
    const fileInputRef = useRef(null);

    const [currentProject, setCurrentProject] = useState(recentProjects && recentProjects.length > 0 ? recentProjects[0] : null);
    const [projects, setProjects] = useState(recentProjects || []);
    const [activeTab, setActiveTab] = useState('highlights'); // 'highlights' | 'manual' | 'rendered'
    const [toast, setToast] = useState(null);
    const [copiedStates, setCopiedStates] = useState({});
    const [expandedShortsKit, setExpandedShortsKit] = useState({});
    
    // Manual Clipper States
    const [customTitle, setCustomTitle] = useState('Custom Highlight');
    const [startTime, setStartTime] = useState(0);
    const [endTime, setEndTime] = useState(30);
    const [aspectRatio, setAspectRatio] = useState('9:16');
    const [isRenderingCustom, setIsRenderingCustom] = useState(false);
    const [renderingClipIds, setRenderingClipIds] = useState(new Set());
    const [renderingMemeClipIds, setRenderingMemeClipIds] = useState(new Set());
    const [clipMemeIntensity, setClipMemeIntensity] = useState({}); // { [clipId]: 'santai' | 'rame' | 'barbar' }

    // Video Player Ref
    const videoRef = useRef(null);
    const [isPlaying, setIsPlaying] = useState(false);
    const [currentTime, setCurrentTime] = useState(0);

    const showToast = (message, type = 'info') => {
        setToast({ message, type });
        setTimeout(() => setToast(null), 4000);
    };

    // Safe Hashtags Parser
    const parseHashtags = (tags) => {
        if (Array.isArray(tags)) return tags;
        if (typeof tags === 'string') {
            try {
                const parsed = JSON.parse(tags);
                if (Array.isArray(parsed)) return parsed;
            } catch (e) {
                return tags.split(/[\s,]+/).filter(Boolean);
            }
        }
        return ['#shorts', '#viral', '#trending', '#fyp'];
    };

    // Copy to Clipboard Helper
    const copyToClipboard = (text, key, label) => {
        try {
            if (navigator && navigator.clipboard && navigator.clipboard.writeText) {
                navigator.clipboard.writeText(text);
            } else {
                const textarea = document.createElement('textarea');
                textarea.value = text;
                document.body.appendChild(textarea);
                textarea.select();
                document.execCommand('copy');
                document.body.removeChild(textarea);
            }
            setCopiedStates(prev => ({ ...prev, [key]: true }));
            showToast(`📋 ${label} disalin ke clipboard!`, 'success');
            setTimeout(() => {
                setCopiedStates(prev => ({ ...prev, [key]: false }));
            }, 2500);
        } catch (e) {
            console.error('Clipboard copy error:', e);
            showToast('Gagal menyalin ke clipboard', 'error');
        }
    };

    const toggleShortsKit = (clipId) => {
        setExpandedShortsKit(prev => ({ ...prev, [clipId]: !prev[clipId] }));
    };

    // Polling effect for active project processing
    useEffect(() => {
        if (!currentProject) return;

        let interval = null;
        const status = (currentProject.status || '').toLowerCase();
        if (status === 'pending' || status === 'downloading' || status === 'analyzing') {
            interval = setInterval(async () => {
                try {
                    const res = await fetch(`/api/projects/${currentProject.id}`);
                    const data = await res.json();
                    if (data.success && data.project) {
                        setCurrentProject(data.project);
                        setProjects(prev => prev.map(p => p.id === data.project.id ? data.project : p));
                        
                        if (data.project.status === 'ready') {
                            showToast('Highlights detected successfully', 'success');
                            confetti({
                                particleCount: 50,
                                spread: 60,
                                origin: { y: 0.6 }
                            });
                        }
                    }
                } catch (err) {
                    console.error('Polling error:', err);
                }
            }, 2500);
        }

        return () => {
            if (interval) clearInterval(interval);
        };
    }, [currentProject?.id, currentProject?.status]);

    // Handle URL Submit
    const handleStartAutoClip = async (e) => {
        e?.preventDefault();
        if (!videoUrl || isSubmitting) return;

        setIsSubmitting(true);
        showToast('Processing video stream & extracting transcript...', 'info');
        try {
            const res = await fetch('/api/projects', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                },
                body: JSON.stringify({ video_url: videoUrl })
            });

            let data;
            try {
                data = await res.json();
            } catch (e) {
                data = { success: false, error: 'Invalid server response' };
            }

            if (data.success && data.project) {
                setCurrentProject(data.project);
                setProjects(prev => [data.project, ...prev.filter(p => p.id !== data.project.id)]);
                setVideoUrl('');
                setActiveTab('highlights');
                showToast('Video added to processing pipeline', 'success');
            } else {
                showToast(data.error || 'Failed to process video', 'error');
            }
        } catch (err) {
            console.error('Submit error:', err);
            showToast('Network error while processing link', 'error');
        } finally {
            setIsSubmitting(false);
        }
    };

    // File validation and selection
    const handleFileChange = (file) => {
        if (!file) return;
        const validExtensions = ['mp4', 'mov', 'webm', 'mkv', 'avi'];
        const ext = file.name.split('.').pop()?.toLowerCase();
        if (!ext || !validExtensions.includes(ext)) {
            showToast('Format file tidak didukung. Harap upload video MP4, MOV, WebM, atau MKV.', 'error');
            return;
        }

        if (file.size > 200 * 1024 * 1024) {
            showToast('Ukuran video terlalu besar (maksimal 200MB untuk video pendek).', 'error');
            return;
        }

        setUploadFile(file);
        showToast(`File "${file.name}" dipilih (${(file.size / (1024 * 1024)).toFixed(1)} MB)`, 'info');
    };

    // Drag and drop events
    const handleDragOver = (e) => {
        e.preventDefault();
        setIsDragging(true);
    };

    const handleDragLeave = (e) => {
        e.preventDefault();
        setIsDragging(false);
    };

    const handleDrop = (e) => {
        e.preventDefault();
        setIsDragging(false);
        if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
            handleFileChange(e.dataTransfer.files[0]);
        }
    };

    // Handle Local Video File Upload & STT Analysis
    const handleUploadVideo = async (e) => {
        e?.preventDefault();
        if (!uploadFile || isUploading) return;

        setIsUploading(true);
        setUploadProgress(15);
        showToast('Mengunggah video & mengekstrak transkrip ucapan...', 'info');

        const formData = new FormData();
        formData.append('video_file', uploadFile);
        if (uploadChannel.trim()) {
            formData.append('channel_name', uploadChannel.trim());
        }
        if (uploadTitleHint.trim()) {
            formData.append('custom_title', uploadTitleHint.trim());
        }

        try {
            const xhr = new XMLHttpRequest();
            xhr.open('POST', '/api/upload-video', true);
            xhr.setRequestHeader('Accept', 'application/json');

            xhr.upload.onprogress = (event) => {
                if (event.lengthComputable) {
                    const percent = Math.min(85, Math.round((event.loaded / event.total) * 60));
                    setUploadProgress(percent);
                }
            };

            xhr.onload = () => {
                setIsUploading(false);
                setUploadProgress(100);
                try {
                    let text = xhr.responseText || '';
                    // Strip any PHP warnings/HTML tags if present before JSON
                    const jsonStart = text.indexOf('{');
                    const jsonEnd = text.lastIndexOf('}');
                    if (jsonStart !== -1 && jsonEnd !== -1 && jsonEnd >= jsonStart) {
                        text = text.substring(jsonStart, jsonEnd + 1);
                    }
                    const data = JSON.parse(text);
                    if (xhr.status >= 200 && xhr.status < 300 && data.success && data.project) {
                        setCurrentProject(data.project);
                        setProjects(prev => [data.project, ...prev.filter(p => p.id !== data.project.id)]);
                        setUploadFile(null);
                        setActiveTab('highlights');
                        showToast('Transkripsi & paket caption YouTube Shorts selesai!', 'success');
                        confetti({
                            particleCount: 60,
                            spread: 70,
                            origin: { y: 0.6 }
                        });
                    } else {
                        const errMsg = data.message || data.error || (data.errors ? Object.values(data.errors).flat().join(', ') : 'Gagal menganalisis video lokal.');
                        showToast(errMsg, 'error');
                    }
                } catch (err) {
                    console.error('Upload parse error. Raw:', xhr.responseText);
                    showToast('Gagal memproses file upload (status ' + xhr.status + '). Coba file video lainnya.', 'error');
                }
            };

            xhr.onerror = () => {
                setIsUploading(false);
                showToast('Koneksi terputus saat mengunggah video.', 'error');
            };

            xhr.send(formData);
        } catch (err) {
            console.error('Upload error:', err);
            setIsUploading(false);
            showToast('Terjadi kesalahan saat mengunggah video.', 'error');
        }
    };

    // Render an AI detected clip
    const handleRenderClip = async (clipId, ratio = '9:16') => {
        setRenderingClipIds(prev => new Set(prev).add(clipId));
        showToast(`Rendering ${ratio} clip with FFmpeg...`, 'info');
        try {
            const res = await fetch(`/api/clips/${clipId}/render`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                },
                body: JSON.stringify({ aspect_ratio: ratio })
            });

            let data;
            try {
                data = await res.json();
            } catch (e) {
                data = { success: false, error: 'Could not parse response' };
            }

            if (data.success && data.clip) {
                setCurrentProject(prev => ({
                    ...prev,
                    clips: (prev?.clips || []).map(c => c.id === clipId ? data.clip : c)
                }));
                showToast(`Clip rendered successfully (${data.clip.file_size_mb} MB)`, 'success');
                confetti({
                    particleCount: 50,
                    spread: 60,
                    origin: { y: 0.7 }
                });
            } else {
                showToast('Render failed: ' + (data.error || 'FFmpeg error'), 'error');
            }
        } catch (err) {
            console.error('Render error:', err);
            showToast('Connection error during render', 'error');
        } finally {
            setRenderingClipIds(prev => {
                const next = new Set(prev);
                next.delete(clipId);
                return next;
            });
        }
    };

    // Render clip with Auto-Meme, SFX & Screen Shake
    const handleRenderMemeClip = async (clipId, ratio = '9:16', overrideIntensity = null) => {
        const intensity = overrideIntensity || clipMemeIntensity[clipId] || 'rame';
        const intensityLabels = {
            santai: 'Santai ☕',
            rame: 'Rame 🔥',
            barbar: 'Bar-Bar 🤯'
        };
        setRenderingMemeClipIds(prev => new Set(prev).add(clipId));
        showToast(`Injecting memes (${intensityLabels[intensity] || intensity}), SFX & screen shake (${ratio})... ✨`, 'info');
        try {
            const res = await fetch(`/api/clips/${clipId}/render-meme`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                },
                body: JSON.stringify({ 
                    aspect_ratio: ratio,
                    intensity: intensity
                })
            });

            let data;
            try {
                data = await res.json();
            } catch (e) {
                data = { success: false, error: 'Could not parse response' };
            }

            if (data.success && data.clip) {
                setCurrentProject(prev => ({
                    ...prev,
                    clips: (prev?.clips || []).map(c => c.id === clipId ? data.clip : c)
                }));
                showToast(`🔥 Auto-Meme video ready! (${data.clip.meme_file_size_mb} MB)`, 'success');
                confetti({
                    particleCount: 80,
                    spread: 70,
                    origin: { y: 0.6 }
                });
            } else {
                showToast('Auto-Meme failed: ' + (data.error || 'FFmpeg error'), 'error');
            }
        } catch (err) {
            console.error('Meme render error:', err);
            showToast('Connection error during meme render', 'error');
        } finally {
            setRenderingMemeClipIds(prev => {
                const next = new Set(prev);
                next.delete(clipId);
                return next;
            });
        }
    };

    // Create custom manual clip
    const handleRenderCustomClip = async () => {
        if (!currentProject || isRenderingCustom) return;
        setIsRenderingCustom(true);
        showToast('Rendering custom clip...', 'info');
        try {
            const res = await fetch(`/api/projects/${currentProject.id}/custom-clip`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                },
                body: JSON.stringify({
                    title: customTitle,
                    start_time: startTime,
                    end_time: endTime,
                    aspect_ratio: aspectRatio
                })
            });

            let data;
            try {
                data = await res.json();
            } catch (e) {
                data = { success: false, error: 'Invalid response' };
            }

            if (data.success && data.clip) {
                setCurrentProject(prev => ({
                    ...prev,
                    clips: [data.clip, ...(prev?.clips || [])]
                }));
                setActiveTab('rendered');
                showToast('Custom clip created', 'success');
                confetti({
                    particleCount: 60,
                    spread: 70,
                    origin: { y: 0.7 }
                });
            } else {
                showToast('Custom clip failed: ' + (data.error || 'Unknown error'), 'error');
            }
        } catch (err) {
            console.error('Custom render error:', err);
            showToast('Failed to create custom clip', 'error');
        } finally {
            setIsRenderingCustom(false);
        }
    };

    // Video Player Controls
    const jumpToTime = (timeInSec) => {
        if (videoRef.current) {
            videoRef.current.currentTime = timeInSec;
            videoRef.current.play();
            setIsPlaying(true);
        }
    };

    const formatSeconds = (sec) => {
        const n = Math.max(0, Math.floor(Number(sec) || 0));
        const m = Math.floor(n / 60);
        const s = Math.floor(n % 60);
        return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
    };

    const renderedClips = (currentProject?.clips || []).filter(c => c.status === 'completed' || !!c.meme_clip_path || !!c.clip_path);
    const projectDuration = Number(currentProject?.duration) || 0;
    const projectStatus = (currentProject?.status || 'pending').toLowerCase();

    // Helper to generate full YouTube Shorts copy text with Fair Use Disclaimer
    const getFullShortsText = (clip) => {
        const tags = parseHashtags(clip.hashtags).join(' ');
        const cap = clip.caption || `Tonton bagian seru ini! 🔥\n\n"${clip.hook || clip.title}"\n\nTulis pendapat kalian di kolom komentar ya! 👇\n\n━━━━━━━━━━━━━━━━━━━━━━\n📌 CREDITS: @${currentProject?.channel || 'Original Creator'}\n⚠️ FAIR USE NOTICE: Video used under Fair Use for commentary/entertainment.`;
        return `${clip.title}\n\n${cap}\n\n${tags}`;
    };

    return (
        <div className="min-h-screen bg-[#09090b] text-[#f4f4f5] flex flex-col font-sans selection:bg-zinc-800 selection:text-zinc-100 pb-20">
            
            {/* Minimalist Floating Toast */}
            {toast && (
                <div className="fixed bottom-6 right-6 z-50 px-4 py-3 rounded-lg shadow-xl flex items-center gap-3 text-xs font-medium border border-zinc-800 bg-zinc-900/95 backdrop-blur-md transition-all duration-200">
                    {toast.type === 'success' && <span className="w-2 h-2 rounded-full bg-emerald-400 dot-indicator" />}
                    {toast.type === 'error' && <span className="w-2 h-2 rounded-full bg-rose-400 dot-indicator" />}
                    {toast.type === 'info' && <RefreshCw className="w-3.5 h-3.5 text-zinc-400 animate-spin shrink-0" />}
                    <span className="text-zinc-200">{toast.message}</span>
                </div>
            )}

            {/* Precision Navbar (21st.dev Style) */}
            <header className="sticky top-0 z-40 border-b border-zinc-800/80 bg-[#09090b]/80 backdrop-blur-xl px-6 py-3.5 flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <div className="w-7 h-7 rounded-md bg-gradient-to-br from-teal-400 to-emerald-600 flex items-center justify-center mr-2.5 shadow-[0_0_15px_rgba(20,184,166,0.3)]">
                        <Scissors className="w-3.5 h-3.5 text-black" />
                    </div>
                    <div className="flex items-center gap-2">
                        <span className="font-semibold text-sm tracking-tight text-white">Klip_Kyy</span>
                        <span className="text-zinc-600 text-xs">/</span>
                        <span className="text-xs text-zinc-400 font-mono">Studio</span>
                    </div>
                    <div className="hidden sm:flex items-center gap-1.5 ml-2 px-2 py-0.5 rounded-full border border-emerald-500/30 bg-emerald-950/40 text-[11px] text-emerald-300 font-mono">
                        <ShieldCheck className="w-3 h-3 text-emerald-400" />
                        <span>Anti-Copyright & Fair Use Engine</span>
                    </div>
                </div>

                <div className="flex items-center gap-3">
                    {projects.length > 1 && (
                        <div className="relative">
                            <select 
                                className="text-xs bg-zinc-900 border border-zinc-800 text-zinc-300 rounded-lg pl-3 pr-8 py-1.5 focus:outline-none focus:border-zinc-600 appearance-none cursor-pointer font-sans"
                                value={currentProject?.id || ''}
                                onChange={(e) => {
                                    const found = projects.find(p => p.id === parseInt(e.target.value));
                                    if (found) setCurrentProject(found);
                                }}
                            >
                                {projects.map(p => (
                                    <option key={p.id} value={p.id}>
                                        {p.title ? p.title.substring(0, 32) + '...' : `Project #${p.id}`}
                                    </option>
                                ))}
                            </select>
                            <ChevronDown className="w-3.5 h-3.5 text-zinc-500 absolute right-2.5 top-1/2 -translate-y-1/2 pointer-events-none" />
                        </div>
                    )}

                    <div className="text-[11px] font-mono text-zinc-400 border border-zinc-800 bg-zinc-900/50 px-2.5 py-1 rounded-md">
                        FFmpeg 7.1
                    </div>
                </div>
            </header>

            {/* Main Content */}
            <main className="max-w-6xl w-full mx-auto px-4 sm:px-6 pt-8 flex-1 flex flex-col gap-8">
                
                {/* Input Mode Switcher & Command Section */}
                <section className="flex flex-col items-center gap-3 w-full">
                    {/* Switcher Pill */}
                    <div className="flex items-center p-1 rounded-xl bg-zinc-900/90 border border-zinc-800 text-xs shadow-sm">
                        <button
                            type="button"
                            onClick={() => setInputMode('url')}
                            className={`py-1.5 px-4 rounded-lg font-medium transition cursor-pointer flex items-center gap-2 ${
                                inputMode === 'url'
                                    ? 'bg-zinc-800 text-zinc-100 shadow-sm border border-zinc-700/60'
                                    : 'text-zinc-400 hover:text-zinc-200'
                            }`}
                        >
                            <Video className="w-3.5 h-3.5 text-zinc-400" />
                            <span>Link YouTube</span>
                        </button>
                        <button
                            type="button"
                            onClick={() => setInputMode('upload')}
                            className={`py-1.5 px-4 rounded-lg font-medium transition cursor-pointer flex items-center gap-2 ${
                                inputMode === 'upload'
                                    ? 'bg-zinc-800 text-zinc-100 shadow-sm border border-zinc-700/60'
                                    : 'text-zinc-400 hover:text-zinc-200'
                            }`}
                        >
                            <UploadCloud className="w-3.5 h-3.5 text-emerald-400" />
                            <span>Upload Video Lokal</span>
                            <span className="px-1.5 py-0.5 rounded text-[9px] font-mono bg-emerald-500/20 text-emerald-300 font-semibold border border-emerald-500/30">Auto-Caption STT</span>
                        </button>
                    </div>

                    {/* Mode 1: YouTube URL Input */}
                    {inputMode === 'url' && (
                        <div className="w-full max-w-2xl flex flex-col items-center gap-3">
                            <form onSubmit={handleStartAutoClip} className="w-full relative flex items-center">
                                <div className="absolute left-4 flex items-center pointer-events-none text-zinc-500">
                                    <Video className="w-4 h-4" />
                                </div>
                                <input
                                    type="url"
                                    required
                                    value={videoUrl}
                                    onChange={(e) => setVideoUrl(e.target.value)}
                                    placeholder="Paste link video YouTube (contoh: https://youtu.be/...)"
                                    className="w-full pl-11 pr-32 py-3 rounded-xl craft-input text-sm text-zinc-100 placeholder-zinc-500 focus:outline-none font-sans"
                                />
                                <div className="absolute right-2 flex items-center gap-1.5">
                                    <button
                                        type="submit"
                                        disabled={isSubmitting || !videoUrl}
                                        className="craft-btn-primary px-3.5 py-1.5 rounded-lg text-xs font-medium flex items-center gap-1.5 cursor-pointer disabled:opacity-40 disabled:cursor-not-allowed shadow-sm"
                                    >
                                        {isSubmitting ? (
                                            <>
                                                <RefreshCw className="w-3 h-3 animate-spin" />
                                                <span>Processing...</span>
                                            </>
                                        ) : (
                                            <>
                                                <span>Clip Video</span>
                                                <CornerDownLeft className="w-3 h-3 text-zinc-500" />
                                            </>
                                        )}
                                    </button>
                                </div>
                            </form>

                            {/* Quick Demo Chips */}
                            <div className="flex flex-wrap items-center justify-center gap-2 text-xs text-zinc-500 font-mono">
                                <span className="text-[11px]">Quick Samples:</span>
                                <button 
                                    type="button" 
                                    onClick={() => setVideoUrl('https://www.youtube.com/watch?v=jNQXAC9IVRw')}
                                    className="px-2.5 py-1 rounded-md bg-zinc-900/80 hover:bg-zinc-800 border border-zinc-800 text-zinc-400 hover:text-zinc-200 transition text-[11px] font-sans cursor-pointer"
                                >
                                    Me at the zoo (Short)
                                </button>
                                <button 
                                    type="button" 
                                    onClick={() => setVideoUrl('https://youtu.be/avP1G9p1Vkc?si=JyyT3EiAu-oWwsMH')}
                                    className="px-2.5 py-1 rounded-md bg-zinc-900/80 hover:bg-zinc-800 border border-zinc-800 text-zinc-400 hover:text-zinc-200 transition text-[11px] font-sans cursor-pointer"
                                >
                                    Lapor Pak (Podcast)
                                </button>
                            </div>
                        </div>
                    )}

                    {/* Mode 2: Local Video Upload with Speech-to-Text & Auto-Caption */}
                    {inputMode === 'upload' && (
                        <div className="w-full max-w-2xl flex flex-col gap-3">
                            <form onSubmit={handleUploadVideo} className="craft-card p-5 rounded-2xl border border-zinc-800/90 shadow-xl flex flex-col gap-4">
                                <input
                                    type="file"
                                    ref={fileInputRef}
                                    accept="video/mp4,video/quicktime,video/webm,video/x-matroska,video/avi"
                                    onChange={(e) => {
                                        if (e.target.files && e.target.files[0]) {
                                            handleFileChange(e.target.files[0]);
                                        }
                                    }}
                                    className="hidden"
                                />

                                {/* Drag & Drop Dropzone */}
                                {!uploadFile ? (
                                    <div
                                        onDragOver={handleDragOver}
                                        onDragLeave={handleDragLeave}
                                        onDrop={handleDrop}
                                        onClick={() => fileInputRef.current?.click()}
                                        className={`p-6 border-2 border-dashed rounded-xl flex flex-col items-center justify-center gap-2.5 text-center cursor-pointer transition ${
                                            isDragging 
                                                ? 'border-emerald-500 bg-emerald-950/20' 
                                                : 'border-zinc-800 hover:border-zinc-700 bg-zinc-950/40 hover:bg-zinc-900/40'
                                        }`}
                                    >
                                        <div className="w-11 h-11 rounded-full bg-zinc-900 border border-zinc-800 flex items-center justify-center text-zinc-300">
                                            <UploadCloud className="w-5 h-5 text-emerald-400" />
                                        </div>
                                        <div className="space-y-0.5">
                                            <p className="text-xs font-semibold text-zinc-200">
                                                Klik untuk pilih video atau drag & drop file ke sini
                                            </p>
                                            <p className="text-[11px] text-zinc-500 font-sans">
                                                Format: MP4, MOV, WebM, MKV (Maksimal 200MB / durasi pendek)
                                            </p>
                                        </div>
                                        <div className="flex items-center gap-2 mt-1">
                                            <span className="px-2 py-0.5 rounded-full text-[10px] font-mono bg-zinc-900 text-zinc-400 border border-zinc-800 flex items-center gap-1">
                                                <Mic className="w-2.5 h-2.5 text-emerald-400" />
                                                <span>Auto Speech-to-Text (Indonesian/English)</span>
                                            </span>
                                        </div>
                                    </div>
                                ) : (
                                    <div className="p-4 rounded-xl bg-zinc-950/60 border border-zinc-800 flex items-center justify-between">
                                        <div className="flex items-center gap-3 min-w-0">
                                            <div className="w-10 h-10 rounded-lg bg-zinc-900 border border-zinc-800 flex items-center justify-center shrink-0">
                                                <FileVideo className="w-5 h-5 text-emerald-400" />
                                            </div>
                                            <div className="min-w-0 space-y-0.5">
                                                <p className="text-xs font-semibold text-zinc-200 truncate">{uploadFile.name}</p>
                                                <p className="text-[11px] text-zinc-500 font-mono">{(uploadFile.size / (1024 * 1024)).toFixed(2)} MB</p>
                                            </div>
                                        </div>
                                        <button
                                            type="button"
                                            onClick={() => setUploadFile(null)}
                                            className="p-1.5 rounded-lg text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800 cursor-pointer"
                                            title="Ganti file"
                                        >
                                            <X className="w-4 h-4" />
                                        </button>
                                    </div>
                                )}

                                {/* Video Topic / Title Input */}
                                <div className="space-y-1.5">
                                    <label className="text-[11px] font-medium text-zinc-400 flex items-center justify-between">
                                        <span>Topik / Judul Video:</span>
                                        <span className="text-[10px] text-zinc-500 font-mono">Opsional</span>
                                    </label>
                                    <input
                                        type="text"
                                        value={uploadTitleHint}
                                        onChange={(e) => setUploadTitleHint(e.target.value)}
                                        placeholder="Contoh: Mobile Legends Maniac / Gameplay Savage / Podcast Lucu"
                                        className="w-full px-3 py-2 rounded-lg craft-input text-xs text-zinc-100 font-sans"
                                    />
                                    {/* Quick Preset Tags */}
                                    <div className="flex flex-wrap items-center gap-1.5 pt-0.5">
                                        <span className="text-[10px] text-zinc-500 font-mono">Pilih Preset Cepat:</span>
                                        <button
                                            type="button"
                                            onClick={() => setUploadTitleHint('Mobile Legends Maniac')}
                                            className="px-2 py-0.5 rounded-md bg-zinc-900 hover:bg-zinc-800 text-zinc-300 hover:text-emerald-300 border border-zinc-800 text-[10px] font-sans cursor-pointer transition flex items-center gap-1"
                                        >
                                            <span>🎮 MLBB Maniac</span>
                                        </button>
                                        <button
                                            type="button"
                                            onClick={() => setUploadTitleHint('Mobile Legends Savage')}
                                            className="px-2 py-0.5 rounded-md bg-zinc-900 hover:bg-zinc-800 text-zinc-300 hover:text-emerald-300 border border-zinc-800 text-[10px] font-sans cursor-pointer transition flex items-center gap-1"
                                        >
                                            <span>⚔️ MLBB Savage</span>
                                        </button>
                                        <button
                                            type="button"
                                            onClick={() => setUploadTitleHint('Momen Lucu Ngakak')}
                                            className="px-2 py-0.5 rounded-md bg-zinc-900 hover:bg-zinc-800 text-zinc-300 hover:text-amber-300 border border-zinc-800 text-[10px] font-sans cursor-pointer transition flex items-center gap-1"
                                        >
                                            <span>😂 Meme Lucu</span>
                                        </button>
                                        <button
                                            type="button"
                                            onClick={() => setUploadTitleHint('Podcast Cerita')}
                                            className="px-2 py-0.5 rounded-md bg-zinc-900 hover:bg-zinc-800 text-zinc-300 hover:text-sky-300 border border-zinc-800 text-[10px] font-sans cursor-pointer transition flex items-center gap-1"
                                        >
                                            <span>🎙️ Podcast</span>
                                        </button>
                                    </div>
                                </div>

                                {/* Channel / Creator attribution input */}
                                <div className="space-y-1.5">
                                    <label className="text-[11px] font-medium text-zinc-400 flex items-center justify-between">
                                        <span>Nama Kreator / Channel Asli (untuk Kredit & Atribusi Anti-Copyright):</span>
                                        <span className="text-[10px] text-zinc-500 font-mono">Opsional</span>
                                    </label>
                                    <input
                                        type="text"
                                        value={uploadChannel}
                                        onChange={(e) => setUploadChannel(e.target.value)}
                                        placeholder="Contoh: @MyChannel / @OriginalCreator"
                                        className="w-full px-3 py-2 rounded-lg craft-input text-xs text-zinc-100 font-sans"
                                    />
                                </div>

                                {/* Submit button with Progress */}
                                <div className="flex flex-col gap-2">
                                    <button
                                        type="submit"
                                        disabled={!uploadFile || isUploading}
                                        className="w-full craft-btn-primary py-2.5 px-4 rounded-xl text-xs font-semibold flex items-center justify-center gap-2 cursor-pointer disabled:opacity-40 disabled:cursor-not-allowed shadow-md"
                                    >
                                        {isUploading ? (
                                            <>
                                                <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                                                <span>Mengekstrak Audio & Membuat Caption ({uploadProgress}%)...</span>
                                            </>
                                        ) : (
                                            <>
                                                <Sparkles className="w-3.5 h-3.5 text-zinc-950" />
                                                <span>Upload & Otomatis Buat Caption YouTube Shorts</span>
                                            </>
                                        )}
                                    </button>

                                    {isUploading && (
                                        <div className="w-full bg-zinc-900 rounded-full h-1.5 overflow-hidden mt-1">
                                            <div 
                                                className="bg-emerald-400 h-full rounded-full transition-all duration-300"
                                                style={{ width: `${Math.max(uploadProgress, 10)}%` }}
                                            />
                                        </div>
                                    )}
                                </div>

                                <p className="text-[11px] text-zinc-400 text-center font-sans">
                                    💡 Sistem akan otomatis mengekstrak audio, mentranskripsikan ucapan secara akurat, dan meracik judul, hook, sinopsis cerita, serta Fair Use disclaimer yang 100% selaras dengan percakapan dalam video.
                                </p>
                            </form>
                        </div>
                    )}
                </section>

                {/* Progress Status Bar */}
                {currentProject && projectStatus !== 'ready' && projectStatus !== 'failed' && (
                    <div className="craft-card p-4 rounded-xl border border-zinc-800/90 flex flex-col gap-3">
                        <div className="flex items-center justify-between text-xs">
                            <div className="flex items-center gap-2 text-zinc-300">
                                <RefreshCw className="w-3.5 h-3.5 animate-spin text-zinc-400" />
                                <span>{currentProject.status_message || 'Processing video...'}</span>
                            </div>
                            <span className="font-mono text-zinc-400">{currentProject.progress || 0}%</span>
                        </div>
                        <div className="w-full bg-zinc-900 rounded-full h-1.5 overflow-hidden">
                            <div 
                                className="bg-zinc-100 h-full rounded-full transition-all duration-300"
                                style={{ width: `${Math.max(currentProject.progress || 0, 5)}%` }}
                            ></div>
                        </div>
                    </div>
                )}

                {/* Workspace Grid */}
                {currentProject && (
                    <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
                        
                        {/* Left Column: Video Viewport & Aspect Ratio Selector (5 Cols) */}
                        <div className="lg:col-span-5 flex flex-col gap-4">
                            
                            {/* Video Player Card */}
                            <div className="craft-card p-4 rounded-xl flex flex-col gap-3">
                                
                                {/* Video Player Frame */}
                                <div className="relative rounded-lg overflow-hidden bg-black aspect-video border border-zinc-800 shadow-sm">
                                    {currentProject.video_path ? (
                                        <video
                                            ref={videoRef}
                                            src={currentProject.video_path}
                                            controls
                                            className="w-full h-full object-contain"
                                            onTimeUpdate={() => setCurrentTime(videoRef.current?.currentTime || 0)}
                                            onPlay={() => setIsPlaying(true)}
                                            onPause={() => setIsPlaying(false)}
                                        />
                                    ) : (
                                        <div className="w-full h-full flex flex-col items-center justify-center p-6 text-center text-zinc-500">
                                            {currentProject.thumbnail && (
                                                <img src={currentProject.thumbnail} alt="Thumbnail" className="absolute inset-0 w-full h-full object-cover opacity-20" />
                                            )}
                                            <Film className="w-6 h-6 mb-2 relative z-10 text-zinc-400" />
                                            <p className="text-xs relative z-10 font-sans">Processing video...</p>
                                        </div>
                                    )}
                                </div>

                                {/* Title & Metadata */}
                                <div className="space-y-1.5">
                                    <h3 className="font-semibold text-sm text-zinc-100 line-clamp-2 leading-snug">
                                        {currentProject.title || 'Video Project'}
                                    </h3>
                                    <div className="flex items-center justify-between text-xs text-zinc-400 font-mono">
                                        <span className="truncate max-w-[200px] text-zinc-400 font-sans font-medium">@{currentProject.channel || 'Channel'}</span>
                                        <div className="flex items-center gap-2 text-[11px]">
                                            <span className="text-zinc-300">{formatSeconds(currentTime)}</span>
                                            <span className="text-zinc-600">/</span>
                                            <span className="text-zinc-500">{formatSeconds(projectDuration)}</span>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            {/* Aspect Ratio Presets Box */}
                            <div className="craft-card p-4 rounded-xl space-y-2.5">
                                <div className="flex items-center justify-between text-xs text-zinc-400">
                                    <span className="font-medium text-zinc-300">Format Ekspor FFmpeg</span>
                                    <span className="font-mono text-[10px] uppercase text-zinc-500">Auto-Scale</span>
                                </div>
                                <div className="grid grid-cols-3 gap-2">
                                    <div className="p-2.5 rounded-lg bg-zinc-900/60 border border-zinc-800 text-center space-y-1">
                                        <Smartphone className="w-4 h-4 mx-auto text-zinc-300" />
                                        <p className="font-medium text-xs text-zinc-200">9:16</p>
                                        <p className="text-[10px] text-zinc-500 font-mono">TikTok / Shorts</p>
                                    </div>
                                    <div className="p-2.5 rounded-lg bg-zinc-900/60 border border-zinc-800 text-center space-y-1">
                                        <Monitor className="w-4 h-4 mx-auto text-zinc-300" />
                                        <p className="font-medium text-xs text-zinc-200">16:9</p>
                                        <p className="text-[10px] text-zinc-500 font-mono">Landscape</p>
                                    </div>
                                    <div className="p-2.5 rounded-lg bg-zinc-900/60 border border-zinc-800 text-center space-y-1">
                                        <Square className="w-4 h-4 mx-auto text-zinc-300" />
                                        <p className="font-medium text-xs text-zinc-200">1:1</p>
                                        <p className="text-[10px] text-zinc-500 font-mono">Feed</p>
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Right Column: Studio Segmented Tabs & Cards (7 Cols) */}
                        <div className="lg:col-span-7 flex flex-col gap-4">
                            
                            {/* Segmented Control Tabs */}
                            <div className="flex items-center p-1 rounded-xl bg-zinc-900/80 border border-zinc-800/90 text-xs">
                                <button
                                    onClick={() => setActiveTab('highlights')}
                                    className={`flex-1 py-1.5 px-3 rounded-lg font-medium transition cursor-pointer flex items-center justify-center gap-1.5 ${
                                        activeTab === 'highlights'
                                            ? 'bg-zinc-800 text-zinc-100 shadow-sm border border-zinc-700/60'
                                            : 'text-zinc-400 hover:text-zinc-200'
                                    }`}
                                >
                                    <Sparkles className="w-3.5 h-3.5 text-zinc-400" />
                                    <span>AI Highlights ({(currentProject?.clips || []).length})</span>
                                </button>
                                <button
                                    onClick={() => setActiveTab('manual')}
                                    className={`flex-1 py-1.5 px-3 rounded-lg font-medium transition cursor-pointer flex items-center justify-center gap-1.5 ${
                                        activeTab === 'manual'
                                            ? 'bg-zinc-800 text-zinc-100 shadow-sm border border-zinc-700/60'
                                            : 'text-zinc-400 hover:text-zinc-200'
                                    }`}
                                >
                                    <Scissors className="w-3.5 h-3.5 text-zinc-400" />
                                    <span>Manual Clipper</span>
                                </button>
                                <button
                                    onClick={() => setActiveTab('rendered')}
                                    className={`flex-1 py-1.5 px-3 rounded-lg font-medium transition cursor-pointer flex items-center justify-center gap-1.5 ${
                                        activeTab === 'rendered'
                                            ? 'bg-zinc-800 text-zinc-100 shadow-sm border border-zinc-700/60'
                                            : 'text-zinc-400 hover:text-zinc-200'
                                    }`}
                                >
                                    <Film className="w-3.5 h-3.5 text-zinc-400" />
                                    <span>Exports ({renderedClips.length})</span>
                                </button>
                            </div>

                            {/* TAB 1: AI HIGHLIGHTS */}
                            {activeTab === 'highlights' && (
                                <div className="flex flex-col gap-3">
                                    {(currentProject?.clips || []).length > 0 ? (
                                        currentProject.clips.map((clip) => {
                                            const isRendering = renderingClipIds.has(clip.id);
                                            const isRenderingMeme = renderingMemeClipIds.has(clip.id);
                                            const isCompleted = clip.status === 'completed';
                                            const isExpanded = !!expandedShortsKit[clip.id];
                                            const isCopiedAll = !!copiedStates[`all_${clip.id}`];
                                            const isCopiedTitle = !!copiedStates[`title_${clip.id}`];
                                            const isCopiedCaption = !!copiedStates[`cap_${clip.id}`];
                                            const clipTags = parseHashtags(clip.hashtags);

                                            return (
                                                <div 
                                                    key={clip.id} 
                                                    className="craft-card craft-card-interactive p-4.5 rounded-xl border border-zinc-800/90 flex flex-col gap-3"
                                                >
                                                    {/* Card Header */}
                                                    <div className="flex items-center justify-between">
                                                        <div className="flex items-center gap-2">
                                                            <span className="px-2 py-0.5 rounded-md text-[11px] font-mono font-semibold bg-zinc-900 text-zinc-200 border border-zinc-800 flex items-center gap-1">
                                                                <span className="w-1.5 h-1.5 rounded-full bg-amber-400"></span>
                                                                <span>{clip.virality_score || 90}% Viral</span>
                                                            </span>
                                                            <span className="text-xs font-mono text-zinc-400">
                                                                {formatSeconds(clip.start_time)} — {formatSeconds(clip.end_time)} ({Math.round(Number(clip.duration) || 0)}s)
                                                            </span>
                                                        </div>

                                                        <button
                                                            onClick={() => jumpToTime(clip.start_time)}
                                                            className="text-xs text-zinc-400 hover:text-zinc-100 flex items-center gap-1 font-medium transition cursor-pointer"
                                                        >
                                                            <Play className="w-3 h-3 fill-current" />
                                                            <span>Preview</span>
                                                        </button>
                                                    </div>

                                                    {/* Card Body */}
                                                    <div className="space-y-1.5">
                                                        <h4 className="font-semibold text-sm text-zinc-100 leading-snug">{clip.title}</h4>
                                                        {clip.hook && (
                                                            <p className="text-xs text-zinc-300 italic border-l-2 border-zinc-700 pl-2.5 py-0.5 font-sans">
                                                                "{clip.hook}"
                                                            </p>
                                                        )}
                                                        {clip.reason && (
                                                            <p className="text-[11px] text-zinc-400 flex items-center gap-1.5 pt-0.5">
                                                                <TrendingUp className="w-3 h-3 text-zinc-500 shrink-0" />
                                                                <span>{clip.reason}</span>
                                                            </p>
                                                        )}
                                                    </div>

                                                    {/* YouTube Shorts Kit Section with Anti-Copyright & Fair Use */}
                                                    <div className="rounded-lg bg-zinc-900/90 border border-zinc-800/80 p-3 flex flex-col gap-2.5">
                                                        <div className="flex items-center justify-between flex-wrap gap-2">
                                                            <div className="flex items-center gap-2">
                                                                <span className="w-2 h-2 rounded-full bg-red-500"></span>
                                                                <span className="text-xs text-zinc-200 font-medium">YouTube Shorts Kit</span>
                                                                <span className="px-1.5 py-0.5 rounded text-[10px] font-mono bg-emerald-950/80 text-emerald-300 border border-emerald-500/30 flex items-center gap-1">
                                                                    <ShieldCheck className="w-2.5 h-2.5" />
                                                                    <span>Anti-Copyright & Credits</span>
                                                                </span>
                                                            </div>

                                                            <div className="flex items-center gap-1.5">
                                                                {/* One-Click Copy All */}
                                                                <button
                                                                    type="button"
                                                                    onClick={() => copyToClipboard(getFullShortsText(clip), `all_${clip.id}`, 'Paket Shorts Lengkap (Judul + Sinopsis + Kredit + Tag)')}
                                                                    className={`px-2.5 py-1 rounded-md text-[11px] font-medium flex items-center gap-1 transition cursor-pointer ${
                                                                        isCopiedAll 
                                                                            ? 'bg-emerald-950 text-emerald-300 border border-emerald-500/40'
                                                                            : 'bg-zinc-800 hover:bg-zinc-700 text-zinc-200 border border-zinc-700/60'
                                                                    }`}
                                                                >
                                                                    {isCopiedAll ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3 text-zinc-400" />}
                                                                    <span>{isCopiedAll ? 'Copied!' : 'Copy All for Shorts'}</span>
                                                                </button>

                                                                {/* Toggle Accordion */}
                                                                <button
                                                                    type="button"
                                                                    onClick={() => toggleShortsKit(clip.id)}
                                                                    className="p-1 rounded text-zinc-400 hover:text-zinc-200 cursor-pointer"
                                                                    title="Lihat detail caption, kredit & tag"
                                                                >
                                                                    {isExpanded ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
                                                                </button>
                                                            </div>
                                                        </div>

                                                        {/* Expanded Caption, Credits & Tag Details */}
                                                        {isExpanded && (
                                                            <div className="pt-2 border-t border-zinc-800 space-y-2.5 text-xs">
                                                                {/* Shorts Title */}
                                                                <div className="space-y-1">
                                                                    <div className="flex items-center justify-between text-[10px] text-zinc-400">
                                                                        <span className="font-mono uppercase text-zinc-400">Judul Shorts (Catchy):</span>
                                                                        <button
                                                                            type="button"
                                                                            onClick={() => copyToClipboard(clip.title, `title_${clip.id}`, 'Judul Shorts')}
                                                                            className="text-zinc-400 hover:text-zinc-200 flex items-center gap-1 cursor-pointer font-sans"
                                                                        >
                                                                            {isCopiedTitle ? <Check className="w-2.5 h-2.5 text-emerald-400" /> : <Copy className="w-2.5 h-2.5" />}
                                                                            <span>Copy Judul</span>
                                                                        </button>
                                                                    </div>
                                                                    <p className="text-zinc-200 font-medium bg-zinc-950/60 px-2.5 py-1.5 rounded border border-zinc-800/80 select-all">
                                                                        {clip.title}
                                                                    </p>
                                                                </div>

                                                                {/* Shorts Caption / Narrative Context */}
                                                                <div className="space-y-1">
                                                                    <div className="flex items-center justify-between text-[10px] text-zinc-400">
                                                                        <span className="font-mono uppercase text-zinc-400">Sinopsis Isi Video, Kredit & Fair Use Disclaimer:</span>
                                                                        <button
                                                                            type="button"
                                                                            onClick={() => copyToClipboard(clip.caption || '', `cap_${clip.id}`, 'Deskripsi & Disclaimer')}
                                                                            className="text-zinc-400 hover:text-zinc-200 flex items-center gap-1 cursor-pointer font-sans"
                                                                        >
                                                                            {isCopiedCaption ? <Check className="w-2.5 h-2.5 text-emerald-400" /> : <Copy className="w-2.5 h-2.5" />}
                                                                            <span>Copy Caption & Disclaimer</span>
                                                                        </button>
                                                                    </div>
                                                                    <p className="text-zinc-300 whitespace-pre-line bg-zinc-950/60 p-2.5 rounded border border-zinc-800/80 leading-relaxed select-all font-sans text-[11px]">
                                                                        {clip.caption || 'Tonton bagian seru ini! Drop komentar kalian di bawah! 👇'}
                                                                    </p>
                                                                </div>

                                                                {/* Hashtags */}
                                                                {clipTags && clipTags.length > 0 && (
                                                                    <div className="flex items-center justify-between flex-wrap gap-1.5 pt-1">
                                                                        <div className="flex flex-wrap gap-1.5">
                                                                            {clipTags.map((tag, tIdx) => (
                                                                                <span key={tIdx} className="px-2 py-0.5 rounded bg-zinc-800/80 text-zinc-400 text-[10px] font-mono border border-zinc-700/50">
                                                                                    {tag}
                                                                                </span>
                                                                            ))}
                                                                        </div>
                                                                        <button
                                                                            type="button"
                                                                            onClick={() => copyToClipboard(clipTags.join(' '), `tag_${clip.id}`, 'Hashtags')}
                                                                            className="text-[11px] text-zinc-400 hover:text-zinc-200 flex items-center gap-1 cursor-pointer font-sans"
                                                                        >
                                                                            <Copy className="w-2.5 h-2.5" />
                                                                            <span>Copy Tags</span>
                                                                        </button>
                                                                    </div>
                                                                )}
                                                            </div>
                                                        )}
                                                    </div>

                                                    {/* Auto-Meme & SFX Timeline Badges */}
                                                    <div className="rounded-lg bg-gradient-to-r from-amber-500/10 via-amber-950/20 to-orange-500/10 border border-amber-500/30 p-2.5 flex flex-col gap-2">
                                                        <div className="flex items-center justify-between">
                                                            <div className="flex items-center gap-1.5 text-xs text-amber-300 font-medium">
                                                                <Flame className="w-3.5 h-3.5 text-amber-400" />
                                                                <span>Auto-Meme Soundboard & Camera Sync ✨</span>
                                                            </div>
                                                            <span className="text-[10px] text-amber-400/80 font-mono">
                                                                {clip.meme_cues && clip.meme_cues.length > 0 ? `${clip.meme_cues.length} Cue Siap` : 'Auto Punch-Zoom & SFX'}
                                                            </span>
                                                        </div>

                                                        {clip.meme_cues && clip.meme_cues.length > 0 ? (
                                                            <div className="flex items-center gap-1.5 flex-wrap pt-0.5">
                                                                {clip.meme_cues.map((cue, cueIdx) => {
                                                                    const memeIcons = {
                                                                        vine_boom: '💥',
                                                                        metal_pipe: '🛢️',
                                                                        taco_bell: '🔔',
                                                                        bonk: '🔨',
                                                                        bruh: '🗿',
                                                                        emotional_damage: '💔',
                                                                        windows_error: '💻',
                                                                        fart_reverb: '💨',
                                                                        huh: '❓',
                                                                        run: '🏃',
                                                                        laugh_wheeze: '🤣',
                                                                        cricket: '🦗',
                                                                        anime_wow: '✨',
                                                                        directed_by: '🎬'
                                                                    };
                                                                    const icon = memeIcons[cue.effect] || '🎬';
                                                                    return (
                                                                        <span 
                                                                            key={cueIdx} 
                                                                            title={cue.reason || cue.effect}
                                                                            className="px-2 py-0.5 rounded bg-zinc-900/90 text-amber-200 text-[10px] font-mono border border-amber-500/40 flex items-center gap-1 shadow-sm"
                                                                        >
                                                                            <span>{icon}</span>
                                                                            <span className="capitalize">{cue.effect.replace('_', ' ')}</span>
                                                                            <span className="text-zinc-400 font-sans">@{cue.time}s</span>
                                                                            {cue.punch_zoom && <span className="text-[9px] text-amber-400 font-bold">🔍 Zoom</span>}
                                                                            {cue.screen_shake && <span className="text-[9px] text-orange-400 font-bold">📳 Shake</span>}
                                                                        </span>
                                                                    );
                                                                })}
                                                            </div>
                                                        ) : (
                                                            <p className="text-[11px] text-zinc-400 font-sans">
                                                                Efek suara meme viral, punch zoom & screen shake kamera otomatis tersinkronisasi saat dirender.
                                                            </p>
                                                        )}

                                                        {/* Meme Intensity Presets */}
                                                        <div className="flex items-center justify-between pt-1.5 border-t border-amber-500/20 text-xs">
                                                            <span className="text-[11px] text-amber-200/90 font-medium">Level Keramaian:</span>
                                                            <div className="inline-flex rounded-lg bg-zinc-900/90 p-0.5 border border-zinc-800">
                                                                {[
                                                                    { id: 'santai', label: 'Santai ☕', hint: '2 Meme (Hook & Outro)' },
                                                                    { id: 'rame', label: 'Rame 🔥', hint: '4-6 Meme (Hype Multi-Drop)' },
                                                                    { id: 'barbar', label: 'Bar-Bar 🤯', hint: '7-10 Meme + Heavy Shake' }
                                                                ].map(preset => {
                                                                    const isSelected = (clipMemeIntensity[clip.id] || 'rame') === preset.id;
                                                                    return (
                                                                        <button
                                                                            key={preset.id}
                                                                            type="button"
                                                                            title={preset.hint}
                                                                            onClick={() => setClipMemeIntensity(prev => ({ ...prev, [clip.id]: preset.id }))}
                                                                            className={`px-2 py-0.5 rounded text-[10px] font-medium transition cursor-pointer ${
                                                                                isSelected 
                                                                                    ? 'bg-amber-500 text-zinc-950 font-bold shadow-sm' 
                                                                                    : 'text-zinc-400 hover:text-zinc-200'
                                                                            }`}
                                                                        >
                                                                            {preset.label}
                                                                        </button>
                                                                    );
                                                                })}
                                                            </div>
                                                        </div>
                                                    </div>

                                                    {/* Card Actions */}
                                                    <div className="pt-2 border-t border-zinc-800/60 flex flex-wrap items-center justify-between gap-2">
                                                        <div className="flex items-center flex-wrap gap-2">
                                                            {/* Clean 9:16 Render */}
                                                            <button
                                                                disabled={isRendering || isRenderingMeme}
                                                                onClick={() => handleRenderClip(clip.id, '9:16')}
                                                                className="craft-btn-secondary px-3 py-1.5 rounded-lg text-xs flex items-center gap-1.5 cursor-pointer disabled:opacity-50"
                                                            >
                                                                {isRendering ? (
                                                                    <>
                                                                        <RefreshCw className="w-3 h-3 animate-spin text-zinc-400" />
                                                                        <span>Rendering 9:16...</span>
                                                                    </>
                                                                ) : (
                                                                    <>
                                                                        <Smartphone className="w-3.5 h-3.5 text-zinc-400" />
                                                                        <span>Clean 9:16</span>
                                                                    </>
                                                                )}
                                                            </button>

                                                            {/* Auto-Meme 9:16 Render */}
                                                            <button
                                                                disabled={isRendering || isRenderingMeme}
                                                                onClick={() => handleRenderMemeClip(clip.id, '9:16')}
                                                                className="craft-btn-secondary px-3 py-1.5 rounded-lg text-xs flex items-center gap-1.5 cursor-pointer disabled:opacity-50 border-amber-500/40 hover:border-amber-400 text-amber-300 hover:text-amber-100 bg-amber-500/10 hover:bg-amber-500/20 shadow-sm transition"
                                                            >
                                                                {isRenderingMeme ? (
                                                                    <>
                                                                        <RefreshCw className="w-3 h-3 animate-spin text-amber-400" />
                                                                        <span>Meme Magic...</span>
                                                                    </>
                                                                ) : (
                                                                    <>
                                                                        <Flame className="w-3.5 h-3.5 text-amber-400" />
                                                                        <span>Auto-Meme 9:16 🔥</span>
                                                                    </>
                                                                )}
                                                            </button>

                                                            {/* 16:9 Render */}
                                                            <button
                                                                disabled={isRendering || isRenderingMeme}
                                                                onClick={() => handleRenderClip(clip.id, '16:9')}
                                                                className="craft-btn-secondary px-2.5 py-1.5 rounded-lg text-xs flex items-center gap-1 cursor-pointer disabled:opacity-50 text-zinc-400 hover:text-zinc-200"
                                                            >
                                                                <Monitor className="w-3.5 h-3.5" />
                                                                <span>16:9</span>
                                                            </button>
                                                        </div>

                                                        {/* Downloads */}
                                                        <div className="flex items-center flex-wrap gap-2">
                                                            {clip.clip_path && (
                                                                <a
                                                                    href={clip.clip_path}
                                                                    download
                                                                    target="_blank"
                                                                    rel="noreferrer"
                                                                    className="craft-btn-secondary px-3 py-1.5 rounded-lg text-xs font-medium flex items-center gap-1.5 shadow-sm cursor-pointer text-zinc-300 hover:text-white"
                                                                >
                                                                    <Download className="w-3 h-3" />
                                                                    <span>Clean ({clip.file_size_mb} MB)</span>
                                                                </a>
                                                            )}

                                                            {clip.meme_clip_path && (
                                                                <a
                                                                    href={clip.meme_clip_path}
                                                                    download
                                                                    target="_blank"
                                                                    rel="noreferrer"
                                                                    className="px-3.5 py-1.5 rounded-lg text-xs font-medium flex items-center gap-1.5 shadow-sm cursor-pointer bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-600 hover:to-orange-600 text-white font-sans transition"
                                                                >
                                                                    <Download className="w-3 h-3" />
                                                                    <span>Meme Video ({clip.meme_file_size_mb} MB) 🔥</span>
                                                                </a>
                                                            )}
                                                        </div>
                                                    </div>
                                                </div>
                                            );
                                        })
                                    ) : (
                                        <div className="craft-card p-8 text-center text-zinc-500 text-xs rounded-xl">
                                            No clips found yet. Paste a video URL to generate highlights automatically.
                                        </div>
                                    )}
                                </div>
                            )}

                            {/* TAB 2: MANUAL CLIPPER */}
                            {activeTab === 'manual' && (
                                <div className="craft-card p-5 rounded-xl border border-zinc-800 space-y-5">
                                    <div className="space-y-1">
                                        <h3 className="font-semibold text-sm text-zinc-100">Manual Video Trimmer</h3>
                                        <p className="text-xs text-zinc-500">Set precise in/out timestamps to render custom clips.</p>
                                    </div>

                                    {/* Title Input */}
                                    <div className="space-y-1.5">
                                        <label className="text-xs text-zinc-400 font-medium">Clip Title</label>
                                        <input
                                            type="text"
                                            value={customTitle}
                                            onChange={(e) => setCustomTitle(e.target.value)}
                                            className="w-full px-3 py-2 rounded-lg craft-input text-xs text-zinc-100 font-sans"
                                            placeholder="Enter clip title..."
                                        />
                                    </div>

                                    {/* Start & End Inputs */}
                                    <div className="grid grid-cols-2 gap-4">
                                        <div className="space-y-1.5">
                                            <div className="flex items-center justify-between text-xs">
                                                <label className="text-zinc-400 font-medium">Start Time (sec)</label>
                                                <button
                                                    type="button"
                                                    onClick={() => setStartTime(Math.round(currentTime * 10) / 10)}
                                                    className="text-[11px] text-zinc-400 hover:text-zinc-200 cursor-pointer font-mono"
                                                >
                                                    [Set In: {formatSeconds(currentTime)}]
                                                </button>
                                            </div>
                                            <input
                                                type="number"
                                                step="0.5"
                                                min="0"
                                                max={endTime - 1}
                                                value={startTime}
                                                onChange={(e) => setStartTime(parseFloat(e.target.value) || 0)}
                                                className="w-full px-3 py-2 rounded-lg craft-input text-xs text-zinc-100 font-mono"
                                            />
                                            <span className="text-[10px] text-zinc-500 font-mono">{formatSeconds(startTime)}</span>
                                        </div>

                                        <div className="space-y-1.5">
                                            <div className="flex items-center justify-between text-xs">
                                                <label className="text-zinc-400 font-medium">End Time (sec)</label>
                                                <button
                                                    type="button"
                                                    onClick={() => setEndTime(Math.round(currentTime * 10) / 10)}
                                                    className="text-[11px] text-zinc-400 hover:text-zinc-200 cursor-pointer font-mono"
                                                >
                                                    [Set Out: {formatSeconds(currentTime)}]
                                                </button>
                                            </div>
                                            <input
                                                type="number"
                                                step="0.5"
                                                min={startTime + 1}
                                                max={projectDuration || 3600}
                                                value={endTime}
                                                onChange={(e) => setEndTime(parseFloat(e.target.value) || startTime + 1)}
                                                className="w-full px-3 py-2 rounded-lg craft-input text-xs text-zinc-100 font-mono"
                                            />
                                            <span className="text-[10px] text-zinc-500 font-mono">{formatSeconds(endTime)}</span>
                                        </div>
                                    </div>

                                    {/* Aspect Ratio Selector */}
                                    <div className="space-y-2">
                                        <label className="text-xs text-zinc-400 font-medium">Aspect Ratio</label>
                                        <div className="grid grid-cols-3 gap-2 text-xs">
                                            <button
                                                type="button"
                                                onClick={() => setAspectRatio('9:16')}
                                                className={`p-2.5 rounded-lg border text-center transition cursor-pointer ${
                                                    aspectRatio === '9:16'
                                                        ? 'bg-zinc-800 border-zinc-600 text-zinc-100'
                                                        : 'bg-zinc-900/60 border-zinc-800/80 text-zinc-400 hover:text-zinc-200'
                                                }`}
                                            >
                                                <Smartphone className="w-3.5 h-3.5 mx-auto mb-1 text-zinc-300" />
                                                <span className="font-mono text-xs">9:16 Vertical</span>
                                            </button>

                                            <button
                                                type="button"
                                                onClick={() => setAspectRatio('16:9')}
                                                className={`p-2.5 rounded-lg border text-center transition cursor-pointer ${
                                                    aspectRatio === '16:9'
                                                        ? 'bg-zinc-800 border-zinc-600 text-zinc-100'
                                                        : 'bg-zinc-900/60 border-zinc-800/80 text-zinc-400 hover:text-zinc-200'
                                                }`}
                                            >
                                                <Monitor className="w-3.5 h-3.5 mx-auto mb-1 text-zinc-300" />
                                                <span className="font-mono text-xs">16:9 Landscape</span>
                                            </button>

                                            <button
                                                type="button"
                                                onClick={() => setAspectRatio('1:1')}
                                                className={`p-2.5 rounded-lg border text-center transition cursor-pointer ${
                                                    aspectRatio === '1:1'
                                                        ? 'bg-zinc-800 border-zinc-600 text-zinc-100'
                                                        : 'bg-zinc-900/60 border-zinc-800/80 text-zinc-400 hover:text-zinc-200'
                                                }`}
                                            >
                                                <Square className="w-3.5 h-3.5 mx-auto mb-1 text-zinc-300" />
                                                <span className="font-mono text-xs">1:1 Square</span>
                                            </button>
                                        </div>
                                    </div>

                                    {/* CTA */}
                                    <div className="pt-2 flex items-center gap-3">
                                        <button
                                            type="button"
                                            disabled={isRenderingCustom}
                                            onClick={handleRenderCustomClip}
                                            className="w-full craft-btn-primary py-2.5 px-4 rounded-lg text-xs font-medium flex items-center justify-center gap-2 cursor-pointer disabled:opacity-50"
                                        >
                                            {isRenderingCustom ? (
                                                <>
                                                    <RefreshCw className="w-3 h-3 animate-spin" />
                                                    <span>Rendering Custom Clip...</span>
                                                </>
                                            ) : (
                                                <>
                                                    <Scissors className="w-3 h-3" />
                                                    <span>Render Custom Clip ({Math.max(0, Math.round(endTime - startTime))}s)</span>
                                                </>
                                            )}
                                        </button>
                                    </div>
                                </div>
                            )}

                            {/* TAB 3: EXPORTS GALLERY */}
                            {activeTab === 'rendered' && (
                                <div className="space-y-3">
                                    {renderedClips.length > 0 ? (
                                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                                            {renderedClips.map((clip) => {
                                                const isCopiedAll = !!copiedStates[`all_${clip.id}`];

                                                return (
                                                    <div key={clip.id} className="craft-card p-3.5 rounded-xl border border-zinc-800 space-y-2.5">
                                                        <div className="aspect-[9/16] bg-black rounded-lg overflow-hidden relative group max-h-64 mx-auto border border-zinc-800/80">
                                                            {clip.meme_clip_path && (
                                                                <div className="absolute top-2 left-2 z-10 px-2 py-0.5 rounded-md bg-amber-500/90 text-white font-mono text-[10px] font-bold shadow flex items-center gap-1">
                                                                    <Flame className="w-3 h-3" />
                                                                    <span>Meme Enhanced</span>
                                                                </div>
                                                            )}
                                                            <video
                                                                src={clip.meme_clip_path || clip.clip_path}
                                                                controls
                                                                className="w-full h-full object-contain"
                                                            />
                                                        </div>
                                                        <div className="space-y-1">
                                                            <h4 className="font-medium text-xs text-zinc-200 line-clamp-1">{clip.title}</h4>
                                                            <div className="flex items-center justify-between text-[10px] font-mono text-zinc-500">
                                                                <span>{Math.round(Number(clip.duration) || 0)}s</span>
                                                                <span>{clip.meme_file_size_mb || clip.file_size_mb} MB</span>
                                                            </div>
                                                        </div>

                                                        {/* Quick Shorts Copy in Exports Gallery */}
                                                        <button
                                                            type="button"
                                                            onClick={() => copyToClipboard(getFullShortsText(clip), `all_${clip.id}`, 'Paket Shorts Lengkap (Judul + Sinopsis + Kredit + Tag)')}
                                                            className="w-full craft-btn-secondary py-1.5 rounded-lg text-xs font-medium flex items-center justify-center gap-1.5 transition cursor-pointer text-zinc-300"
                                                        >
                                                            {isCopiedAll ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3 text-zinc-400" />}
                                                            <span>{isCopiedAll ? 'Shorts Pack Copied!' : 'Copy Title & Caption'}</span>
                                                        </button>

                                                        <div className="flex items-center gap-1.5">
                                                            {clip.clip_path && (
                                                                <a
                                                                    href={clip.clip_path}
                                                                    download
                                                                    target="_blank"
                                                                    rel="noreferrer"
                                                                    className="flex-1 craft-btn-secondary py-2 rounded-lg text-xs font-medium flex items-center justify-center gap-1.5 transition cursor-pointer text-zinc-300 hover:text-white"
                                                                >
                                                                    <Download className="w-3 h-3" />
                                                                    <span>Clean</span>
                                                                </a>
                                                            )}

                                                            {clip.meme_clip_path && (
                                                                <a
                                                                    href={clip.meme_clip_path}
                                                                    download
                                                                    target="_blank"
                                                                    rel="noreferrer"
                                                                    className="flex-1 py-2 rounded-lg text-xs font-medium flex items-center justify-center gap-1.5 transition cursor-pointer bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-600 hover:to-orange-600 text-white font-sans"
                                                                >
                                                                    <Flame className="w-3 h-3" />
                                                                    <span>Meme Video</span>
                                                                </a>
                                                            )}
                                                        </div>
                                                    </div>
                                                );
                                            })}
                                        </div>
                                    ) : (
                                        <div className="craft-card p-8 text-center text-zinc-500 text-xs rounded-xl">
                                            No rendered clips yet. Click "Render 9:16 Short" on any highlight card.
                                        </div>
                                    )}
                                </div>
                            )}

                        </div>

                    </div>
                )}

            </main>
        </div>
    );
}

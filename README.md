# Video Transcript

[English](#english) | [中文](#chinese)

---

## English

A Python tool to extract transcripts from YouTube, Bilibili, and local video files.

### Features

- **Online videos** — extract subtitles from YouTube and Bilibili with one command
- **Local files** — transcribe local videos with faster-whisper (Chinese/English)
- **CLI + Web UI** — command line for quick use, Gradio UI for browsing
- **Multiple formats** — output as TXT, SRT, or JSON

### Install

```bash
pip install -e .
# Requires ffmpeg installed on your system
# macOS: brew install ffmpeg
# Ubuntu: apt install ffmpeg
```

### CLI Usage

```bash
# Online video
transcript get "https://www.youtube.com/watch?v=xxx"
transcript get "https://www.bilibili.com/video/BV1xx" --lang zh --format srt

# Local file
transcript get ~/Videos/lecture.mp4

# List available subtitles
transcript list "https://www.youtube.com/watch?v=xxx"

# Save to file
transcript get "https://youtube.com/watch?v=xxx" -o notes.txt
```

### Web UI

```bash
python -m transcript.web
# Open http://127.0.0.1:7860
```

### Dependencies

- yt-dlp (online subtitle download)
- faster-whisper (local ASR)
- gradio (web UI)
- click (CLI)
- ffmpeg (system dependency)

### License

MIT

---

## Chinese

一个从 YouTube、Bilibili 和本地视频文件中提取逐字稿的 Python 工具。

### 功能

- **在线视频** — 一条命令提取 YouTube 和 B站的 CC 字幕 / 自动字幕
- **本地文件** — 使用 faster-whisper 对本地视频进行语音转写（中英文）
- **CLI + Web UI** — 命令行快速使用，Gradio 界面方便浏览
- **多格式输出** — 支持 TXT、SRT、JSON

### 安装

```bash
pip install -e .
# 需要系统安装 ffmpeg
# macOS: brew install ffmpeg
# Ubuntu: apt install ffmpeg
```

### CLI 使用

```bash
transcript get "https://www.bilibili.com/video/BV1xx" --lang zh --format srt
transcript get ~/Videos/lecture.mp4
transcript list "https://www.youtube.com/watch?v=xxx"
transcript get "https://youtube.com/watch?v=xxx" -o notes.txt
```

### Web UI

```bash
python -m transcript.web
# 打开 http://127.0.0.1:7860
```

### 依赖

- yt-dlp
- faster-whisper
- gradio
- click
- ffmpeg（系统依赖）

### License

MIT

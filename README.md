# Sansky AI Editor

Production-quality AI-powered desktop application that automates repetitive gaming video editing tasks while integrating with Adobe Premiere Pro.

## Features (Planned)
- Automate gaming video editing.
- Detect highlights.
- Generate subtitles locally.
- Prepare Premiere Pro timelines.
- Export optimized Shorts.

## Tech Stack
- **Language**: Python 3.12+
- **Video Processing**: FFmpeg
- **Computer Vision**: OpenCV
- **Speech Recognition**: OpenAI Whisper (Local)
- **Machine Learning**: PyTorch, NumPy
- **Editing**: Adobe Premiere Pro

## Architecture
This project follows SOLID principles, single responsibility, and composition over inheritance. 
- `app/`: High-level application logic (bootstrap, workflows, etc.).
- `core/`: Core infrastructure (config, DI, logger, events).
- `engines/`: Specific independent subsystems (video, ai, captions, premiere).
- `data/` and `assets/`: File and media storage.

## Development

Install dependencies:
```bash
pip install -r requirements.txt
```

Run the application:
```bash
python main.py
```

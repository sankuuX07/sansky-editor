# Sansky AI Editor

Sansky AI Editor is a production-grade desktop application that fully automates the creation of professional gaming Highlights and YouTube Shorts, directly integrating with Adobe Premiere Pro.

## Features
- **Video Processing Engine**: Extracts audio streams and visual characteristics from massive raw gameplay files.
- **Whisper Speech Intelligence Engine**: Generates highly accurate raw speech transcription from gaming audio.
- **Caption Engine**: Transforms raw text into visually stunning, stylized subtitling metadata.
- **Highlight Detection Engine**: Programmatically scrubs hours of footage to select the most engaging, action-packed moments.
- **Premiere Automation Engine**: Bridges python logic directly to Adobe Premiere Pro.
- **One-Click Shorts Generator**: The flagship orchestrator that triggers all systems above via an asynchronous DAG.

## Quickstart

```python
import asyncio
from pathlib import Path

from app.services.engine_manager import EngineManager
from app.scheduler.task_manager import TaskManager
from engines.automation_engine.automation_engine import AutomationEngine
from engines.shorts_generator_engine.shorts_generator_engine import ShortsGeneratorEngine

# Initialize core architecture
engine_manager = EngineManager()
task_manager = TaskManager(max_workers=4)
task_manager.start_workers()

automation = AutomationEngine(engine_manager, task_manager)
engine_manager.register(automation)

shorts_generator = ShortsGeneratorEngine(automation)
engine_manager.register(shorts_generator)

# Start all subsystems
engine_manager.initialize_all()
engine_manager.start_all()

# Generate a YouTube Short
async def run():
    video = Path("./raw_footage/gameplay_01.mp4")
    result = await shorts_generator.generate_shorts([video])
    print(f"Generated Project: {result.projects[0].premiere_project_path}")

asyncio.run(run())
```

## Architecture
The application is strictly designed following SOLID principles and utilizes Dependency Injection to isolate engines. An overarching `EngineManager` acts as the DI Container, while the `AutomationEngine` manages parallel `TaskManager` queues to process complex computational graphs.

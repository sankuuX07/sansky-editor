# Known Limitations (Version 1.0.0)

While Version 1.0 of the Sansky AI Editor is production-ready, the following limitations are present by design and will be expanded upon in future releases:

1. **Premiere Pro Dependency**: The `PremiereAutomationEngine` requires Adobe Premiere Pro to be installed and accessible. It does not replace the renderer; it generates project structures via API bindings.
2. **GPU Acceleration**: Whisper speech transcription operates synchronously. While the queue protects the CPU, environments lacking dedicated NVIDIA GPUs (CUDA) will experience severe execution delays during the `transcribe` step.
3. **Aspect Ratio Support**: The `ShortsGeneratorEngine` currently hardcodes the `TimelinePreparationManager` output configuration to vertical `1080x1920` (9:16). Horizontal videos will be center-cropped unless manually adjusted inside Premiere.
4. **Cloud Scalability**: The `EngineManager` operates entirely locally. To distribute compute across a network in future updates, the `EventBus` must be refactored to support Redis/RabbitMQ.

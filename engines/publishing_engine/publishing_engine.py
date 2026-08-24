"""
Publishing Engine for M18.
Handles generating metadata, validating export profiles, and launching isolated FFmpeg exports.
"""
import logging
import json
import uuid
import asyncio
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple

from engines.base_engine import BaseEngine
from core.models.shared_types import EngineStatus
from core.models.publishing_models import (
    PublishingProject, ExportTarget, PlatformExportProfile, ExportStatus
)
from engines.creator_intelligence_engine.creator_intelligence_engine import CreatorIntelligenceEngine
from core.models.creator_models import CreatorIntelligenceReport
from core.models.shorts_models import ShortsProject

class PublishingEngine(BaseEngine):
    def __init__(self, library_engine=None):
        super().__init__("publishing_engine")
        self.library_engine = library_engine
        self.creator_engine = CreatorIntelligenceEngine()
        
        # Predefined Profiles
        self.profiles = [
            PlatformExportProfile("YOUTUBE", "YouTube Video", "16:9", 1920, 1080),
            PlatformExportProfile("SHORTS", "YouTube Shorts", "9:16", 1080, 1920, max_duration=60.0),
            PlatformExportProfile("INSTAGRAM", "Instagram Reel", "9:16", 1080, 1920, max_duration=90.0),
            PlatformExportProfile("CUSTOM", "Custom", "16:9", 1920, 1080)
        ]

    def initialize(self) -> None:
        self._status = EngineStatus.INITIALIZING
        self.logger.info("Initializing Publishing Engine...")
        self._status = EngineStatus.UNINITIALIZED
        self.is_initialized = True

    def get_profiles(self) -> List[PlatformExportProfile]:
        return self.profiles

    def validate_profile(self, target: ExportTarget, source_metadata: Dict) -> Tuple[bool, str]:
        """Validates if the source video can be exported using the target profile."""
        if target.profile.max_duration and source_metadata.get('duration', 0) > target.profile.max_duration:
            return False, f"Source duration exceeds maximum allowed for {target.profile.name}."
            
        source_ar = source_metadata.get('aspect_ratio', '16:9')
        if source_ar != target.profile.aspect_ratio:
            return True, f"Aspect ratio conversion required: Source ({source_ar}) to Target ({target.profile.aspect_ratio})."
            
        return True, "Valid"

    def generate_metadata(self, project_path: str) -> Optional[CreatorIntelligenceReport]:
        """Regenerates or fetches M14 creator metadata based on the original project."""
        p = Path(project_path)
        report_path = p.parent / "content_strategy_report.json"
        
        if report_path.exists():
            try:
                with open(report_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                report = CreatorIntelligenceReport(
                    job_id=data.get('job_id', ''),
                    best_candidate_id=data.get('best_candidate_id'),
                    best_candidate_reason=data.get('best_candidate_reason', ''),
                    title_suggestions=data.get('title_suggestions', []),
                    description_suggestion=data.get('description_suggestion', ''),
                    hashtags=data.get('hashtags', []),
                    recommended_thumbnail=data.get('recommended_thumbnail')
                )
                return report
            except Exception as e:
                self.logger.error(f"Error reading existing CI report: {e}")
                
        # If no report, we'd theoretically run CreatorIntelligenceEngine.analyze_project
        # For this prototype, we'll return a mock if it doesn't exist
        return CreatorIntelligenceReport(
            job_id="unknown",
            title_suggestions=["Generated Highlight", "Epic Moment!"],
            description_suggestion="Check out this awesome gameplay highlight!",
            hashtags=["#Gaming", "#Highlight"]
        )

    async def export_package(self, publishing_project: PublishingProject, source_video_path: Path, output_dir: Path):
        """Asynchronously exports all targets in the publishing project."""
        publishing_project.status = ExportStatus.PROCESSING
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save overarching metadata
        pub_meta_path = output_dir / "publishing_summary.json"
        
        tasks = []
        for target in publishing_project.export_targets:
            tasks.append(self._export_single_target(target, source_video_path, output_dir))
            
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        any_success = False
        all_success = True
        
        for i, res in enumerate(results):
            target = publishing_project.export_targets[i]
            if isinstance(res, Exception):
                target.status = ExportStatus.FAILED
                target.error_message = str(res)
                all_success = False
            else:
                if target.status == ExportStatus.COMPLETED:
                    any_success = True
                else:
                    all_success = False
                    
        if all_success:
            publishing_project.status = ExportStatus.COMPLETED
        elif any_success:
            publishing_project.status = ExportStatus.COMPLETED # Partial success, UI will show specific errors
        else:
            publishing_project.status = ExportStatus.FAILED
            
        # Update summary
        try:
            import dataclasses
            with open(pub_meta_path, 'w', encoding='utf-8') as f:
                json.dump(dataclasses.asdict(publishing_project), f, default=str, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to write publishing summary: {e}")

    async def _export_single_target(self, target: ExportTarget, source_path: Path, base_output_dir: Path):
        """Exports a single platform target using FFmpeg."""
        target.status = ExportStatus.PROCESSING
        target.progress = 0.0
        
        target_dir = base_output_dir / target.profile.platform.lower()
        target_dir.mkdir(parents=True, exist_ok=True)
        
        output_video = target_dir / f"video.{target.profile.container}"
        
        # Build FFmpeg command (Scale & Crop to fit target aspect ratio)
        # Using a simple scale/crop approach for demonstration
        vf_str = f"scale={target.profile.width}:{target.profile.height}:force_original_aspect_ratio=increase,crop={target.profile.width}:{target.profile.height}"
        
        cmd = [
            "ffmpeg", "-y", "-i", str(source_path),
            "-vf", vf_str,
            "-c:v", target.profile.video_codec,
            "-c:a", target.profile.audio_codec,
        ]
        
        if target.profile.fps:
            cmd.extend(["-r", str(target.profile.fps)])
            
        cmd.append(str(output_video))
        
        try:
            import subprocess
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Simple progress simulation
            target.progress = 50.0
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                target.status = ExportStatus.FAILED
                target.error_message = f"FFmpeg error: {stderr.decode()}"
                return
                
            target.progress = 90.0
            
            # Write metadata.json for this specific export
            meta_path = target_dir / "metadata.json"
            meta_data = {
                "platform": target.profile.platform,
                "title": target.title,
                "description": target.description,
                "hashtags": target.hashtags,
                "thumbnail": target.thumbnail_path,
                "export_date": datetime.now().isoformat()
            }
            with open(meta_path, 'w', encoding='utf-8') as f:
                json.dump(meta_data, f, indent=2)
                
            # Copy thumbnail if exists
            if target.thumbnail_path:
                thumb_src = Path(target.thumbnail_path)
                if thumb_src.exists():
                    import shutil
                    shutil.copy2(thumb_src, target_dir / thumb_src.name)
            
            target.output_path = str(target_dir)
            target.progress = 100.0
            target.status = ExportStatus.COMPLETED
            
        except Exception as e:
            target.status = ExportStatus.FAILED
            target.error_message = str(e)
            raise e

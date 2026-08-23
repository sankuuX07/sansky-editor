import logging
import json
from pathlib import Path
from core.models.creator_models import ContentCandidate, HookAnalysis, PlatformSuitability, CreatorIntelligenceReport
from core.models.shorts_models import ShortsProject
from core.models.preference_models import UserEditingProfile

logger = logging.getLogger(__name__)

class CreatorIntelligenceEngine:
    """
    Analyzes generated shorts projects to provide platform, title, description, and thumbnail recommendations
    grounded in actual evidence (events, edits, composition).
    """
    def __init__(self):
        pass

    def analyze_project(self, project: ShortsProject, pref_profile: UserEditingProfile = None) -> CreatorIntelligenceReport:
        report = CreatorIntelligenceReport(job_id=project.project_id)
        
        if not project.clips:
            return report
            
        candidates = []
        for clip in project.clips:
            duration = clip.end_time - clip.start_time
            has_caps = bool(clip.captions)
            has_thumb = bool(getattr(clip, 'thumbnail_path', None))
            event_cnt = len(clip.events_contained) if clip.events_contained else 0
            
            # Hook Analysis
            # Did an important event happen in the first 3 seconds?
            hook_activity = "Low"
            recommendation = "Consider trimming the beginning if there is dead space."
            first_event_time = 0.0
            
            if clip.events_contained:
                for ev in clip.events_contained:
                    if hasattr(ev, 'start_time'):
                        rel_time = ev.start_time - clip.start_time
                        if 0 <= rel_time <= 3.0:
                            hook_activity = "High"
                            recommendation = "Strong opening for short-form content."
                            first_event_time = rel_time
                            break
                        elif first_event_time == 0.0 or rel_time < first_event_time:
                            first_event_time = rel_time
            
            hook = HookAnalysis(first_meaningful_event_time=first_event_time, 
                                opening_activity=hook_activity, 
                                recommendation=recommendation)
            
            # Ranking Score calculation
            score = clip.score * 0.3 # 30% Engagement
            score += (event_cnt * 5) # 5 points per event
            if 15 <= duration <= 60:
                score += 20 # Suitable duration for shorts
            if has_caps:
                score += 10 # Captions are good for shorts
                
            # M13 Preference influence on ranking (if preference is action heavy, prefer high event count)
            if pref_profile:
                if pref_profile.action_intensity_preference > 0.6 and event_cnt >= 2:
                    score += 10
            
            candidate = ContentCandidate(
                id=clip.clip_id,
                duration=duration,
                engagement_score=clip.score,
                events_count=event_cnt,
                has_captions=has_caps,
                composition_ratio=project.settings.target_aspect_ratio,
                has_thumbnail=has_thumb,
                hook_analysis=hook,
                ranking_score=score
            )
            candidates.append(candidate)
            
        # Rank them
        candidates.sort(key=lambda x: x.ranking_score, reverse=True)
        report.candidates = candidates
        
        best = candidates[0]
        report.best_candidate_id = best.id
        report.best_candidate_reason = f"Ranked highest based on engagement score ({best.engagement_score:.1f}), {best.events_count} important events, and strong short-form duration."
        
        # Platform Suitability based on properties
        platforms = []
        is_vertical = project.settings.target_aspect_ratio == "9:16"
        is_short = 10 <= best.duration <= 60
        
        # YouTube Shorts
        yt_reason = "Vertical format and duration compatible." if (is_vertical and is_short) else "May not be optimal (needs vertical 9:16 and <60s)."
        platforms.append(PlatformSuitability("YouTube Shorts", (is_vertical and is_short), yt_reason))
        
        # Instagram Reels
        ig_reason = "Short duration and vertical format." if (is_vertical and is_short) else "Reels perform best under 60s and in 9:16."
        platforms.append(PlatformSuitability("Instagram Reels", (is_vertical and is_short), ig_reason))
        
        # TikTok
        tk_reason = "Vertical format and dynamic action." if is_vertical else "Requires 9:16 format."
        platforms.append(PlatformSuitability("TikTok", is_vertical, tk_reason))
        
        report.platform_suitability = platforms
        
        # Title Generation
        best_clip = next((c for c in project.clips if c.clip_id == best.id), None)
        titles = []
        if best_clip and best_clip.events_contained:
            event_types = [getattr(e, 'event_type', '').lower() for e in best_clip.events_contained]
            if any("kill" in t or "elimination" in t for t in event_types):
                titles.append("Clean Finish! 🔥")
                titles.append("Perfect Timing for the Elimination")
                
            if any("damage" in t or "fight" in t for t in event_types):
                titles.append("Intense Fight Under Pressure 😱")
                
            if "high_motion" in event_types:
                titles.append("Crazy Action Moment 🚀")
                
        if not titles:
            titles = ["Epic Gameplay Highlight", "You Won't Believe This Moment!"]
            
        report.title_suggestions = titles
        report.description_suggestion = "An intense gameplay moment edited automatically using Sansky AI Editor."
        
        # Hashtags
        report.hashtags = ["#Gaming", "#Gameplay", "#GamingHighlights", "#Shorts"]
        
        # Thumbnail
        if best.has_thumbnail:
            # We assume best clip thumb is best.
            report.recommended_thumbnail = best_clip.thumbnail_path.name if best_clip.thumbnail_path else None
            report.thumbnail_reason = "Highest engagement score and relevant event context."
            
        self._write_report(project, report)
        return report
        
    def _write_report(self, project: ShortsProject, report: CreatorIntelligenceReport):
        if not project.premiere_project_path: return
        out_path = project.premiere_project_path.parent / "content_strategy_report.json"
        
        def to_dict(obj):
            import dataclasses
            if dataclasses.is_dataclass(obj):
                return {k: to_dict(v) for k, v in dataclasses.asdict(obj).items()}
            elif isinstance(obj, list):
                return [to_dict(i) for i in obj]
            else:
                return obj
                
        try:
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(to_dict(report), f, indent=4)
        except Exception as e:
            logger.error(f"Failed to write content strategy report: {e}")

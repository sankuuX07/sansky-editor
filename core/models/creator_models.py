from dataclasses import dataclass, field
from typing import List, Dict, Optional

@dataclass
class HookAnalysis:
    first_meaningful_event_time: float
    opening_activity: str  # e.g., "High", "Low"
    recommendation: str

@dataclass
class PlatformSuitability:
    platform: str
    suitable: bool
    reason: str

@dataclass
class ContentCandidate:
    id: str
    duration: float
    engagement_score: float
    events_count: int
    has_captions: bool
    composition_ratio: str
    has_thumbnail: bool
    hook_analysis: HookAnalysis
    ranking_score: float = 0.0

@dataclass
class CreatorIntelligenceReport:
    job_id: str
    best_candidate_id: Optional[str] = None
    best_candidate_reason: str = ""
    candidates: List[ContentCandidate] = field(default_factory=list)
    platform_suitability: List[PlatformSuitability] = field(default_factory=list)
    title_suggestions: List[str] = field(default_factory=list)
    description_suggestion: str = ""
    hashtags: List[str] = field(default_factory=list)
    recommended_thumbnail: Optional[str] = None
    thumbnail_reason: str = ""

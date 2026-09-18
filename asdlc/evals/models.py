from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class EvaluationTier(str, Enum):
    TIER_1_STATIC = "Tier 1: 静的構造・スキーマ検証 (Static & Schema)"
    TIER_2_BEHAVIOR = "Tier 2: 行動・軌跡決定論的検証 (Behavior & Trajectory)"
    TIER_3_RUBRIC = "Tier 3: ルーブリック品質・具体性評価 (Rubric & Actionability)"

class EvalStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    WARN = "WARN"

class EvaluationItemResult(BaseModel):
    item_id: str
    target_type: str # "skill", "agent", "rule", "workflow", "orchestrator"
    tier: EvaluationTier
    status: EvalStatus
    score: float = Field(ge=0.0, le=100.0)
    details: str
    recommendations: List[str] = Field(default_factory=list)

class TierSummary(BaseModel):
    tier: EvaluationTier
    total_checks: int
    passed_checks: int
    failed_checks: int
    average_score: float

class OverallEvaluationReport(BaseModel):
    timestamp: str
    overall_asqs_score: float = Field(ge=0.0, le=100.0)
    overall_verdict: EvalStatus
    tier_summaries: List[TierSummary]
    item_results: List[EvaluationItemResult]
    summary_message: str

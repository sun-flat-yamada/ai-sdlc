from enum import Enum
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime

class Phase(str, Enum):
    PHASE_1_REQUIREMENTS = "phase_1_requirements"         # 要件定義
    PHASE_2_BASIC_DESIGN = "phase_2_basic_design"         # 基本設計 (ADR)
    PHASE_3_DETAIL_DESIGN = "phase_3_detail_design"       # 詳細設計 (API, Schema, Setup)
    PHASE_4_ITERATION = "phase_4_iteration"               # 反復開発・実装 (TDD, Coding, PR)
    PHASE_5_INTEGRATION_TEST = "phase_5_integration_test" # 結合テスト (E2E, 負荷)
    PHASE_6_PRODUCTION_RELEASE = "phase_6_production_release" # 本番リリース
    PHASE_7_MAINTENANCE = "phase_7_maintenance"           # 保守運用

class ReviewVerdict(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    CONDITIONAL_PASS = "CONDITIONAL_PASS"

class MeisterType(str, Enum):
    THREAT_DEFENSE = "Threat Defense Meister (脅威防壁・セキュリティ)"
    REQUIREMENT_FULFILLMENT = "Requirement Fulfillment Meister (要件充足・完全性)"
    PRAGMATIC_OPERATIONS = "Pragmatic Operations Meister (実務運用・実行可能性)"
    QUALITY_ASSURANCE = "Quality Assurance Meister (品質保証・検証可能性)"
    GOVERNANCE_COMPLIANCE = "Governance Compliance Meister (規律統制・説明責任)"
    VALUE_PROPOSITION = "Value Proposition Meister (提供価値・競争優位)"
    ISOLATION_ARCHITECTURE = "Isolation Architecture Meister (隔離構造・疎結合設計)"

class MeisterScore(BaseModel):
    meister: MeisterType
    score: int = Field(ge=0, le=100, description="100点満点評価")
    verdict: ReviewVerdict
    critique: str = Field(description="採点根拠と懸念点")
    recommendations: List[str] = Field(default_factory=list, description="具体的改善指示")

class MeisterEvaluation(BaseModel):
    document_name: str
    phase: Phase
    timestamp: datetime = Field(default_factory=datetime.now)
    total_score: float = Field(ge=0, le=100)
    min_score: int = Field(ge=0, le=100)
    verdict: ReviewVerdict
    meister_scores: List[MeisterScore]
    summary: str
    remediation_required: bool
    charter_ref: str = "docs/charter/MEISTERS_CHARTER.md"

# Issue Triage Models
class IssueType(str, Enum):
    BUG = "bug"
    FEATURE = "feature"
    REFACTOR = "refactor"
    SECURITY = "security"
    QUESTION = "question"
    CHORE = "chore"

class IssuePriority(str, Enum):
    P0_CRITICAL = "P0 (Critical/Blocker)"
    P1_HIGH = "P1 (High)"
    P2_MEDIUM = "P2 (Medium)"
    P3_LOW = "P3 (Low)"

class IssueTriageResult(BaseModel):
    issue_id: Optional[str] = None
    title: str
    sanitized_body: str
    prompt_injection_detected: bool = False
    injection_warnings: List[str] = Field(default_factory=list)
    issue_type: IssueType
    priority: IssuePriority
    estimated_component: str
    suggested_labels: List[str] = Field(default_factory=list)
    missing_information: List[str] = Field(default_factory=list)
    remediation_proposal: str
    recommended_assignee_role: str
    matched_adrs_or_specs: List[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.now)

class SDLCArtifact(BaseModel):
    name: str
    phase: Phase
    path: str
    content_hash: str
    last_modified: datetime = Field(default_factory=datetime.now)
    approved_by: Optional[str] = None

class SDLCState(BaseModel):
    project_name: str
    current_phase: Phase = Phase.PHASE_1_REQUIREMENTS
    completed_phases: List[Phase] = Field(default_factory=list)
    artifacts: Dict[str, SDLCArtifact] = Field(default_factory=dict)
    reviews: List[MeisterEvaluation] = Field(default_factory=list)
    triages: List[IssueTriageResult] = Field(default_factory=list)
    audit_trail: List[Dict[str, Any]] = Field(default_factory=list)

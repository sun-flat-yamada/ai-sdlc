import json
import hashlib
from pathlib import Path
from typing import Optional, Dict, Any
from .models import (
    Phase,
    SDLCState,
    SDLCArtifact,
    ReviewVerdict,
    MeisterEvaluation,
    IssueTriageResult
)
from .agents.procedural import ProceduralAgent
from .agents.qa import QAAgent
from .agents.coding import CodingAgent
from .triage.engine import IssueAutoTriageEngine
from .audit.bridge import AegisAuditBridge

class SDLCOrchestrator:
    """
    ASDLC ライフサイクル統合オーケストレーター
    """

    def __init__(self, project_dir: str = "."):
        self.project_dir = Path(project_dir)
        self.state_file = self.project_dir / ".asdlc_state.json"
        self.procedural = ProceduralAgent()
        self.qa = QAAgent()
        self.coding = CodingAgent()
        self.triage_engine = IssueAutoTriageEngine()
        self.audit_bridge = AegisAuditBridge(project_dir=self.project_dir)
        self.state = self._load_or_init_state()

    def _load_or_init_state(self) -> SDLCState:
        if self.state_file.exists():
            try:
                with open(self.state_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return SDLCState(**data)
            except Exception:
                pass
        return SDLCState(project_name=self.project_dir.name)

    def save_state(self):
        with open(self.state_file, "w", encoding="utf-8") as f:
            json.dump(self.state.model_dump(mode="json"), f, indent=2, ensure_ascii=False)

    def triage_issue(self, title: str, body: str, issue_id: Optional[str] = None) -> IssueTriageResult:
        redacted_title, _ = self.audit_bridge.redact_text(title)
        redacted_body, redacts = self.audit_bridge.redact_text(body)

        result = self.triage_engine.triage(redacted_title, redacted_body, issue_id)
        self.state.triages.append(result)
        
        audit_entry = {
            "action": "triage_issue",
            "title": redacted_title,
            "type": result.issue_type.value,
            "priority": result.priority.value
        }
        if redacts:
            audit_entry["redactions_applied"] = redacts

        self.state.audit_trail.append(audit_entry)
        self.audit_bridge.record_lifecycle_event(
            action="triage_issue",
            details=audit_entry,
            phase=self.state.current_phase.value
        )
        self.save_state()
        return result

    def register_artifact(self, name: str, content: str) -> SDLCArtifact:
        art_path = self.project_dir / name
        with open(art_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        h = hashlib.sha256(content.encode("utf-8")).hexdigest()
        artifact = SDLCArtifact(
            name=name,
            phase=self.state.current_phase,
            path=str(art_path),
            content_hash=h
        )
        self.state.artifacts[name] = artifact
        audit_entry = {
            "action": "register_artifact",
            "artifact": name,
            "phase": self.state.current_phase.value,
            "content_hash": h
        }
        self.state.audit_trail.append(audit_entry)
        self.audit_bridge.record_lifecycle_event(
            action="register_artifact",
            details=audit_entry,
            phase=self.state.current_phase.value
        )
        self.save_state()
        return artifact

    def review_artifact(self, artifact_name: str, deterministic_only: bool = False) -> MeisterEvaluation:
        art_path = self.project_dir / artifact_name
        if not art_path.exists():
            raise FileNotFoundError(f"成果物が見つかりません: {artifact_name}")
        
        with open(art_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()

        from .review.engine import DeterministicCodeReviewer
        if DeterministicCodeReviewer.is_source_code(artifact_name):
            eval_result = self.qa.evaluate_code(
                code_path=artifact_name,
                code_content=content,
                phase=self.state.current_phase,
                deterministic_only=deterministic_only
            )
        else:
            eval_result = self.qa.evaluate_document(
                document_name=artifact_name,
                document_content=content,
                phase=self.state.current_phase
            )
        self.state.reviews.append(eval_result)
        
        audit_entry = {
            "action": "review_artifact",
            "artifact": artifact_name,
            "verdict": eval_result.verdict.value,
            "total_score": eval_result.total_score,
            "min_score": eval_result.min_score
        }
        self.state.audit_trail.append(audit_entry)
        self.audit_bridge.record_lifecycle_event(
            action="review_artifact",
            details=audit_entry,
            phase=self.state.current_phase.value,
            verdict_status=eval_result.verdict.value,
            planning_evidence={
                "path": artifact_name,
                "hash": str(eval_result.total_score),
                "status": eval_result.verdict.value
            }
        )
        self.save_state()
        return eval_result

    def review_code(
        self,
        code_path: str,
        lang: Optional[str] = None,
        deterministic_only: bool = False
    ) -> MeisterEvaluation:
        """ソースコード直接審査インターフェース"""
        art_path = Path(code_path)
        if not art_path.is_absolute():
            art_path = self.project_dir / code_path
        if not art_path.exists():
            raise FileNotFoundError(f"コードファイルが見つかりません: {code_path}")

        with open(art_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()

        eval_result = self.qa.evaluate_code(
            code_path=str(art_path),
            code_content=content,
            lang=lang,
            phase=self.state.current_phase,
            deterministic_only=deterministic_only
        )
        self.state.reviews.append(eval_result)
        
        audit_entry = {
            "action": "review_code",
            "code_path": str(art_path),
            "verdict": eval_result.verdict.value,
            "total_score": eval_result.total_score,
            "min_score": eval_result.min_score
        }
        self.state.audit_trail.append(audit_entry)
        self.audit_bridge.record_lifecycle_event(
            action="review_code",
            details=audit_entry,
            phase=self.state.current_phase.value,
            verdict_status=eval_result.verdict.value,
            verification_evidence={
                "path": str(art_path),
                "hash": str(eval_result.total_score),
                "tests_passed": eval_result.verdict == ReviewVerdict.PASS
            }
        )
        self.save_state()
        return eval_result

    def advance_phase(self) -> Dict[str, Any]:
        # Aegis 監査ログ完全性検証
        is_ok, count, err = self.audit_bridge.verify_integrity()
        audit_integrity_result = {
            "is_valid": is_ok,
            "count": count,
            "error": err
        }

        check = self.procedural.check_guardrails(
            self.state,
            self.state.current_phase,
            audit_integrity_result=audit_integrity_result
        )
        if check["is_blocked"]:
            return {
                "success": False,
                "current_phase": self.state.current_phase,
                "reasons": check["block_reasons"]
            }
        
        phases = list(Phase)
        idx = phases.index(self.state.current_phase)
        if idx < len(phases) - 1:
            prev_phase = self.state.current_phase
            self.state.completed_phases.append(self.state.current_phase)
            self.state.current_phase = phases[idx + 1]
            self.save_state()

            self.audit_bridge.record_lifecycle_event(
                action="advance_phase",
                details={
                    "previous_phase": prev_phase.value,
                    "new_phase": self.state.current_phase.value
                },
                phase=self.state.current_phase.value
            )

            return {
                "success": True,
                "new_phase": self.state.current_phase,
                "info": self.procedural.get_phase_info(self.state.current_phase)
            }
        return {
            "success": True,
            "message": "すべてのSDLCフェーズが完了しました！"
        }


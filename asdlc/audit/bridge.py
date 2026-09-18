"""
ASDLC Aegis Audit Bridge
Integrates ASDLC lifecycle events transparently with Agent Aegis Harness (aah).
Enforces Merkle Hash Chain sealing, secret redaction, and tampering defense.
"""
from __future__ import annotations

import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Graceful import of agent-aegis-harness
try:
    from aegis.models import (
        AegisAuditEvent,
        AuditReproducibility,
        ClientToolType,
        EnvironmentInfo,
        TriggerContext,
        RetrievalContext,
        InferenceTrace,
        ActionPayload,
        ToolCallRecord,
        SentinelVerdict,
        VerdictStatus,
        IntegrityProof,
        PlanningEvidence,
        VerificationEvidence,
    )
    from aegis.sentinel.redactor import SensitiveRedactor
    from aegis.sentinel.judge import SentinelJudge
    from aegis.archivist.integrity import HashChainManager
    from aegis.recorder.tracer import AegisRecorder
    HAS_AEGIS = True
except ImportError:
    HAS_AEGIS = False


class AegisAuditBridge:
    """
    asdlc 実行環境において、利用側プロジェクトで透過的に aah を稼働させるアダプタ
    """

    def __init__(
        self,
        project_dir: Path | str = ".",
        enabled: bool = True,
        enable_wal: bool = False
    ):
        self.project_dir = Path(project_dir).resolve()
        
        # asdlc SDK 自身の開発リポジトリに対するプロト適用を厳格に抑止
        # ユーザー指示: "aah の開発者は私であり、このリポジトリへのプロト適用はするな。"
        is_asdlc_self_repo = (
            (self.project_dir / "asdlc").is_dir()
            and (self.project_dir / "pyproject.toml").is_file()
            and 'name = "asdlc"' in (self.project_dir / "pyproject.toml").read_text(encoding="utf-8", errors="ignore")
        )

        self.enabled = enabled and HAS_AEGIS and not is_asdlc_self_repo
        self.aegis_dir = self.project_dir / ".aegis"
        self.logs_dir = self.aegis_dir / "logs"
        self.audit_trail_path = self.logs_dir / "audit-trail.jsonl"
        self.forensic_trail_path = self.logs_dir / "forensic-trail.jsonl"

        
        self.redactor = SensitiveRedactor() if HAS_AEGIS else None
        self.judge = SentinelJudge() if HAS_AEGIS else None
        self._recorder: Optional[Any] = None
        self.step_index = 0
        self.session_id = f"asdlc_{uuid.uuid4().hex[:8]}"

    @classmethod
    def is_aegis_available(cls) -> bool:
        """agent-aegis-harness が利用可能か"""
        return HAS_AEGIS

    @property
    def recorder(self) -> Optional[Any]:
        """AegisRecorder を遅延初期化（必要時にディレクトリ作成）"""
        if not self.enabled:
            return None
        if self._recorder is None:
            self.logs_dir.mkdir(parents=True, exist_ok=True)
            self._recorder = AegisRecorder(
                audit_trail_path=self.audit_trail_path,
                forensic_trail_path=self.forensic_trail_path,
                enable_wal=False,  # 独立性担保のためWALは無効（またはプロジェクト内）
                session_id=self.session_id,
            )
        return self._recorder

    def redact_text(self, text: str) -> Tuple[str, List[str]]:
        """機微情報（APIキー、シークレット、PII）の透過的自動マスキング"""
        if not self.enabled or self.redactor is None:
            return text, []
        return self.redactor.redact_text(text)

    def inspect_command(self, command_line: str) -> Dict[str, Any]:
        """Sentinel によるコマンド実行前即時検閲 (Tier 1 AST & Regex)"""
        if not self.enabled or self.judge is None:
            return {"allowed": True, "verdict": "PASS", "violations": []}

        verdict = self.judge.evaluate_tool_call(
            tool_name="run_command",
            arguments={"CommandLine": command_line},
            step_index=self.step_index + 1
        )
        is_blocked = verdict.status.value == "BLOCK"
        violations = [{"rule_id": v.rule_id, "message": v.message} for v in verdict.violations]
        return {
            "allowed": not is_blocked,
            "verdict": verdict.status.value,
            "score": verdict.score,
            "violations": violations
        }

    def record_lifecycle_event(
        self,
        action: str,
        details: Dict[str, Any],
        phase: Optional[str] = None,
        verdict_status: str = "PASS",
        planning_evidence: Optional[Dict[str, Any]] = None,
        verification_evidence: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        ライフサイクルイベントを 5W1H 構造化データとして Merkle Hash Chain に封印記録
        """
        if not self.enabled or self.recorder is None:
            return None

        self.step_index += 1
        sanitized_details, applied_redactions = self.redact_text(str(details))

        # PlanningEvidence 変換
        plan_ev = None
        if planning_evidence:
            plan_ev = PlanningEvidence(
                plan_artifact_path=planning_evidence.get("path"),
                plan_hash_digest=planning_evidence.get("hash"),
                plan_status=planning_evidence.get("status")
            )

        # VerificationEvidence 変換
        verif_ev = None
        if verification_evidence:
            verif_ev = VerificationEvidence(
                walkthrough_path=verification_evidence.get("path"),
                walkthrough_digest=verification_evidence.get("hash"),
                tests_passed=verification_evidence.get("tests_passed")
            )

        # 判定ステータス
        status_enum = VerdictStatus.PASS
        if verdict_status == "WARN":
            status_enum = VerdictStatus.WARN
        elif verdict_status in ("BLOCK", "FAIL"):
            status_enum = VerdictStatus.BLOCK

        event = AegisAuditEvent(
            trace_id=self.session_id,
            span_id=uuid.uuid4().hex[:8],
            step_index=self.step_index,
            timestamp=datetime.utcnow(),
            audit_reproducibility=AuditReproducibility(
                policy_bundle_version="asdlc-v0.2.0",
                policy_hash_digest=f"asdlc:phase:{phase or 'global'}",
                sentinel_version="0.1.0",
                evaluator_engine="asdlc-meisters+aegis-sentinel",
            ),
            environment=EnvironmentInfo(
                client_tool=ClientToolType.CLI,
                repository=str(self.project_dir),
                git_commit="HEAD",
                session_id=self.session_id,
            ),
            trigger=TriggerContext(
                source=f"asdlc:{action}",
                sanitized_prompt=sanitized_details[:300],
                redaction_applied=applied_redactions,
            ),
            retrieval_context=RetrievalContext(
                loaded_rules=[f"phase:{phase}"] if phase else [],
            ),
            inference_trace=InferenceTrace(),
            planning_evidence=plan_ev,
            action_payload=ActionPayload(
                tool_calls=[
                    ToolCallRecord(
                        tool_name=f"asdlc_{action}",
                        arguments=details,
                        status=verdict_status,
                    )
                ]
            ),
            sentinel_verdict=SentinelVerdict(
                status=status_enum,
                score=100.0 if status_enum == VerdictStatus.PASS else 70.0,
                tier_level="Tier 1 AST + Meisters Council",
            ),
            verification_evidence=verif_ev,
            integrity=IntegrityProof(
                previous_record_hash="pending",
                current_record_hash="pending",
            ),
        )

        self.recorder.record(event)
        return {
            "session_id": self.session_id,
            "step_index": self.step_index,
            "audit_trail_last_hash": self.recorder.audit_trail_last_hash,
            "redactions": applied_redactions
        }

    def verify_integrity(self) -> Tuple[bool, int, Optional[str]]:
        """
        現在のプロジェクトの監査台帳（audit-trail.jsonl）の暗号学的改ざんを検証
        戻り値: (成功フラグ, 検証ブロック数, エラーメッセージ)
        """
        if not self.enabled:
            return True, 0, None

        if not self.audit_trail_path.exists() or self.audit_trail_path.stat().st_size == 0:
            return True, 0, None

        return HashChainManager.verify_log_file(self.audit_trail_path)

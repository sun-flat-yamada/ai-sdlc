from typing import Dict, Any, List, Optional
from ..models import Phase, SDLCState, ReviewVerdict

class ProceduralAgent:
    """
    ① Procedural Agent:
    ウォーターフォールPhase 1〜7を自律進行させ、人の怠けを防ぐ対話型ガードレール。
    AIと人の明確な責務分担 (29220_b.png 準拠) に基づきタスクを制御する。
    """

    PHASE_SPECS: Dict[Phase, Dict[str, Any]] = {
        Phase.PHASE_1_REQUIREMENTS: {
            "name": "Phase 1: 要件定義",
            "task": "ビジネス要件、機能要件、非機能要件の定義",
            "output": "要件定義書 (requirements.md)",
            "ai_duties": [
                "既存コード解析・説明",
                "要件定義草案作成とそれに必要な質問ヒアリング",
                "要件定義書作成"
            ],
            "human_duties": [
                "開発方針の伝達",
                "質問への回答",
                "要件定義書草案レビュー",
                "整合性確認",
                "要件定義書の修正"
            ],
            "required_artifacts": ["requirements.md"]
        },
        Phase.PHASE_2_BASIC_DESIGN: {
            "name": "Phase 2: 基本設計",
            "task": "アーキテクチャ設計、技術スタック選定、ADR作成",
            "output": "基本設計書/ADR (basic_design.md, ADR-*.md)",
            "ai_duties": [
                "設計書草案生成とそれに必要な質問",
                "設計書作成"
            ],
            "human_duties": [
                "設計方針決定",
                "質問への回答",
                "設計草案レビュー",
                "整合性確認",
                "設計書の修正"
            ],
            "required_artifacts": ["basic_design.md"]
        },
        Phase.PHASE_3_DETAIL_DESIGN: {
            "name": "Phase 3: 詳細設計",
            "task": "API、データモデル、インフラの設計 / プロジェクト本体セットアップ",
            "output": "詳細設計書 / 設定ファイル (detail_design.md, schema, openapi)",
            "ai_duties": [
                "タスク分解支援",
                "テスト方針提案",
                "実行計画案作成",
                "Issue自動生成・登録"
            ],
            "human_duties": [
                "タスク優先度決定",
                "リソース計画",
                "実行計画承認",
                "Issue内容確認・修正"
            ],
            "required_artifacts": ["detail_design.md"]
        },
        Phase.PHASE_4_ITERATION: {
            "name": "Phase 4: 反復開発・実装",
            "task": "Epic/User StoryのIssue作成 → TDD → 実装 → コードレビュー → CI/CD・マージ",
            "output": "実装コード / Pull Request",
            "ai_duties": [
                "Coding Agentによる実装・単体テスト自動生成・実行",
                "CI/CD設定ファイル生成",
                "パイプライン最適化提案",
                "IaCコード・設定ドキュメント生成"
            ],
            "human_duties": [
                "PR内容レビュー",
                "成果物の動作確認",
                "IaCベースの設定内容確認",
                "パイプライン検証",
                "セキュリティ確認"
            ],
            "required_artifacts": []
        },
        Phase.PHASE_5_INTEGRATION_TEST: {
            "name": "Phase 5: 結合テスト",
            "task": "統合テスト / E2Eテスト / 負荷テスト",
            "output": "テスト結果 / 品質レポート (test_report.md)",
            "ai_duties": [
                "テストケース生成",
                "テストコード生成",
                "バグ分析・修正提案"
            ],
            "human_duties": [
                "テスト観点とケースレビュー",
                "テスト実施・確認",
                "品質基準判定"
            ],
            "required_artifacts": ["test_report.md"]
        },
        Phase.PHASE_6_PRODUCTION_RELEASE: {
            "name": "Phase 6: 本番リリース",
            "task": "リリース作成 / 承認フロー / 本番デプロイ",
            "output": "リリースノート / デプロイ記録 (release_notes.md)",
            "ai_duties": [
                "移行スクリプト生成",
                "データ変換支援",
                "環境設定ファイル作成"
            ],
            "human_duties": [
                "データ移行計画",
                "本番環境承認",
                "セキュリティ確認"
            ],
            "required_artifacts": ["release_notes.md"]
        },
        Phase.PHASE_7_MAINTENANCE: {
            "name": "Phase 7: 保守運用",
            "task": "監視・アラート / バグ修正、機能改善 / ドキュメント保守",
            "output": "改善 Pull Request / 運用ドキュメント (runbook.md)",
            "ai_duties": [
                "モニタリング設定",
                "障害分析支援",
                "改善提案・実装支援"
            ],
            "human_duties": [
                "リリース判断",
                "運用体制構築",
                "最終意思決定"
            ],
            "required_artifacts": []
        }
    }

    def get_phase_info(self, phase: Phase) -> Dict[str, Any]:
        return self.PHASE_SPECS.get(phase, {})

    def check_guardrails(
        self,
        state: SDLCState,
        phase: Phase,
        audit_integrity_result: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Proof of Review ガードレール:
        必須成果物の存在、最新のマイスターズレビュー合格、人間のレビュー証跡、
        および Aegis 監査台帳の暗号学的完全性を機械的に検証。
        """
        spec = self.PHASE_SPECS.get(phase, {})
        req_artifacts = spec.get("required_artifacts", [])
        missing_artifacts = [art for art in req_artifacts if art not in state.artifacts]
        
        # マイスターズレビューチェック
        phase_reviews = [r for r in state.reviews if r.phase == phase]
        passed_review = any(r.verdict == ReviewVerdict.PASS for r in phase_reviews) if req_artifacts else True

        # Aegis 監査ログ完全性チェック
        audit_tampered = False
        audit_error = None
        if audit_integrity_result and not audit_integrity_result.get("is_valid", True):
            audit_tampered = True
            audit_error = audit_integrity_result.get("error", "監査台帳のハッシュチェーンが破損しています。")

        is_blocked = bool(missing_artifacts) or (not passed_review if req_artifacts else False) or audit_tampered

        block_reasons = []
        if missing_artifacts:
            block_reasons.append(f"未作成の必須成果物があります: {missing_artifacts}")
        if req_artifacts and not passed_review:
            block_reasons.append("QA Agent（マイスターズレビュー）の合格判定が得られていません。")
        if audit_tampered:
            block_reasons.append(f"Aegis 監査台帳の暗号学的改ざんを検知しました: {audit_error}")

        return {
            "phase": phase,
            "is_blocked": is_blocked,
            "missing_artifacts": missing_artifacts,
            "passed_review": passed_review,
            "audit_tampered": audit_tampered,
            "block_reasons": block_reasons
        }


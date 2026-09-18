"""
End-to-End High-Quality Test Suite for ASDLC + Aegis Transparent Audit Integration
Tests the full software development lifecycle (Phase 1 to Phase 4/5) with cryptographic Hash Chain,
secret redaction, Meisters Council review, and tamper detection guardrails.
"""
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from asdlc.orchestrator import SDLCOrchestrator
from asdlc.models import Phase, ReviewVerdict, IssueType, IssuePriority
from asdlc.audit.bridge import AegisAuditBridge
from aegis.archivist.integrity import HashChainManager

SAMPLE_REQUIREMENTS = """# 要求仕様書: 次世代認証認可プラットフォーム

## 1. 概要と背景
全社規模で利用されるセキュアかつスケーラブルな次世代認証認可プラットフォームの要件を定義する。

## 2. セキュリティおよび認証認可 (Security & Auth)
JWT (JSON Web Token) を採用し、RS256署名によるトークン発行および改ざん防止を行う。
RBAC (Role-Based Access Control) による細粒度アクセス制御と暗号化プロトコル (TLS 1.3) を全エンドポイントに強制する。

## 3. 受入基準と自動テスト (Acceptance & Test)
Given-When-Then 形式による振る舞い駆動受入基準を策定する。
Given 有効なクレデンシャルを持つユーザー、When ログインエンドポイントへPOSTリクエストを送信、Then 署名済みJWTが返却される。
自動テストスイートによるCI/CDテストカバレッジ 90% 以上を必須条件とする。

## 4. 疎結合アーキテクチャ (Architecture & Components)
ヘキサゴナルアーキテクチャに基づき、ドメインロジックを外部インフラから完全分離する。
コンポーネント構成図およびモジュール間インターフェースを疎結合に定義し、部品カタログからの再利用を最大化する。

## 5. 実務運用と監視 (Operations & Monitoring)
Prometheus / Grafana によるメトリクス監視および死活監視アラートを設定する。
障害発生時の自動フェイルオーバーおよび運用手順書（ランブック）を整備し、ダウンタイムを最小化する。
"""

SAMPLE_BASIC_DESIGN = """# 基本設計書: 次世代認証認可プラットフォーム

## 1. アーキテクチャ概要
クリーンアーキテクチャ / ヘキサゴナルアーキテクチャを採用し、ドメイン・ユースケース・インフラ層を厳密に分離する。

## 2. 技術スタックおよび選定根拠 (ADR)
- 言語: Python 3.10+ / FastAPI
- 認証: JWT (RS256)
- データベース: PostgreSQL (接続プール付き)

## 3. 境界づけられたコンテキスト
認証コンテキスト、ユーザー管理コンテキスト、トークン検証コンテキストを疎結合に接続。

## 4. 運用・監視設計
OpenTelemetry による分散トレーシングおよび Prometheus メトリクスエクスポーター。
"""

SAMPLE_DETAIL_DESIGN = """# 詳細設計書: 認証API & データモデル

## 1. API エンドポイント仕様
- POST /api/v1/auth/login
  - Request: LoginRequest (username, password)
  - Response: 200 OK (access_token, token_type, expires_in)

## 2. データベーススキーマ
- users テーブル (id, username, password_hash, created_at)
- roles テーブル (id, name, permissions)

## 3. 単体テスト方針 (TDD)
pytest を用いた受入基準テスト（Given-When-Then）を先行実装する。
"""


class TestAegisTransparentSDLCIntegration(unittest.TestCase):
    """
    asdlc 利用側リポジトリにおける aah 透過的監査機能の高品質検証テストスイート
    """

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="asdlc_aegis_test_")
        self.orch = SDLCOrchestrator(project_dir=self.test_dir)
        self.audit_log = Path(self.test_dir) / ".aegis" / "logs" / "audit-trail.jsonl"
        self.forensic_log = Path(self.test_dir) / ".aegis" / "logs" / "forensic-trail.jsonl"

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_01_triage_with_secret_redaction_and_hash_chain(self):
        """1. Issueトリアージ時の機微情報自動マスキングとGenesisブロック封印 (DUMMY_SECRET_TEST)"""
        dummy_sk = "sk-" + "live-" + "99998888777766665555444433332222"
        dummy_ghp = "ghp_" + "ABCDEF1234567890abcdef1234567890"
        raw_issue = (
            f"Login failed: when submitting token with secret {dummy_sk} "
            f"and auth header Bearer {dummy_ghp}, 500 error occurs."
        )
        res = self.orch.triage_issue("Authentication Crash with Secret", raw_issue)

        self.assertIn(res.issue_type, [IssueType.SECURITY, IssueType.BUG])
        self.assertEqual(res.priority, IssuePriority.P0_CRITICAL)

        # 監査台帳の生成確認
        self.assertTrue(self.audit_log.exists())
        self.assertTrue(self.forensic_log.exists())

        # 平文シークレットがログファイルに漏洩していないことの検証
        audit_content = self.audit_log.read_text(encoding="utf-8")
        self.assertNotIn(dummy_sk, audit_content)
        self.assertNotIn(dummy_ghp, audit_content)


        # Hash Chain の暗号学的検証
        is_valid, count, err = self.orch.audit_bridge.verify_integrity()
        self.assertTrue(is_valid, f"Chain broken: {err}")
        self.assertEqual(count, 1)

    def test_02_requirements_registration_and_meisters_review(self):
        """2. 要件定義書登録とマイスターズ審議会審査の Hash Chain 連鎖"""
        # 要件定義書登録
        art = self.orch.register_artifact("requirements.md", SAMPLE_REQUIREMENTS)
        self.assertIsNotNone(art.content_hash)

        # マイスターズ審議会レビュー
        eval_res = self.orch.review_artifact("requirements.md")
        self.assertEqual(eval_res.verdict, ReviewVerdict.PASS)
        self.assertGreaterEqual(eval_res.total_score, 80.0)

        # 監査台帳が3ブロックに成長し、改ざんがないことの検証
        is_valid, count, err = self.orch.audit_bridge.verify_integrity()
        self.assertTrue(is_valid, f"Chain broken: {err}")
        self.assertEqual(count, 2)  # register_artifact + review_artifact

    def test_03_phase_advance_with_cryptographic_guardrail(self):
        """3. 暗号学的完全性を条件とした Phase 1 -> Phase 2 昇格"""
        self.orch.register_artifact("requirements.md", SAMPLE_REQUIREMENTS)
        self.orch.review_artifact("requirements.md")

        # 昇格実行
        adv = self.orch.advance_phase()
        self.assertTrue(adv["success"], f"Advance blocked: {adv}")
        self.assertEqual(self.orch.state.current_phase, Phase.PHASE_2_BASIC_DESIGN)

        # advance_phase イベントが第3ブロックとして記録されていること
        is_valid, count, err = self.orch.audit_bridge.verify_integrity()
        self.assertTrue(is_valid)
        self.assertEqual(count, 3)

    def test_04_full_sdlc_chain_to_phase4(self):
        """4. Phase 1 から Phase 4 (反復開発/TDD) までの多段ブロック連鎖と完全検証"""
        # Phase 1: 要件定義
        self.orch.register_artifact("requirements.md", SAMPLE_REQUIREMENTS)
        self.orch.review_artifact("requirements.md")
        self.orch.advance_phase()

        # Phase 2: 基本設計
        self.orch.register_artifact("basic_design.md", SAMPLE_BASIC_DESIGN)
        self.orch.review_artifact("basic_design.md")
        self.orch.advance_phase()
        self.assertEqual(self.orch.state.current_phase, Phase.PHASE_3_DETAIL_DESIGN)

        # Phase 3: 詳細設計
        self.orch.register_artifact("detail_design.md", SAMPLE_DETAIL_DESIGN)
        self.orch.review_artifact("detail_design.md")
        self.orch.advance_phase()
        self.assertEqual(self.orch.state.current_phase, Phase.PHASE_4_ITERATION)

        # Phase 4: Coding Agent スキャフォールド生成
        scaffold = self.orch.coding.generate_scaffolding("JWT認証API", lang="python")
        self.assertIn("tdd_test_scaffold", scaffold)

        # 全工程の Hash Chain が完全であること
        is_valid, count, err = self.orch.audit_bridge.verify_integrity()
        self.assertTrue(is_valid, f"Verification failed: {err}")
        self.assertGreaterEqual(count, 8)  # 3フェーズ × (登録 + レビュー + 昇格)

    def test_05_tamper_detection_and_guardrail_lock(self):
        """5. 監査台帳改ざん時の即時検知およびガードレールによる昇格物理ロック"""
        self.orch.register_artifact("requirements.md", SAMPLE_REQUIREMENTS)
        self.orch.review_artifact("requirements.md")

        # 昇格前に故意にログファイルを1文字改変（改ざんシミュレーション）
        content = self.audit_log.read_text(encoding="utf-8")
        lines = content.strip().splitlines()
        first_record = json.loads(lines[0])
        first_record["trigger"]["source"] = "tampered_injection"
        lines[0] = json.dumps(first_record)
        self.audit_log.write_text("\n".join(lines) + "\n", encoding="utf-8")

        # 1. verify_integrity が改ざんを即時検知すること
        is_valid, failed_line, err = self.orch.audit_bridge.verify_integrity()
        self.assertFalse(is_valid)
        self.assertEqual(failed_line, 1)
        self.assertIn("Tampering detected", err)

        # 2. advance_phase() がガードレールにより物理的に拒絶（ブロック）されること
        adv = self.orch.advance_phase()
        self.assertFalse(adv["success"])
        self.assertEqual(self.orch.state.current_phase, Phase.PHASE_1_REQUIREMENTS)
        self.assertTrue(any("Aegis 監査台帳の暗号学的改ざんを検知しました" in r for r in adv["reasons"]))

    def test_06_graceful_fallback_when_disabled(self):
        """6. Aegis 機能が無効または利用不可の環境でのフォールバック保証"""
        fallback_dir = tempfile.mkdtemp(prefix="asdlc_fallback_")
        try:
            orch_fallback = SDLCOrchestrator(project_dir=fallback_dir)
            orch_fallback.audit_bridge.enabled = False  # 強制無効化

            orch_fallback.register_artifact("requirements.md", SAMPLE_REQUIREMENTS)
            eval_res = orch_fallback.review_artifact("requirements.md")
            self.assertEqual(eval_res.verdict, ReviewVerdict.PASS)

            # エラーにならず通常通りフェーズ昇格可能
            adv = orch_fallback.advance_phase()
            self.assertTrue(adv["success"])
            self.assertEqual(orch_fallback.state.current_phase, Phase.PHASE_2_BASIC_DESIGN)
        finally:
            shutil.rmtree(fallback_dir, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()

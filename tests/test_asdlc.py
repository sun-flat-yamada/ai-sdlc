import unittest
import sys
import tempfile
import shutil
from pathlib import Path
from typer.testing import CliRunner

# Add workspace to path
WORKSPACE_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(WORKSPACE_ROOT))

from asdlc.orchestrator import SDLCOrchestrator
from asdlc.models import Phase, ReviewVerdict, IssueType, IssuePriority
from asdlc.cli.main import app

class TestASDLCSDK(unittest.TestCase):
    def setUp(self):
        self.fixtures_dir = WORKSPACE_ROOT / "tests" / "fixtures"
        self.test_dir = tempfile.mkdtemp()
        self.orch = SDLCOrchestrator(project_dir=self.test_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_01_issue_auto_triage_normal_fixture(self):
        issue_file = self.fixtures_dir / "sample_issues" / "normal_bug.md"
        content = issue_file.read_text(encoding="utf-8")
        lines = content.splitlines()
        title = lines[0].replace("#", "").strip()
        body = "\n".join(lines[1:])
        
        res = self.orch.triage_issue(title, body)
        self.assertEqual(res.issue_type, IssueType.BUG)
        self.assertEqual(res.estimated_component, "auth")
        self.assertFalse(res.prompt_injection_detected)
        self.assertIn("docs/ADR-0004-jwt-auth.md", res.matched_adrs_or_specs)

    def test_02_issue_auto_triage_injection_defense_fixture(self):
        issue_file = self.fixtures_dir / "sample_issues" / "injection_attack.md"
        content = issue_file.read_text(encoding="utf-8")
        lines = content.splitlines()
        title = lines[0].replace("#", "").strip()
        body = "\n".join(lines[1:])
        
        res = self.orch.triage_issue(title, body)
        self.assertTrue(res.prompt_injection_detected)
        self.assertIn("[FILTERED_SECURITY_RISK]", res.sanitized_body)
        self.assertTrue(len(res.injection_warnings) > 0)
        self.assertIn("security:prompt-injection-flagged", res.suggested_labels)

    def test_03_meisters_review_and_guardrails_fixture(self):
        # 1. Guardrail blocks advance before requirements are met
        check = self.orch.procedural.check_guardrails(self.orch.state, Phase.PHASE_1_REQUIREMENTS)
        self.assertTrue(check["is_blocked"])
        
        # 2. Load requirements fixture
        req_fixture = self.fixtures_dir / "sample_docs" / "requirements.md"
        doc_content = req_fixture.read_text(encoding="utf-8")
        self.orch.register_artifact("requirements.md", doc_content)
        
        # 3. Review with Council of Meisters
        eval_res = self.orch.review_artifact("requirements.md")
        self.assertEqual(len(eval_res.meister_scores), 7)
        self.assertGreaterEqual(eval_res.total_score, 80.0)
        self.assertEqual(eval_res.verdict, ReviewVerdict.PASS)

        # 4. Advance phase should succeed now
        adv_res = self.orch.advance_phase()
        self.assertTrue(adv_res["success"])
        self.assertEqual(adv_res["new_phase"], Phase.PHASE_2_BASIC_DESIGN)

    def test_04_coding_agent_context(self):
        ctx = self.orch.coding.synthesize_code_context("ユーザー一覧画面とJWT認証ログインAPI")
        self.assertTrue(len(ctx["layer_1_governance"]) > 0)
        self.assertTrue(len(ctx["layer_2_standards"]) > 0)
        self.assertTrue(len(ctx["reusable_components_detected"]) > 0)

    def test_05_cli_runner(self):
        runner = CliRunner()
        res = runner.invoke(app, ["status"])
        self.assertEqual(res.exit_code, 0)
        self.assertIn("ASDLC Pipeline Status", res.output)

        issue_fixture = str(self.fixtures_dir / "sample_issues" / "normal_bug.md")
        res_triage = runner.invoke(app, ["triage", issue_fixture])
        self.assertEqual(res_triage.exit_code, 0)
        self.assertIn("4D Triage Result", res_triage.output)

    def test_06_coding_scaffolding_and_tdd(self):
        scaffold = self.orch.coding.generate_scaffolding("JWT認証ログインAPIとユーザーテーブル")
        self.assertIn("reusable_imports", scaffold)
        self.assertIn("tdd_test_scaffold", scaffold)
        self.assertIn("@enterprise/jwt-auth-middleware", scaffold["reusable_imports"])
        self.assertIn("test_acceptance_criteria", scaffold["tdd_test_scaffold"])

    def test_07_polyglot_coding_agent_context_and_scaffolding(self):
        # 1. Python Context & Scaffolding
        ctx_py = self.orch.coding.synthesize_code_context("FastAPIを用いた商品登録API", lang="python")
        self.assertEqual(ctx_py["detected_language"], "python")
        self.assertTrue(any("Pydantic v2" in r for r in ctx_py["tier_2_language_pack"]))
        self.assertTrue(any("OWASP" in r for r in ctx_py["tier_1_governance_agnostic"]))
        scaffold_py = self.orch.coding.generate_scaffolding("FastAPI商品登録API", lang="python")
        self.assertIn("import pytest", scaffold_py["tdd_test_scaffold"])

        # 2. TypeScript Context & Scaffolding
        ctx_ts = self.orch.coding.synthesize_code_context("Reactデータグリッドとログイン画面", lang="typescript")
        self.assertEqual(ctx_ts["detected_language"], "typescript")
        self.assertTrue(any("Strict Mode" in r for r in ctx_ts["tier_2_language_pack"]))
        scaffold_ts = self.orch.coding.generate_scaffolding("Reactデータグリッド", lang="typescript")
        self.assertIn("vitest", scaffold_ts["tdd_test_scaffold"])

        # 3. Go Context & Scaffolding
        ctx_go = self.orch.coding.synthesize_code_context("高スループット監査ロギングgRPCサービス", lang="go")
        self.assertEqual(ctx_go["detected_language"], "go")
        self.assertTrue(any("Effective Go" in r for r in ctx_go["tier_2_language_pack"]))
        scaffold_go = self.orch.coding.generate_scaffolding("監査ロギングサービス", lang="go")
        self.assertIn("testing", scaffold_go["tdd_test_scaffold"])
        self.assertIn("TestAcceptanceCriteria", scaffold_go["tdd_test_scaffold"])

        # 4. C Context & Scaffolding
        ctx_c = self.orch.coding.synthesize_code_context("組込みバッファメモリ制御モジュール", lang="c")
        self.assertEqual(ctx_c["detected_language"], "c")
        self.assertTrue(any("C11/C17/C23" in r for r in ctx_c["tier_2_language_pack"]))
        scaffold_c = self.orch.coding.generate_scaffolding("バッファモジュール", lang="c")
        self.assertIn("assert", scaffold_c["tdd_test_scaffold"])

        # 5. C++ Context & Scaffolding
        ctx_cpp = self.orch.coding.synthesize_code_context("低遅延マッチングエンジンとスマートポインタ", lang="cpp")
        self.assertEqual(ctx_cpp["detected_language"], "cpp")
        self.assertTrue(any("RAII" in r for r in ctx_cpp["tier_2_language_pack"]))
        scaffold_cpp = self.orch.coding.generate_scaffolding("マッチングエンジン", lang="cpp")
        self.assertIn("gtest", scaffold_cpp["tdd_test_scaffold"])

        # 6. C# Context & Scaffolding
        ctx_cs = self.orch.coding.synthesize_code_context("ASP.NET Core決済マイクロサービス", lang="csharp")
        self.assertEqual(ctx_cs["detected_language"], "csharp")
        self.assertTrue(any("Nullable" in r for r in ctx_cs["tier_2_language_pack"]))
        scaffold_cs = self.orch.coding.generate_scaffolding("決済マイクロサービス", lang="csharp")
        self.assertIn("Xunit", scaffold_cs["tdd_test_scaffold"])

        # 7. CLI code command with --lang option
        runner = CliRunner()
        res = runner.invoke(app, ["code", "商品マスタAPI", "--lang", "python"])
        self.assertEqual(res.exit_code, 0)
        self.assertIn("TARGET LANGUAGE", res.output.upper())
        self.assertIn("PYTHON", res.output.upper())

        res_cs = runner.invoke(app, ["code", "決済サービス", "--lang", "csharp"])
        self.assertEqual(res_cs.exit_code, 0)
        self.assertIn("CSHARP", res_cs.output.upper())

    def test_08_meisters_clarified_roles_and_responsibilities(self):
        qa = self.orch.qa
        self.assertEqual(len(qa.MEISTER_PROFILES), 7)
        for meister_type, profile in qa.MEISTER_PROFILES.items():
            self.assertIn("name", profile)
            self.assertIn("role", profile)
            self.assertIn("responsibility", profile)
            self.assertIn("monitoring_guidance", profile)
            self.assertIn("focus", profile)
            self.assertIn("Meister", profile["name"])
            self.assertTrue(len(profile["role"]) > 0)
            self.assertTrue(len(profile["responsibility"]) > 0)
            self.assertTrue(len(profile["monitoring_guidance"]) > 0)

        # Specifically check Isolation Architecture Meister's GenAI resilience focus
        from asdlc.models import MeisterType
        iso_profile = qa.MEISTER_PROFILES[MeisterType.ISOLATION_ARCHITECTURE]
        self.assertIn("Clean Architecture", iso_profile["role"])
        self.assertIn("生成AI", iso_profile["monitoring_guidance"])
        self.assertIn("劣化", iso_profile["monitoring_guidance"])

if __name__ == "__main__":
    unittest.main()


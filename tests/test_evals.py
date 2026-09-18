import unittest
import sys
from pathlib import Path
from typer.testing import CliRunner

# Add workspace to path
WORKSPACE_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(WORKSPACE_ROOT))

from asdlc.evals import (
    EvaluationTier,
    EvalStatus,
    EvaluationRunner,
    StaticEvaluator,
    BehavioralEvaluator,
    RubricEvaluator
)
from asdlc.cli.main import app

class TestASDLCSupervisedEvaluations(unittest.TestCase):
    def setUp(self):
        self.workspace_root = WORKSPACE_ROOT
        self.cli_runner = CliRunner()

    def test_01_static_evaluator_tier1(self):
        """Tier 1: 静的構造・フロントマター・整合性検証"""
        evaluator = StaticEvaluator(self.workspace_root)
        results = evaluator.evaluate_all()
        
        self.assertGreaterEqual(len(results), 15, "Tier 1 の評価対象成果物（Agent, Skill, Rule, Workflow）が不足しています。")
        for res in results:
            self.assertEqual(res.tier, EvaluationTier.TIER_1_STATIC)
            self.assertEqual(res.status, EvalStatus.PASS, f"Tier 1 検証失敗: {res.item_id} - {res.recommendations}")
            self.assertEqual(res.score, 100.0)

    def test_02_behavioral_evaluator_tier2(self):
        """Tier 2: 行動・軌跡決定論的検証 (Behavior & Trajectory)"""
        evaluator = BehavioralEvaluator()
        results = evaluator.evaluate_all()
        
        self.assertEqual(len(results), 6, "Tier 2 のテストケース数（Coding, QA, Code Review, Procedural, Triage, Aegis Audit）が一致しません。")
        for res in results:
            self.assertEqual(res.tier, EvaluationTier.TIER_2_BEHAVIOR)
            self.assertEqual(res.status, EvalStatus.PASS, f"Tier 2 検証失敗: {res.item_id} - {res.recommendations}")
            self.assertGreaterEqual(res.score, 80.0)


    def test_03_rubric_evaluator_tier3(self):
        """Tier 3: ルーブリック品質・実行可能性評価 (Rubric & Actionability)"""
        evaluator = RubricEvaluator()
        results = evaluator.evaluate_all()
        
        self.assertEqual(len(results), 3, "Tier 3 のルーブリック評価項目数が一致しません。")
        for res in results:
            self.assertEqual(res.tier, EvaluationTier.TIER_3_RUBRIC)
            self.assertEqual(res.status, EvalStatus.PASS, f"Tier 3 検証失敗: {res.item_id} - {res.recommendations}")
            self.assertGreaterEqual(res.score, 80.0)

    def test_04_evaluation_runner_overall_asqs(self):
        """EvaluationRunner による総合 ASQS スコア算出および合否判定"""
        runner = EvaluationRunner(self.workspace_root)
        report = runner.run_evaluations(target="all")
        
        self.assertEqual(report.overall_verdict, EvalStatus.PASS)
        self.assertGreaterEqual(report.overall_asqs_score, 80.0)
        total_failed = sum(t.failed_checks for t in report.tier_summaries)
        self.assertEqual(total_failed, 0)
        self.assertEqual(len(report.tier_summaries), 3)

    def test_05_evaluation_runner_target_filter(self):
        """EvaluationRunner の個別 Tier フィルタリング動作検証"""
        runner = EvaluationRunner(self.workspace_root)
        
        rep_tier1 = runner.run_evaluations(target="tier1")
        self.assertEqual(len(rep_tier1.tier_summaries), 1)
        self.assertEqual(rep_tier1.tier_summaries[0].tier, EvaluationTier.TIER_1_STATIC)

        rep_tier2 = runner.run_evaluations(target="tier2")
        self.assertEqual(len(rep_tier2.tier_summaries), 1)
        self.assertEqual(rep_tier2.tier_summaries[0].tier, EvaluationTier.TIER_2_BEHAVIOR)

    def test_06_cli_eval_command(self):
        """asdlc eval CLI コマンドの正常終了および JSON 出力検証"""
        # 1. Standard Rich output
        result = self.cli_runner.invoke(app, ["eval"])
        self.assertEqual(result.exit_code, 0, f"asdlc eval 実行エラー: {result.stdout}")
        self.assertIn("ASQS", result.stdout)
        self.assertIn("PASS", result.stdout)

        # 2. JSON output
        result_json = self.cli_runner.invoke(app, ["eval", "--json"])
        self.assertEqual(result_json.exit_code, 0)
        self.assertIn('"overall_verdict": "PASS"', result_json.stdout)
        self.assertIn('"overall_asqs_score":', result_json.stdout)

if __name__ == "__main__":
    unittest.main()

from datetime import datetime
from typing import List, Optional
from .models import EvaluationTier, EvalStatus, EvaluationItemResult, TierSummary, OverallEvaluationReport
from .static_eval import StaticEvaluator
from .behavior_eval import BehavioralEvaluator
from .rubric_eval import RubricEvaluator

class EvaluationRunner:
    """
    ASDLC Agent & Skill Quality Evaluation Runner
    Tier 1 (静的), Tier 2 (行動・軌跡), Tier 3 (ルーブリック品質) を統括実行し、
    総合スコア ASQS (Agent & Skill Quality Score) を算出する。
    """

    def __init__(self, root_dir=None):
        self.static_eval = StaticEvaluator(root_dir)
        self.behavior_eval = BehavioralEvaluator()
        self.rubric_eval = RubricEvaluator()

    def run_evaluations(self, target: str = "all") -> OverallEvaluationReport:
        all_results: List[EvaluationItemResult] = []

        # 1. Tier 1: Static
        static_results = self.static_eval.evaluate_all()
        all_results.extend(static_results)

        # 2. Tier 2: Behavioral
        behavior_results = self.behavior_eval.evaluate_all()
        all_results.extend(behavior_results)

        # 3. Tier 3: Rubric
        rubric_results = self.rubric_eval.evaluate_all()
        all_results.extend(rubric_results)

        # Target filtering if requested
        if target in ["skills", "skill"]:
            filtered = [r for r in all_results if r.target_type == "skill"]
        elif target in ["agents", "agent"]:
            filtered = [r for r in all_results if r.target_type == "agent"]
        elif target in ["rules", "rule"]:
            filtered = [r for r in all_results if r.target_type == "rule"]
        elif target in ["workflows", "workflow"]:
            filtered = [r for r in all_results if r.target_type == "workflow"]
        elif target in ["tier1", "tier_1", "static"]:
            filtered = [r for r in all_results if r.tier == EvaluationTier.TIER_1_STATIC]
        elif target in ["tier2", "tier_2", "behavior", "behavioral"]:
            filtered = [r for r in all_results if r.tier == EvaluationTier.TIER_2_BEHAVIOR]
        elif target in ["tier3", "tier_3", "rubric"]:
            filtered = [r for r in all_results if r.tier == EvaluationTier.TIER_3_RUBRIC]
        else:
            filtered = all_results

        # Calculate Tier Summaries
        tier_summaries = []
        for tier in EvaluationTier:
            items = [r for r in filtered if r.tier == tier]
            if not items:
                continue
            passed = sum(1 for r in items if r.status == EvalStatus.PASS)
            failed = len(items) - passed
            avg_score = sum(r.score for r in items) / len(items)
            tier_summaries.append(
                TierSummary(
                    tier=tier,
                    total_checks=len(items),
                    passed_checks=passed,
                    failed_checks=failed,
                    average_score=round(avg_score, 1)
                )
            )

        # Overall ASQS score calculation
        if filtered:
            total_asqs = sum(r.score for r in filtered) / len(filtered)
            all_pass = all(r.status == EvalStatus.PASS for r in filtered)
            overall_verdict = EvalStatus.PASS if (all_pass and total_asqs >= 80.0) else EvalStatus.FAIL
        else:
            total_asqs = 0.0
            overall_verdict = EvalStatus.FAIL

        msg = (
            f"ASDLC Evaluation 完了: 総合 ASQS スコア {total_asqs:.1f}点 / 100点 -> 判定: {overall_verdict.value} "
            f"(合格項目: {sum(t.passed_checks for t in tier_summaries)} / {len(filtered)})"
        )

        return OverallEvaluationReport(
            timestamp=datetime.now().isoformat(),
            overall_asqs_score=round(total_asqs, 1),
            overall_verdict=overall_verdict,
            tier_summaries=tier_summaries,
            item_results=filtered,
            summary_message=msg
        )

from typing import List
from .models import EvaluationTier, EvalStatus, EvaluationItemResult
from ..agents.qa import QAAgent
from ..agents.coding import CodingAgent
from ..models import Phase, MeisterType

class RubricEvaluator:
    """
    Tier 3: ルーブリック品質・具体性評価 (Rubric & Actionability Evaluation)
    SkillsBench に準拠し、エージェント出力の具体性（Actionability）、
    再発明防止性、およびガバナンス遵守度を客観的ルーブリックで評価する。
    """

    def __init__(self):
        self.qa = QAAgent()
        self.coding = CodingAgent()

    def evaluate_all(self) -> List[EvaluationItemResult]:
        results = []
        results.append(self.eval_meisters_remediation_actionability())
        results.append(self.eval_coding_anti_reinvention_precision())
        results.append(self.eval_governance_rule_completeness())
        return results

    def eval_meisters_remediation_actionability(self) -> EvaluationItemResult:
        """マイスターズ審議会の指摘事項における具体的改善指示（Actionability）の評価"""
        score = 100.0
        recs = []

        # 不備のあるドキュメントを評価させ、出力される指摘の具体性を検査
        deficient_doc = "# 機能仕様書\nユーザー管理機能。とりあえず作成する。"
        evaluation = self.qa.evaluate_document("short_spec.md", deficient_doc, Phase.PHASE_1_REQUIREMENTS)

        all_recommendations = []
        for s in evaluation.meister_scores:
            all_recommendations.extend(s.recommendations)

        if not all_recommendations:
            score -= 50.0
            recs.append("FAIL判定時に改善指示（Recommendations）が1件も生成されていません。")
        else:
            # 具体的キーワード（章節、プロトコル、テスト等）が含まれているか検証
            concrete_keywords = ["章", "追加", "形式", "計画", "記述", "具体化"]
            concrete_count = sum(
                1 for r in all_recommendations if any(kw in r for kw in concrete_keywords)
            )
            actionability_ratio = concrete_count / len(all_recommendations)
            if actionability_ratio < 0.8:
                score -= 30.0
                recs.append(f"改善指示の具体性比率が低すぎます ({actionability_ratio * 100:.1f}%)。")

        status = EvalStatus.PASS if score >= 80.0 else EvalStatus.FAIL
        return EvaluationItemResult(
            item_id="rubric:meisters_actionability",
            target_type="skill",
            tier=EvaluationTier.TIER_3_RUBRIC,
            status=status,
            score=max(0.0, score),
            details=f"マイスターズ指摘事項の実行可能性・具体性評価 (Actionability Score: {score:.1f})",
            recommendations=recs
        )

    def eval_coding_anti_reinvention_precision(self) -> EvaluationItemResult:
        """Coding Agent の車輪の再発明防止（Anti-Reinvention）適合精度の評価"""
        score = 100.0
        recs = []

        test_cases = [
            ("JWT認証によるログインAPI", "@enterprise/jwt-auth-middleware"),
            ("ユーザー一覧のソート可能なテーブルUI", "@enterprise/ui-datagrid"),
            ("監査ログの構造化出力ハンドラ", "@enterprise/structured-logger")
        ]

        for prompt, expected_comp in test_cases:
            matches = self.coding.search_reusable_components(prompt)
            matched_names = [m["name"] for m in matches]
            if expected_comp not in matched_names:
                score -= 25.0
                recs.append(f"意図 '{prompt}' に対して推奨部品 '{expected_comp}' が検出されませんでした。")

        status = EvalStatus.PASS if score >= 80.0 else EvalStatus.FAIL
        return EvaluationItemResult(
            item_id="rubric:anti_reinvention_precision",
            target_type="skill",
            tier=EvaluationTier.TIER_3_RUBRIC,
            status=status,
            score=max(0.0, score),
            details=f"コンポーネントカタログ再利用検出適合度 (Precision Score: {score:.1f})",
            recommendations=recs
        )

    def eval_governance_rule_completeness(self) -> EvaluationItemResult:
        """全社ガバナンス（Layer 1）制約の強制網羅性の評価"""
        score = 100.0
        recs = []

        ctx = self.coding.synthesize_code_context("任意の機能開発")
        l1_policies = ctx.get("layer_1_governance", [])

        # 必須ガバナンス3大要素: セキュリティ、規約/型、仕様コメント
        required_elements = ["セキュリティ", "規約", "仕様"]
        for elem in required_elements:
            if not any(elem in p for p in l1_policies):
                score -= 25.0
                recs.append(f"Layer 1 ガバナンス規約に '{elem}' 関連のポリシーが欠落しています。")

        status = EvalStatus.PASS if score >= 80.0 else EvalStatus.FAIL
        return EvaluationItemResult(
            item_id="rubric:governance_enforcement",
            target_type="rule",
            tier=EvaluationTier.TIER_3_RUBRIC,
            status=status,
            score=max(0.0, score),
            details=f"Layer 1 不可侵ガバナンス規約の網羅度 (Enforcement Score: {score:.1f})",
            recommendations=recs
        )

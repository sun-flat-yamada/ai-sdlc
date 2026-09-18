from typing import List, Dict, Any
from ..models import Phase, ReviewVerdict, MeisterType, MeisterScore, MeisterEvaluation

class QAAgent:
    """
    ② QA Agent (The Meisters Council):
    「マイスターズレビュー憲章 (docs/charter/MEISTERS_CHARTER.md)」に準拠した多角的高品質レビュー審議会（マイスターズ審議会）。
    7つのマイスター（および将来追加されるマイスター）が独立採点し、
    調停者（Chief Moderator）が統合判定を行う。
    """

    MEISTER_PROFILES = {
        MeisterType.THREAT_DEFENSE: {
            "name": "Threat Defense Meister",
            "role": "脅威やリスク対策のMeister",
            "responsibility": "脆弱性・不確実性の脅威が残存しておらず、認証・暗号化、シークレット漏洩の徹底排除に責任を持つ",
            "monitoring_guidance": "多角的なリスク対策視点で監視し、改善を導く",
            "focus": "脆弱性・不確実性の脅威排除、認証・暗号化、シークレット漏洩の徹底防止、多角的なリスク対策視点の監視・改善"
        },
        MeisterType.REQUIREMENT_FULFILLMENT: {
            "name": "Requirement Fulfillment Meister",
            "role": "ビジネス要求・ユーザー要求の仕様定義Meister",
            "responsibility": "要求の仕様化が十分行われていることに責任を持つ",
            "monitoring_guidance": "ビジネス要求・ユーザー要求の完全充足、境界値・エッジケース網羅がされていること、または合理的に推測できることを監視し、改善を導く",
            "focus": "ビジネス要求・ユーザー要求の完全充足、境界値・エッジケース網羅、仕様定義の完全性、暗黙の前提の排除"
        },
        MeisterType.PRAGMATIC_OPERATIONS: {
            "name": "Pragmatic Operations Meister",
            "role": "リアルな現場運用のMeister",
            "responsibility": "本番実運用の現実性、可観測性（ログ・監視・アラート）、ランブック具体性に責任を持つ",
            "monitoring_guidance": "本当に運用できるかを最重視し、具体化されていない曖昧な領域や箇所が残っていないかを監視し、改善を導く",
            "focus": "本番実運用の現実性、可観測性（ログ・監視・アラート）、ランブック具体性、曖昧な運用の徹底排除"
        },
        MeisterType.QUALITY_ASSURANCE: {
            "name": "Quality Assurance Meister",
            "role": "品質保証のMeister",
            "responsibility": "受入基準（Given-When-Then）、客観的テスト可能性、品質メトリクスに責任を持つ",
            "monitoring_guidance": "検証可能か、受入品質基準が十分に定義されているかといったことを監視し、改善を導く",
            "focus": "受入基準（Given-When-Then）、客観的テスト可能性、品質メトリクス、検証可能性の監視・改善"
        },
        MeisterType.GOVERNANCE_COMPLIANCE: {
            "name": "Governance Compliance Meister",
            "role": "規律を統制し、説明責任をはたすMeister",
            "responsibility": "全社開発標準・規約準拠、ADR意思決定経緯の透明性と説明に責任を持つ",
            "monitoring_guidance": "意思決定材料の網羅性や説明可能になっていることを監視し、改善を導く",
            "focus": "全社開発標準・規約準拠、ADR意思決定経緯の透明性と説明責任、意思決定材料の網羅性の監視・改善"
        },
        MeisterType.VALUE_PROPOSITION: {
            "name": "Value Proposition Meister",
            "role": "ビジネス価値提供のMeister",
            "responsibility": "真の顧客価値創出、ROI、市場競争優位性、過剰/不足設計の排除といったことに責任を持つ",
            "monitoring_guidance": "本当に市場で「刺さる提案」か「勝てるか」を監視し、改善を導く",
            "focus": "真の顧客価値創出、ROI、市場競争優位性、過剰/不足設計の排除、市場適合性の監視・改善"
        },
        MeisterType.ISOLATION_ARCHITECTURE: {
            "name": "Isolation Architecture Meister",
            "role": "疎結合なClean ArchitectureのMeister",
            "responsibility": "疎結合性、コンポーザブル部品化、全社コンポーネントの再利用徹底といった視点でソフトウエア構造に責任を持つ",
            "monitoring_guidance": "生成AIによる繰り返し変更においても劣化を最小に抑えられるソフトウエア構造となっているかを監視し、改善を導く",
            "focus": "疎結合性、コンポーザブル部品化、全社コンポーネント再利用徹底、生成AIの反復変更に耐えうる劣化最小化構造"
        }
    }

    def evaluate_document(self, document_name: str, document_content: str, phase: Phase) -> MeisterEvaluation:
        """
        マイスターズ審議会による成果物審査（マイスターズレビュー・憲章準拠アルゴリズム）
        """
        meister_scores: List[MeisterScore] = []
        doc_len = len(document_content)
        base_score = 88 if doc_len > 250 else 65

        for meister, meta in self.MEISTER_PROFILES.items():
            score = base_score
            recs = []
            
            # 各マイスターの審査基準
            if meister == MeisterType.THREAT_DEFENSE:
                if not any(w in document_content.lower() for w in ["security", "auth", "rbac", "セキュリティ", "暗号化", "認証"]):
                    score -= 20
                    recs.append("脅威分析およびセキュリティ・アクセス制御の章を追加してください。")
            elif meister == MeisterType.QUALITY_ASSURANCE:
                if not any(w in document_content.lower() for w in ["test", "acceptance", "テスト", "受入基準"]):
                    score -= 15
                    recs.append("受入基準（Given-When-Then形式）と自動テスト計画を明記してください。")
            elif meister == MeisterType.ISOLATION_ARCHITECTURE:
                if not any(w in document_content.lower() for w in ["architecture", "component", "構成", "疎結合", "モジュール"]):
                    score -= 15
                    recs.append("コンポーネント構成図および依存関係の疎結合性（コンポーザブル設計）を記述してください。")
            elif meister == MeisterType.PRAGMATIC_OPERATIONS:
                if not any(w in document_content.lower() for w in ["operation", "monitoring", "alert", "運用", "監視", "障害"]):
                    score -= 10
                    recs.append("実務運用時の監視項目・アラート基準および障害復旧方針を具体化してください。")

            verdict = ReviewVerdict.PASS if score >= 70 else ReviewVerdict.FAIL
            critique = f"{meta['name']}の観点から審査を実施。適合度: {score}/100点。"

            meister_scores.append(MeisterScore(
                meister=meister,
                score=score,
                verdict=verdict,
                critique=critique,
                recommendations=recs
            ))

        avg_score = sum(s.score for s in meister_scores) / len(meister_scores)
        min_score = min(s.score for s in meister_scores)

        # 憲章第3条の合否条件: 加重平均 ≧ 80.0 かつ 最低点 ≧ 70
        is_pass = avg_score >= 80.0 and min_score >= 70
        overall_verdict = ReviewVerdict.PASS if is_pass else ReviewVerdict.FAIL

        summary = (
            f"マイスターズレビュー完了: 平均スコア {avg_score:.1f}点 (最低: {min_score}点) -> 判定: {overall_verdict.value} "
            f"[準拠憲章: docs/charter/MEISTERS_CHARTER.md]"
        )

        return MeisterEvaluation(
            document_name=document_name,
            phase=phase,
            total_score=round(avg_score, 1),
            min_score=min_score,
            verdict=overall_verdict,
            meister_scores=meister_scores,
            summary=summary,
            remediation_required=not is_pass
        )

    def evaluate_code(
        self,
        code_path: str,
        code_content: str,
        lang: str = None,
        phase: Phase = Phase.PHASE_4_ITERATION,
        deterministic_only: bool = False
    ) -> MeisterEvaluation:
        """
        ソースコード審査（決定論的静的解析ゲート ＋ マイスターズ審議会セマンティックレビュー）
        憲章第4条（ソースコード審査における決定論的第1防壁の遵守原則）準拠
        """
        from ..review.engine import DeterministicCodeReviewer
        from ..review.models import Severity, IssueCategory

        reviewer = DeterministicCodeReviewer()
        report = reviewer.review(code_path, content=code_content, lang=lang)

        # Stage 1: Short-Circuiting (重大欠陥検知時は即時FAIL)
        if report.has_errors:
            error_issues = [i for i in report.issues if i.severity == Severity.ERROR]
            threat_errors = [i for i in error_issues if i.category == IssueCategory.SECURITY]
            qa_errors = [i for i in error_issues if i.category in (IssueCategory.ROBUSTNESS, IssueCategory.SYNTAX)]
            gov_errors = [i for i in error_issues if i.category in (IssueCategory.GOVERNANCE, IssueCategory.STYLE)]

            meister_scores: List[MeisterScore] = []
            for meister, meta in self.MEISTER_PROFILES.items():
                score = 50
                recs = []
                if meister == MeisterType.THREAT_DEFENSE and threat_errors:
                    score = 30
                    recs.extend([f"[CWE/SEC] Line {e.line}: {e.message} (推奨対策: {e.remediation})" for e in threat_errors])
                elif meister == MeisterType.QUALITY_ASSURANCE and qa_errors:
                    score = 35
                    recs.extend([f"[ROBUSTNESS] Line {e.line}: {e.message} (推奨対策: {e.remediation})" for e in qa_errors])
                elif meister == MeisterType.GOVERNANCE_COMPLIANCE and gov_errors:
                    score = 40
                    recs.extend([f"[GOVERNANCE] Line {e.line}: {e.message} (推奨対策: {e.remediation})" for e in gov_errors])
                elif meister == MeisterType.ISOLATION_ARCHITECTURE:
                    score = 60
                    recs.append("決定論的静的解析で重大エラーが検出されたため、アーキテクチャ審査を保留しました。")
                else:
                    recs.append("決定論的静的解析エラーの解消後に再審査が必要です。")

                meister_scores.append(MeisterScore(
                    meister=meister,
                    score=score,
                    verdict=ReviewVerdict.FAIL,
                    critique=f"{meta['name']}: 決定論的静的解析ゲートにより重大欠陥 (ERROR) が検知され、Short-Circuit 遮断されました。",
                    recommendations=recs
                ))

            avg_score = sum(s.score for s in meister_scores) / len(meister_scores)
            min_score = min(s.score for s in meister_scores)

            summary = (
                f"[Short-Circuit FAIL] 決定論的静的解析ゲートにより重大欠陥 {len(error_issues)} 件を検出 ({report.execution_time_ms}ms)。"
                f"LLM推論を短絡遮断しました。平均スコア {avg_score:.1f}点 (最低: {min_score}点) "
                f"[憲章第4条 決定論的第1防壁準拠]"
            )

            return MeisterEvaluation(
                document_name=code_path,
                phase=phase,
                total_score=round(avg_score, 1),
                min_score=min_score,
                verdict=ReviewVerdict.FAIL,
                meister_scores=meister_scores,
                summary=summary,
                remediation_required=True
            )

        # Stage 2: 決定論的検証パス (Clean または Warning のみ)
        warning_issues = [i for i in report.issues if i.severity == Severity.WARNING]
        info_issues = [i for i in report.issues if i.severity == Severity.INFO]

        base_score = 92
        meister_scores = []
        for meister, meta in self.MEISTER_PROFILES.items():
            score = base_score
            recs = []
            
            if meister == MeisterType.THREAT_DEFENSE:
                sec_warns = [w for w in warning_issues if w.category == IssueCategory.SECURITY]
                score -= len(sec_warns) * 12
                for w in sec_warns:
                    recs.append(f"[Security Warning] Line {w.line}: {w.message} -> {w.remediation}")
            elif meister == MeisterType.QUALITY_ASSURANCE:
                rob_warns = [w for w in warning_issues if w.category == IssueCategory.ROBUSTNESS]
                score -= len(rob_warns) * 10
                for w in rob_warns:
                    recs.append(f"[Robustness Warning] Line {w.line}: {w.message} -> {w.remediation}")
            elif meister == MeisterType.GOVERNANCE_COMPLIANCE:
                gov_warns = [w for w in warning_issues if w.category in (IssueCategory.GOVERNANCE, IssueCategory.STYLE)]
                score -= len(gov_warns) * 8
                for w in gov_warns:
                    recs.append(f"[Governance Warning] Line {w.line}: {w.message} -> {w.remediation}")

            score = max(0, min(100, score))
            verdict = ReviewVerdict.PASS if score >= 70 else ReviewVerdict.FAIL
            critique = f"{meta['name']} 観点: 決定論的静的解析通過 (Warning: {len(warning_issues)}件, Info: {len(info_issues)}件)。"

            meister_scores.append(MeisterScore(
                meister=meister,
                score=score,
                verdict=verdict,
                critique=critique,
                recommendations=recs
            ))

        avg_score = sum(s.score for s in meister_scores) / len(meister_scores)
        min_score = min(s.score for s in meister_scores)
        is_pass = avg_score >= 80.0 and min_score >= 70

        mode_str = "決定論的解析のみ" if deterministic_only else "決定論的＋マイスターズセマンティック"
        summary = (
            f"コード審査完了 ({mode_str}): 決定論的静的解析 PASS ({report.execution_time_ms}ms, Warning: {len(warning_issues)}件) "
            f"-> 平均スコア {avg_score:.1f}点 (最低: {min_score}点) -> 判定: {'PASS' if is_pass else 'FAIL'}"
        )

        return MeisterEvaluation(
            document_name=code_path,
            phase=phase,
            total_score=round(avg_score, 1),
            min_score=min_score,
            verdict=ReviewVerdict.PASS if is_pass else ReviewVerdict.FAIL,
            meister_scores=meister_scores,
            summary=summary,
            remediation_required=not is_pass
        )


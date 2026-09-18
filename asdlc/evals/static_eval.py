import os
import re
import yaml
from pathlib import Path
from typing import List, Optional
from .models import EvaluationTier, EvalStatus, EvaluationItemResult

class StaticEvaluator:
    """
    Tier 1: 静的構造・スキーマ検証 (Static & Schema Evaluation)
    .agents/ 配下の Agent, Skill, Rule, Workflow の Frontmatter および構造を検証する。
    """

    def __init__(self, root_dir: Optional[Path] = None):
        if root_dir is None:
            self.root_dir = Path(__file__).resolve().parent.parent.parent
        else:
            self.root_dir = Path(root_dir)

    def evaluate_all(self) -> List[EvaluationItemResult]:
        results = []
        agents_dir = self.root_dir / ".agents"
        if not agents_dir.exists():
            return [
                EvaluationItemResult(
                    item_id=".agents_dir",
                    target_type="workspace",
                    tier=EvaluationTier.TIER_1_STATIC,
                    status=EvalStatus.FAIL,
                    score=0.0,
                    details=".agents ディレクトリが存在しません。",
                    recommendations=["リポジトリルートに .agents ディレクトリを作成してください。"]
                )
            ]

        # 1. Evaluate Agents
        agents_path = agents_dir / "agents"
        if agents_path.exists():
            for f in agents_path.glob("*.md"):
                results.append(self.evaluate_agent_file(f))

        # 2. Evaluate Skills
        skills_path = agents_dir / "skills"
        if skills_path.exists():
            for s_dir in skills_path.iterdir():
                if s_dir.is_dir():
                    skill_file = s_dir / "SKILL.md"
                    if skill_file.exists():
                        results.append(self.evaluate_skill_file(skill_file))
                    else:
                        results.append(
                            EvaluationItemResult(
                                item_id=s_dir.name,
                                target_type="skill",
                                tier=EvaluationTier.TIER_1_STATIC,
                                status=EvalStatus.FAIL,
                                score=0.0,
                                details=f"SKILL.md がディレクトリ内に見つかりません: {s_dir.name}",
                                recommendations=[f"{s_dir}/SKILL.md を作成してください。"]
                            )
                        )

        # 3. Evaluate Rules
        rules_path = agents_dir / "rules"
        if rules_path.exists():
            for r in rules_path.glob("*.md"):
                results.append(self.evaluate_rule_file(r))

        # 4. Evaluate Workflows
        workflows_path = agents_dir / "workflows"
        if workflows_path.exists():
            for w in workflows_path.glob("*.md"):
                results.append(self.evaluate_workflow_file(w))

        # 5. Evaluate Secret Leak Prevention (Zero-Secret Gate)
        results.append(self.evaluate_secret_leak_scan())

        return results


    def _parse_frontmatter(self, file_path: Path):
        content = file_path.read_text(encoding="utf-8")
        if not content.startswith("---"):
            return None, content
        parts = content.split("---", 2)
        if len(parts) < 3:
            return None, content
        try:
            fm = yaml.safe_load(parts[1])
            return fm, parts[2]
        except Exception:
            return None, content

    def evaluate_agent_file(self, file_path: Path) -> EvaluationItemResult:
        fm, body = self._parse_frontmatter(file_path)
        item_id = file_path.stem
        recs = []
        score = 100.0

        if fm is None:
            return EvaluationItemResult(
                item_id=item_id,
                target_type="agent",
                tier=EvaluationTier.TIER_1_STATIC,
                status=EvalStatus.FAIL,
                score=0.0,
                details="Frontmatter (YAML) が存在しないか無効です。",
                recommendations=["YAML Frontmatter ('---') を先頭に追加してください。"]
            )

        if "name" not in fm:
            score -= 30.0
            recs.append("Frontmatter に 'name' フィールドを追加してください。")
        if "description" not in fm or len(str(fm.get("description", ""))) < 10:
            score -= 30.0
            recs.append("Frontmatter に 10文字以上の具体的な 'description' を記載してください。")

        if len(body.strip()) < 100:
            score -= 30.0
            recs.append("エージェントペルソナ本文を具体化し、責務・原則・ワークフローを詳述してください。")

        status = EvalStatus.PASS if score >= 70.0 else EvalStatus.FAIL
        return EvaluationItemResult(
            item_id=f"agent:{item_id}",
            target_type="agent",
            tier=EvaluationTier.TIER_1_STATIC,
            status=status,
            score=max(0.0, score),
            details=f"Agent Frontmatter & 本文構造検証 (Score: {score:.1f})",
            recommendations=recs
        )

    def evaluate_skill_file(self, file_path: Path) -> EvaluationItemResult:
        fm, body = self._parse_frontmatter(file_path)
        item_id = file_path.parent.name
        recs = []
        score = 100.0

        if fm is None:
            return EvaluationItemResult(
                item_id=item_id,
                target_type="skill",
                tier=EvaluationTier.TIER_1_STATIC,
                status=EvalStatus.FAIL,
                score=0.0,
                details="Frontmatter (YAML) が存在しないか無効です。",
                recommendations=["YAML Frontmatter ('---') を先頭に追加してください。"]
            )

        if "name" not in fm:
            score -= 30.0
            recs.append("Frontmatter に 'name' フィールドを追加してください。")
        if "description" not in fm or len(str(fm.get("description", ""))) < 10:
            score -= 30.0
            recs.append("Frontmatter に 10文字以上の具体的な 'description' を記載してください。")

        if len(body.strip()) < 100:
            score -= 20.0
            recs.append("スキル本文に具体的な手順（Mermaid図、CLIコマンド、受入基準）を詳述してください。")

        status = EvalStatus.PASS if score >= 70.0 else EvalStatus.FAIL
        return EvaluationItemResult(
            item_id=f"skill:{item_id}",
            target_type="skill",
            tier=EvaluationTier.TIER_1_STATIC,
            status=status,
            score=max(0.0, score),
            details=f"Skill Frontmatter & 本文構造検証 (Score: {score:.1f})",
            recommendations=recs
        )

    def evaluate_rule_file(self, file_path: Path) -> EvaluationItemResult:
        fm, body = self._parse_frontmatter(file_path)
        item_id = file_path.stem
        recs = []
        score = 100.0

        if fm is None:
            return EvaluationItemResult(
                item_id=item_id,
                target_type="rule",
                tier=EvaluationTier.TIER_1_STATIC,
                status=EvalStatus.FAIL,
                score=0.0,
                details="Frontmatter (YAML) が存在しないか無効です。",
                recommendations=["YAML Frontmatter ('---') を先頭に追加してください。"]
            )

        if "description" not in fm:
            score -= 30.0
            recs.append("Frontmatter に 'description' フィールドを追加してください。")

        if "always_on" not in fm and "globs" not in fm:
            score -= 20.0
            recs.append("'always_on' または 'globs' トリガー条件を指定してください。")

        status = EvalStatus.PASS if score >= 70.0 else EvalStatus.FAIL
        return EvaluationItemResult(
            item_id=f"rule:{item_id}",
            target_type="rule",
            tier=EvaluationTier.TIER_1_STATIC,
            status=status,
            score=max(0.0, score),
            details=f"Rule Frontmatter & 制約文構造検証 (Score: {score:.1f})",
            recommendations=recs
        )

    def evaluate_workflow_file(self, file_path: Path) -> EvaluationItemResult:
        fm, body = self._parse_frontmatter(file_path)
        item_id = file_path.stem
        recs = []
        score = 100.0

        if fm is None:
            return EvaluationItemResult(
                item_id=item_id,
                target_type="workflow",
                tier=EvaluationTier.TIER_1_STATIC,
                status=EvalStatus.FAIL,
                score=0.0,
                details="Frontmatter (YAML) が存在しないか無効です。",
                recommendations=["YAML Frontmatter ('---') を先頭に追加してください。"]
            )

        if "title" not in fm:
            score -= 25.0
            recs.append("Frontmatter に 'title' フィールドを追加してください。")
        if "doc_type" not in fm:
            score -= 25.0
            recs.append("Frontmatter に 'doc_type: workflow' を追加してください。")

        status = EvalStatus.PASS if score >= 70.0 else EvalStatus.FAIL
        return EvaluationItemResult(
            item_id=f"workflow:{item_id}",
            target_type="workflow",
            tier=EvaluationTier.TIER_1_STATIC,
            status=status,
            score=max(0.0, score),
            details=f"Workflow Frontmatter & SOP構造検証 (Score: {score:.1f})",
            recommendations=recs
        )

    def evaluate_secret_leak_scan(self) -> EvaluationItemResult:
        """Tier 1: リポジトリ全体のシークレット・機微情報誤混入静的スキャン (Zero-Secret Gate)"""
        from ..security.secret_scanner import SecretScanner
        scanner = SecretScanner()
        findings = scanner.scan_directory(self.root_dir)

        if not findings:
            return EvaluationItemResult(
                item_id="security:secret_leak_prevention",
                target_type="workspace",
                tier=EvaluationTier.TIER_1_STATIC,
                status=EvalStatus.PASS,
                score=100.0,
                details="全ファイル静的スキャン完了: シークレット・機微情報の誤混入は 0 件です（Zero-Secret達成）。",
                recommendations=[]
            )
        else:
            recs = [f"{f.file_path}:{f.line_number} [{f.rule_id}] {f.secret_type} ({f.masked_snippet})" for f in findings[:10]]
            return EvaluationItemResult(
                item_id="security:secret_leak_prevention",
                target_type="workspace",
                tier=EvaluationTier.TIER_1_STATIC,
                status=EvalStatus.FAIL,
                score=0.0,
                details=f"シークレット・機微情報の誤混入を {len(findings)} 件検知しました！直ちに削除・無害化してください。",
                recommendations=recs
            )


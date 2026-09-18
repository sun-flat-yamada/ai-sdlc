import time
import shutil
import subprocess
from pathlib import Path
from typing import Optional, List, Dict, Any
from .models import (
    Severity,
    IssueCategory,
    StaticAnalysisIssue,
    StaticAnalysisReport
)
from .rules.python_rules import PythonRuleSet
from .rules.typescript_rules import TypeScriptRuleSet
from .rules.go_rules import GoRuleSet
from .rules.c_rules import CRuleSet
from .rules.cpp_rules import CPPRuleSet
from .rules.csharp_rules import CSharpRuleSet

class DeterministicCodeReviewer:
    """
    決定論的コード検証エンジン (Deterministic Verification Engine)
    - ゼロハルシネーション・100%再現性
    - Dual-Engine (Native External CLI + Zero-Dependency Built-in Rules)
    - Short-Circuiting (重大欠陥検知時の即時遮断)
    """

    EXT_LANG_MAP = {
        ".py": "python",
        ".ts": "typescript",
        ".tsx": "typescript",
        ".js": "typescript",
        ".jsx": "typescript",
        ".go": "go",
        ".c": "c",
        ".h": "c",
        ".cpp": "cpp",
        ".hpp": "cpp",
        ".cc": "cpp",
        ".cxx": "cpp",
        ".cs": "csharp",
    }

    RULE_SETS = {
        "python": PythonRuleSet,
        "typescript": TypeScriptRuleSet,
        "go": GoRuleSet,
        "c": CRuleSet,
        "cpp": CPPRuleSet,
        "csharp": CSharpRuleSet,
    }

    @classmethod
    def is_source_code(cls, file_path: str) -> bool:
        ext = Path(file_path).suffix.lower()
        return ext in cls.EXT_LANG_MAP

    @classmethod
    def detect_language(cls, file_path: str) -> str:
        ext = Path(file_path).suffix.lower()
        return cls.EXT_LANG_MAP.get(ext, "unknown")

    def run_external_linter(self, file_path: str, lang: str) -> List[StaticAnalysisIssue]:
        """
        環境に外部CLIツールがインストールされている場合に実行する
        """
        issues: List[StaticAnalysisIssue] = []
        path_obj = Path(file_path)
        if not path_obj.exists():
            return issues

        try:
            if lang == "python" and shutil.which("ruff"):
                res = subprocess.run(
                    ["ruff", "check", "--output-format=text", str(path_obj)],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if res.returncode != 0 and res.stdout:
                    for line in res.stdout.splitlines():
                        parts = line.split(":")
                        if len(parts) >= 4:
                            try:
                                lineno = int(parts[1])
                                colno = int(parts[2])
                                msg = ":".join(parts[3:]).strip()
                                issues.append(StaticAnalysisIssue(
                                    file_path=file_path,
                                    line=lineno,
                                    column=colno,
                                    rule_id="EXT-RUFF",
                                    severity=Severity.WARNING,
                                    category=IssueCategory.STYLE,
                                    message=f"[Ruff] {msg}",
                                    remediation="Ruffの指摘に従ってコードを修正してください。"
                                ))
                            except ValueError:
                                pass
        except Exception:
            # 外部ツール実行エラー時は内蔵エンジンで十分カバーするため黙殺
            pass

        return issues

    def review(
        self,
        file_path: str,
        content: Optional[str] = None,
        lang: Optional[str] = None
    ) -> StaticAnalysisReport:
        """
        対象コードに対する決定論的静的解析を実行し、レポートを生成する
        """
        start_time = time.perf_counter()

        if content is None:
            p = Path(file_path)
            if not p.exists():
                raise FileNotFoundError(f"ファイルが見つかりません: {file_path}")
            with open(p, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()

        detected_lang = (lang or self.detect_language(file_path)).lower()
        rule_class = self.RULE_SETS.get(detected_lang)

        issues: List[StaticAnalysisIssue] = []
        tool_name = "Built-in Deterministic Rule Engine"

        # 1. 内蔵決定論的ルールエンジンの実行 (Zero-Dependency Base Engine)
        if rule_class:
            issues.extend(rule_class.evaluate(file_path, content))

        # 2. 外部ネイティブツールの実行（利用可能な場合）
        ext_issues = self.run_external_linter(file_path, detected_lang)
        if ext_issues:
            tool_name += " + Native External CLI"
            issues.extend(ext_issues)

        # 重複排除（同じ行・列・ルールID）
        unique_issues = []
        seen = set()
        for iss in issues:
            k = (iss.line, iss.column, iss.rule_id)
            if k not in seen:
                seen.add(k)
                unique_issues.append(iss)

        # 重大度降順 (ERROR > WARNING > INFO), 行番号昇順にソート
        severity_order = {Severity.ERROR: 0, Severity.WARNING: 1, Severity.INFO: 2}
        unique_issues.sort(key=lambda x: (severity_order.get(x.severity, 99), x.line, x.column))

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        has_error = any(i.severity == Severity.ERROR for i in unique_issues)

        return StaticAnalysisReport(
            file_path=file_path,
            language=detected_lang,
            tool_name=tool_name,
            issues=unique_issues,
            execution_time_ms=round(elapsed_ms, 2),
            is_short_circuited=has_error
        )

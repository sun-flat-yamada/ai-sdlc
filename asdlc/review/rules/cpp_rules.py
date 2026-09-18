import re
from typing import List
from ..models import Severity, IssueCategory, StaticAnalysisIssue
from .c_rules import CRuleSet

class CPPRuleSet:
    """C++ 決定論的静的解析ルールセット (モダンC++ & RAII & 型安全性)"""

    RULES = [
        # 1. catch (...) の完全握りつぶし
        (
            re.compile(r"""catch\s*\(\s*\.\.\.\s*\)\s*\{\s*\}"""),
            "CPP-ROB-EMPTY-CATCH-ALL",
            Severity.ERROR,
            IssueCategory.ROBUSTNESS,
            "すべての例外を無言で破棄する 'catch (...) {}' が検出されました。",
            "例外の型 (std::exception&) をキャッチしてログ記録を行うか、上位へ再送出 (throw;) してください。",
            None
        ),
        # 2. 生 new / delete の直接呼び出し (RAII違反)
        (
            re.compile(r"""\b(?:new\s+[A-Za-z0-9_]+|delete\s+[A-Za-z0-9_]+)\b"""),
            "CPP-ROB-RAW-NEW-DELETE",
            Severity.WARNING,
            IssueCategory.ROBUSTNESS,
            "生ポインタの手動管理 ('new' / 'delete') が検出されました (メモリリーク・二重解放リスク)。",
            "std::unique_ptr または std::make_unique / std::shared_ptr (RAII) を使用してください。",
            "CWE-401"
        ),
        # 3. reinterpret_cast の乱用
        (
            re.compile(r"""\breinterpret_cast\s*<"""),
            "CPP-SEC-REINTERPRET-CAST",
            Severity.WARNING,
            IssueCategory.SECURITY,
            "低レベルで未定義動作を引き起こしやすい 'reinterpret_cast' が使用されています。",
            "static_cast や dynamic_cast、または型安全な設計（variant / any）への見直しを検討してください。",
            None
        )
    ]

    @classmethod
    def evaluate(cls, file_path: str, content: str) -> List[StaticAnalysisIssue]:
        issues: List[StaticAnalysisIssue] = []

        # C言語共通の危険関数（gets, strcpy, sprintf 等）を包含
        issues.extend(CRuleSet.evaluate(file_path, content))

        lines = content.splitlines()
        for idx, line in enumerate(lines, start=1):
            trimmed = line.strip()
            if trimmed.startswith(("//", "/*", "*")):
                continue

            for pattern, rule_id, sev, cat, msg, rem, cwe in cls.RULES:
                m = pattern.search(line)
                if m:
                    # コメント行や既存の指摘との重複を考慮
                    issues.append(StaticAnalysisIssue(
                        file_path=file_path,
                        line=idx,
                        column=m.start() + 1,
                        rule_id=rule_id,
                        severity=sev,
                        category=cat,
                        message=msg,
                        snippet=line.strip()[:80],
                        remediation=rem,
                        cwe_id=cwe
                    ))

        return issues

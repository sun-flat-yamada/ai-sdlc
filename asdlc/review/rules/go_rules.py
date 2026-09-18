import re
from typing import List
from ..models import Severity, IssueCategory, StaticAnalysisIssue
from .base import SecretScanningRule

class GoRuleSet:
    """Go 決定論的静的解析ルールセット"""

    RULES = [
        # 1. 未チェックエラー (_ = err)
        (
            re.compile(r"""(?:_\s*,\s*err\s*:?=|_\s*=\s*err\b)"""),
            "GO-ROB-UNCHECKED-ERROR",
            Severity.ERROR,
            IssueCategory.ROBUSTNESS,
            "エラーの握りつぶし・未チェック ('_ = err') が検出されました。",
            "if err != nil { return err } による明示的なエラーハンドリングを徹底してください。",
            None
        ),
        # 2. 本番コードでの panic() 乱用
        (
            re.compile(r"""\bpanic\s*\("""),
            "GO-ROB-PANIC-USAGE",
            Severity.WARNING,
            IssueCategory.ROBUSTNESS,
            "プロセスをクラッシュさせる 'panic()' の直接呼び出しが検出されました。",
            "panicを避け、error型を返却して呼び出し元で制御してください（main初期化時を除く）。",
            None
        ),
        # 3. unsafe.Pointer の使用
        (
            re.compile(r"""\bunsafe\.Pointer\b"""),
            "GO-SEC-UNSAFE-POINTER",
            Severity.WARNING,
            IssueCategory.SECURITY,
            "メモリ安全性を破壊する 'unsafe.Pointer' の使用が検出されました。",
            "標準パッケージの安全な抽象化（reflectや型安全な構造体）を使用してください。",
            None
        ),
        # 4. fmt.Sprintf による動的SQL構築 (CWE-89)
        (
            re.compile(r"""fmt\.Sprintf\s*\(\s*["'](?:SELECT|INSERT|UPDATE|DELETE).*?%[svq]""", re.IGNORECASE),
            "GO-SEC-SQL-INJECTION",
            Severity.ERROR,
            IssueCategory.SECURITY,
            "fmt.Sprintf による動的SQL文字列構築が検出されました (SQLインジェクション脆弱性)。",
            "database/sql のパラメータ化クエリ（db.Query(\"SELECT ... WHERE id = ?\", id)）を使用してください。",
            "CWE-89"
        )
    ]

    @classmethod
    def evaluate(cls, file_path: str, content: str) -> List[StaticAnalysisIssue]:
        issues: List[StaticAnalysisIssue] = []

        # シークレットスキャン
        issues.extend(SecretScanningRule().evaluate(file_path, content))

        lines = content.splitlines()
        for idx, line in enumerate(lines, start=1):
            trimmed = line.strip()
            if trimmed.startswith("//"):
                continue

            for pattern, rule_id, sev, cat, msg, rem, cwe in cls.RULES:
                m = pattern.search(line)
                if m:
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

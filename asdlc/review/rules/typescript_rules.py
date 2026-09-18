import re
from typing import List
from ..models import Severity, IssueCategory, StaticAnalysisIssue
from .base import SecretScanningRule

class TypeScriptRuleSet:
    """TypeScript / JavaScript 決定論的静的解析ルールセット"""

    RULES = [
        # 1. eval / Function
        (
            re.compile(r"""\b(?:eval\s*\(|new\s+Function\s*\()"""),
            "TS-SEC-DANGEROUS-EVAL",
            Severity.ERROR,
            IssueCategory.SECURITY,
            "危険な動的コード実行関数 'eval()' または 'new Function()' が使用されています。",
            "動的実行を排し、安全な標準関数またはJSONパーサーを使用してください。",
            "CWE-95"
        ),
        # 2. 空の catch ブロック (catch (e) {})
        (
            re.compile(r"""catch\s*\([^\)]*\)\s*\{\s*\}"""),
            "TS-ROB-EMPTY-CATCH",
            Severity.ERROR,
            IssueCategory.ROBUSTNESS,
            "例外の完全な握りつぶし (空の catch ブロック) が検出されました。",
            "例外を適切にロギングするか、上位層へ再スローしてください。",
            None
        ),
        # 3. SQL 文字列テンプレート結合 (CWE-89)
        (
            re.compile(r"""(?:SELECT|INSERT|UPDATE|DELETE)\s+.*?\$\{[^\}]+\}""", re.IGNORECASE),
            "TS-SEC-SQL-INJECTION",
            Severity.ERROR,
            IssueCategory.SECURITY,
            "テンプレートリテラルによる動的SQL文字列構築が検出されました (SQLインジェクション脆弱性)。",
            "ORMまたはパラメータ化クエリ（Prepared Statement）を使用してください。",
            "CWE-89"
        ),
        # 4. @ts-ignore / @ts-nocheck の無秩序な使用
        (
            re.compile(r"""//\s*@ts-(?:ignore|nocheck)"""),
            "TS-GOV-TS-IGNORE",
            Severity.WARNING,
            IssueCategory.GOVERNANCE,
            "型チェックを無効化する '@ts-ignore' または '@ts-nocheck' が使用されています。",
            "型定義を正しく修正するか、型ガード（Type Guards）を導入してください。",
            None
        ),
        # 5. any 型の乱用 (: any, as any)
        (
            re.compile(r"""(?::\s*any\b|as\s+any\b)"""),
            "TS-ROB-ANY-TYPE",
            Severity.WARNING,
            IssueCategory.ROBUSTNESS,
            "型安全性を放棄する 'any' 型の使用が検出されました。",
            "厳格な型定義（Zodスキーマ、unknown型、ジェネリクス）に置き換えてください。",
            None
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
            if trimmed.startswith("//") and "@ts-" not in trimmed:
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

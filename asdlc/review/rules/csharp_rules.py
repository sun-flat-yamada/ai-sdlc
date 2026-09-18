import re
from typing import List
from ..models import Severity, IssueCategory, StaticAnalysisIssue
from .base import SecretScanningRule

class CSharpRuleSet:
    """C# (.NET) 決定論的静的解析ルールセット"""

    RULES = [
        # 1. 危険な BinaryFormatter デシリアライゼーション (CWE-502)
        (
            re.compile(r"""\b(?:BinaryFormatter|NetDataContractSerializer)\b"""),
            "CS-SEC-INSECURE-DESERIALIZATION",
            Severity.ERROR,
            IssueCategory.SECURITY,
            "任意コード実行脆弱性を引き起こす危険な 'BinaryFormatter' が使用されています（.NET公式で非推奨・禁止）。",
            "System.Text.Json (JsonSerializer) または Protocol Buffers 等の安全なシリアライザーを使用してください。",
            "CWE-502"
        ),
        # 2. 空の catch ブロック (catch (Exception) {} または catch {})
        (
            re.compile(r"""catch(?:\s*\([^\)]*\))?\s*\{\s*\}"""),
            "CS-ROB-EMPTY-CATCH",
            Severity.ERROR,
            IssueCategory.ROBUSTNESS,
            "例外の完全な握りつぶし (空の catch ブロック) が検出されました。",
            "ILogger 等を用いて例外を記録するか、'throw;' で再送出してください。",
            None
        ),
        # 3. 文字列補間による動的SQL (CWE-89)
        (
            re.compile(r"""(?:SqlCommand|ExecuteSql(?:Raw)?)\s*\(\s*\$["'](?:SELECT|INSERT|UPDATE|DELETE).*?\{""", re.IGNORECASE),
            "CS-SEC-SQL-INJECTION",
            Severity.ERROR,
            IssueCategory.SECURITY,
            "文字列補間 ($) による生SQLクエリ構築が検出されました (SQLインジェクション脆弱性)。",
            "SqlParameter または EF Core のパラメータ化クエリ（FromSqlInterpolated 等）を使用してください。",
            "CWE-89"
        ),
        # 4. Thread.Abort() の使用
        (
            re.compile(r"""\bThread\.CurrentThread\.Abort\(\)|\b[A-Za-z0-9_]+\.Abort\(\)"""),
            "CS-ROB-THREAD-ABORT",
            Severity.WARNING,
            IssueCategory.ROBUSTNESS,
            "未定義の状態破壊を引き起こす 'Thread.Abort()' が使用されています。",
            "CancellationToken による協調的中断パターンを使用してください。",
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

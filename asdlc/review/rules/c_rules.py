import re
from typing import List
from ..models import Severity, IssueCategory, StaticAnalysisIssue
from .base import SecretScanningRule

class CRuleSet:
    """C言語 決定論的静的解析ルールセット (CWE & メモリ安全性)"""

    RULES = [
        # 1. gets() の使用 (CWE-242: 絶対に使用してはならない危険な関数)
        (
            re.compile(r"""\bgets\s*\("""),
            "C-SEC-BANNED-GETS",
            Severity.ERROR,
            IssueCategory.SECURITY,
            "バッファオーバーフローを確実に引き起こす危険な標準関数 'gets()' が使用されています。",
            "fgets() を使用し、読み込み最大バッファサイズを明示的に制限してください。",
            "CWE-242"
        ),
        # 2. strcpy() / strcat() の使用 (CWE-120)
        (
            re.compile(r"""\b(?:strcpy|strcat)\s*\("""),
            "C-SEC-UNBOUNDED-STRCPY",
            Severity.ERROR,
            IssueCategory.SECURITY,
            "境界チェックを行わない 'strcpy()' または 'strcat()' が使用されています (バッファオーバーフロー脆弱性)。",
            "strncpy(), strncat(), または安全な境界指定関数 (strlcpy / C11 strcpy_s) を使用してください。",
            "CWE-120"
        ),
        # 3. sprintf() の使用 (CWE-120)
        (
            re.compile(r"""\bsprintf\s*\("""),
            "C-SEC-UNBOUNDED-SPRINTF",
            Severity.ERROR,
            IssueCategory.SECURITY,
            "バッファサイズ制限を行わない 'sprintf()' が使用されています。",
            "snprintf() を使用し、第2引数に出力先バッファ長 (sizeof) を渡してください。",
            "CWE-120"
        ),
        # 4. system() コマンド実行 (CWE-78)
        (
            re.compile(r"""\bsystem\s*\("""),
            "C-SEC-COMMAND-EXEC-SYSTEM",
            Severity.ERROR,
            IssueCategory.SECURITY,
            "シェルを直接呼び出す 'system()' が使用されています (コマンドインジェクションのリスク)。",
            "execve() / posix_spawn() を使用し、シェル展開を経由せず固定引数で呼び出してください。",
            "CWE-78"
        ),
        # 5. scanf() の %s 境界未指定 (CWE-120)
        (
            re.compile(r"""\bscanf\s*\(\s*["'][^"']*%s[^"']*["']"""),
            "C-SEC-SCANF-STRING-OVERFLOW",
            Severity.ERROR,
            IssueCategory.SECURITY,
            "scanf() で幅指定のない '%s' フォーマットが使用されています (バッファオーバーフロー脆弱性)。",
            "scanf(\"%31s\", buf) のようにバッファ上限幅を明示するか、fgets() を使用してください。",
            "CWE-120"
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
            if trimmed.startswith(("//", "/*", "*")):
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

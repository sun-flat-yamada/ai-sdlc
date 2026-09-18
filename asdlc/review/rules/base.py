import re
from typing import List, Optional
from ..models import Severity, IssueCategory, StaticAnalysisIssue

class RuleDefinition:
    """決定論的解析ルールの基底クラス"""
    rule_id: str
    severity: Severity
    category: IssueCategory
    message: str
    remediation: Optional[str] = None
    cwe_id: Optional[str] = None

    def evaluate(self, file_path: str, content: str) -> List[StaticAnalysisIssue]:
        raise NotImplementedError

class SecretScanningRule(RuleDefinition):
    """共通シークレット・トークン・APIキーのハードコード検出 (CWE-798)"""
    rule_id = "SEC-001-HARDCODED-SECRET"
    severity = Severity.ERROR
    category = IssueCategory.SECURITY
    message = "機密情報（APIキー、シークレットトークン、秘密鍵）がハードコードされています。"
    remediation = "環境変数またはシークレットマネージャー（Vault, AWS Secrets Manager, GCP Secret Manager等）から取得してください。"
    cwe_id = "CWE-798"

    SECRET_PATTERNS = [
        (re.compile(r"""(?i)(?:api_key|apikey|secret_key|private_key|auth_token|bearer|access_token|password|passwd)\s*[:=]\s*["']([A-Za-z0-9_\-\.]{16,})["']"""), "ハードコードされた認証シークレット"),
        (re.compile(r"""-----BEGIN (?:RSA )?PRIVATE KEY-----"""), "平文の秘密鍵ブロック"),
        (re.compile(r"""(?i)ghp_[A-Za-z0-9]{36}"""), "GitHub Personal Access Token"),
        (re.compile(r"""(?i)AKIA[0-9A-Z]{16}"""), "AWS Access Key ID"),
    ]

    def evaluate(self, file_path: str, content: str) -> List[StaticAnalysisIssue]:
        issues = []
        lines = content.splitlines()
        for idx, line in enumerate(lines, start=1):
            for pat, desc in self.SECRET_PATTERNS:
                m = pat.search(line)
                if m:
                    # コメント行やプレースホルダー文字列の除外チェック
                    trimmed = line.strip()
                    if trimmed.startswith(("#", "//", "/*", "*")):
                        continue
                    if any(dummy in line.lower() for dummy in ["example", "dummy", "placeholder", "your_", "my_secret_here", "test"]):
                        continue
                    
                    issues.append(StaticAnalysisIssue(
                        file_path=file_path,
                        line=idx,
                        column=m.start() + 1,
                        rule_id=self.rule_id,
                        severity=self.severity,
                        category=self.category,
                        message=f"{desc}: {self.message}",
                        snippet=line.strip()[:80],
                        remediation=self.remediation,
                        cwe_id=self.cwe_id
                    ))
        return issues

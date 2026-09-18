"""
ASDLC Secret Scanner
Comprehensive static scanner for preventing unintentional secret leaks across code, docs, and configurations.
Incorporates industry-standard rules from OWASP, Gitleaks, and proud-noether defense-in-depth architecture.
"""
import math
import re
from pathlib import Path
from typing import List, Dict, Optional, Any, Set
from pydantic import BaseModel, Field

class SecretFinding(BaseModel):
    file_path: str
    line_number: int
    rule_id: str
    secret_type: str
    masked_snippet: str
    entropy: float = 0.0
    severity: str = "CRITICAL"


class SecretScanner:
    """
    リポジトリ全体または単一ファイルからシークレット誤混入を検知するセキュリティスキャナー
    """

    PATTERNS: Dict[str, Dict[str, Any]] = {
        "SEC-001-GITHUB-PAT": {
            "name": "GitHub Personal Access Token (Classic / App)",
            "regex": re.compile(r'\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9_]{36}\b'),
            "severity": "CRITICAL"
        },
        "SEC-001-GITHUB-FINE-GRAINED": {
            "name": "GitHub Fine-Grained Personal Access Token",
            "regex": re.compile(r'\bgithub_pat_[a-zA-Z0-9_]{82}\b'),
            "severity": "CRITICAL"
        },
        "SEC-002-OPENAI-KEY": {
            "name": "OpenAI / LLM API Key",
            "regex": re.compile(r'\bsk-(?!(?:ant-))(?:proj-|live-|test-)?[a-zA-Z0-9_\-]{20,}\b'),
            "severity": "CRITICAL"
        },
        "SEC-002-ANTHROPIC-KEY": {
            "name": "Anthropic Claude API Key",
            "regex": re.compile(r'\bsk-ant-api03-[a-zA-Z0-9_\-]{32,}\b'),
            "severity": "CRITICAL"
        },
        "SEC-003-AWS-KEY": {
            "name": "AWS Access Key ID",
            "regex": re.compile(r'\b(?:AKIA|ABIA|ACCA|ASIA)[0-9A-Z]{16}\b'),
            "severity": "CRITICAL"
        },
        "SEC-004-GOOGLE-API-KEY": {
            "name": "Google Cloud / Gemini API Key",
            "regex": re.compile(r'\bAIza[0-9A-Za-z\-_]{35}\b'),
            "severity": "CRITICAL"
        },
        "SEC-005-PRIVATE-KEY": {
            "name": "Private Cryptographic Key (RSA/EC/OpenSSH/PGP)",
            "regex": re.compile(r'-----BEGIN (?:RSA |EC |DSA |OPENSSH |PGP |ENCRYPTED )?PRIVATE KEY-----'),
            "severity": "CRITICAL"
        },
        "SEC-006-SLACK-WEBHOOK": {
            "name": "Slack Incoming Webhook URL",
            "regex": re.compile(r'https:\/\/hooks\.slack\.com\/services\/T[a-zA-Z0-9_]+\/B[a-zA-Z0-9_]+\/[a-zA-Z0-9_]+'),
            "severity": "CRITICAL"
        },
        "SEC-006-SLACK-TOKEN": {
            "name": "Slack Bot / User Token",
            "regex": re.compile(r'\bxox[baprs]-[0-9a-zA-Z]{10,48}\b'),
            "severity": "CRITICAL"
        },
        "SEC-007-GENERIC-SECRET-ASSIGNMENT": {
            "name": "Hardcoded Secret Assignment",
            "regex": re.compile(
                r'(?i)\b(?:api[_-]?key|secret[_-]?key|access[_-]?token|auth[_-]?token|client_secret|db_password)\s*[:=]\s*[\'"][^\s\'"]{12,}[\'"]'
            ),
            "severity": "HIGH"
        },

    }

    IGNORE_DIRS: Set[str] = {
        ".git",
        ".pytest_cache",
        "__pycache__",
        ".venv",
        "venv",
        "env",
        "node_modules",
        "dist",
        "build",
        ".aegis",
        ".aegis_local",
        "asdlc.egg-info",
        "scratch"
    }

    IGNORE_FILES: Set[str] = {
        "package-lock.json",
        ".env.example"
    }

    IGNORE_EXTENSIONS: Set[str] = {
        ".pyc",
        ".png",
        ".jpg",
        ".jpeg",
        ".gif",
        ".ico",
        ".svg",
        ".woff",
        ".woff2",
        ".zip",
        ".tar",
        ".gz",
        ".pdf"
    }

    # proud-noether / Gitleaks 準拠のプレースホルダー・モック免責ワード
    SAFE_PLACEHOLDERS: List[str] = [
        "mock",
        "dummy",
        "example",
        "sample",
        "placeholder",
        "xxxx",
        "0000",
        "test",
        "fake",
        "ghp_xxxx",
        "your-enterprise-slug",
        "your_",
        "redacted",
        "filtered"
    ]

    @staticmethod
    def calculate_entropy(text: str) -> float:
        """シャノンエントロピー計算（ランダム文字列の不確実性測定）"""
        if not text:
            return 0.0
        prob = [float(text.count(c)) / len(text) for c in set(text)]
        return - sum([p * math.log(p) / math.log(2.0) for p in prob])

    @classmethod
    def mask_secret(cls, raw: str) -> str:
        """ログやレポート出力用にシークレットを部分マスキング (先頭4文字 + **** + 末尾2文字)"""
        if len(raw) <= 8:
            return "*" * len(raw)
        return f"{raw[:4]}****{raw[-2:]}"

    def is_safe_placeholder(self, text: str) -> bool:
        """安全なダミー・モック文字列であるかを判定"""
        lower = text.lower()
        return any(ph in lower for ph in self.SAFE_PLACEHOLDERS)

    def scan_text(self, text: str, file_path: str = "<string>") -> List[SecretFinding]:
        findings: List[SecretFinding] = []
        lines = text.splitlines()

        for idx, line in enumerate(lines, 1):
            stripped = line.strip()
            # 行全体がセーフプレースホルダーを含む場合は除外
            if self.is_safe_placeholder(stripped):
                continue

            for rule_id, spec in self.PATTERNS.items():
                for match in spec["regex"].finditer(line):
                    matched_text = match.group(0)
                    
                    # 一致テキスト内にセーフプレースホルダーが含まれる場合は除外
                    if self.is_safe_placeholder(matched_text):
                        continue

                    entropy = self.calculate_entropy(matched_text)
                    findings.append(
                        SecretFinding(
                            file_path=file_path,
                            line_number=idx,
                            rule_id=rule_id,
                            secret_type=spec["name"],
                            masked_snippet=self.mask_secret(matched_text),
                            entropy=round(entropy, 2),
                            severity=spec["severity"]
                        )
                    )

        return findings

    def scan_file(self, file_path: Path | str) -> List[SecretFinding]:
        p = Path(file_path)
        if not p.is_file():
            return []
        if p.name in self.IGNORE_FILES:
            return []
        if p.suffix.lower() in self.IGNORE_EXTENSIONS:
            return []

        try:
            content = p.read_text(encoding="utf-8", errors="ignore")
            return self.scan_text(content, file_path=str(p))
        except Exception:
            return []

    def scan_directory(self, root_dir: Path | str = ".") -> List[SecretFinding]:
        """リポジトリ全体を再帰スキャン"""
        root = Path(root_dir).resolve()
        all_findings: List[SecretFinding] = []

        for p in root.rglob("*"):
            if p.is_file():
                if any(part in self.IGNORE_DIRS for part in p.parts):
                    continue
                findings = self.scan_file(p)
                all_findings.extend(findings)

        return all_findings

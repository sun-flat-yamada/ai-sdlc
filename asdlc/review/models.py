from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class Severity(str, Enum):
    ERROR = "ERROR"      # 致命的欠陥・即時FAIL対象 (Short-Circuit)
    WARNING = "WARNING"  # 潜在的不具合・減点対象
    INFO = "INFO"        # スタイル・可読性推奨

class IssueCategory(str, Enum):
    SECURITY = "SECURITY"      # OWASP / CWE 脆弱性・シークレット
    ROBUSTNESS = "ROBUSTNESS"  # 例外処理、未初期化ポインタ、未チェックエラー
    SYNTAX = "SYNTAX"          # 構文・インポートエラー
    STYLE = "STYLE"            # フォーマット、命名規則
    GOVERNANCE = "GOVERNANCE"  # 全社ルール、循環参照、隔離アーキテクチャ

class StaticAnalysisIssue(BaseModel):
    file_path: str
    line: int = Field(ge=1, default=1)
    column: int = Field(ge=1, default=1)
    rule_id: str
    severity: Severity
    category: IssueCategory
    message: str
    snippet: Optional[str] = None
    remediation: Optional[str] = None
    cwe_id: Optional[str] = None

class StaticAnalysisReport(BaseModel):
    file_path: str
    language: str
    tool_name: str
    issues: List[StaticAnalysisIssue] = Field(default_factory=list)
    execution_time_ms: float = 0.0
    is_short_circuited: bool = False

    @property
    def has_errors(self) -> bool:
        return any(i.severity == Severity.ERROR for i in self.issues)

    @property
    def error_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == Severity.ERROR)

    @property
    def warning_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == Severity.WARNING)

    @property
    def info_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == Severity.INFO)

    def to_sarif_dict(self) -> Dict[str, Any]:
        """
        OASIS SARIF v2.1.0 規格準拠のディクショナリを生成
        """
        results = []
        rules_map = {}

        for issue in self.issues:
            rule_level = "error" if issue.severity == Severity.ERROR else (
                "warning" if issue.severity == Severity.WARNING else "note"
            )
            
            if issue.rule_id not in rules_map:
                rules_map[issue.rule_id] = {
                    "id": issue.rule_id,
                    "name": issue.rule_id,
                    "shortDescription": {"text": issue.message},
                    "defaultConfiguration": {"level": rule_level},
                    "properties": {
                        "category": issue.category.value,
                        "cwe": issue.cwe_id or ""
                    }
                }

            result_obj: Dict[str, Any] = {
                "ruleId": issue.rule_id,
                "level": rule_level,
                "message": {"text": issue.message},
                "locations": [{
                    "physicalLocation": {
                        "artifactLocation": {"uri": issue.file_path.replace("\\", "/")},
                        "region": {
                            "startLine": issue.line,
                            "startColumn": issue.column
                        }
                    }
                }]
            }
            if issue.remediation:
                result_obj["fixes"] = [{
                    "description": {"text": issue.remediation}
                }]
            results.append(result_obj)

        sarif = {
            "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
            "version": "2.1.0",
            "runs": [{
                "tool": {
                    "driver": {
                        "name": f"ASDLC Deterministic Reviewer ({self.tool_name})",
                        "semanticVersion": "1.0.0",
                        "rules": list(rules_map.values())
                    }
                },
                "results": results
            }]
        }
        return sarif

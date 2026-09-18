import ast
import re
from typing import List
from ..models import Severity, IssueCategory, StaticAnalysisIssue
from .base import RuleDefinition, SecretScanningRule

class PythonRuleSet:
    """Python決定論的静的解析ルールセット (AST & SAST)"""

    @classmethod
    def evaluate(cls, file_path: str, content: str) -> List[StaticAnalysisIssue]:
        issues: List[StaticAnalysisIssue] = []

        # 1. 構文解析 (AST Syntax Check)
        try:
            tree = ast.parse(content, filename=file_path)
        except SyntaxError as e:
            return [StaticAnalysisIssue(
                file_path=file_path,
                line=e.lineno or 1,
                column=e.offset or 1,
                rule_id="PY-SYNTAX-ERROR",
                severity=Severity.ERROR,
                category=IssueCategory.SYNTAX,
                message=f"Python構文エラー (SyntaxError): {e.msg}",
                snippet=e.text.strip() if e.text else None,
                remediation="構文を修正してPython 3.10+で正しくパースできるようにしてください。"
            )]

        # 2. シークレットスキャン
        issues.extend(SecretScanningRule().evaluate(file_path, content))

        # 3. AST走査による決定論的検査
        for node in ast.walk(tree):
            # A. 危険な eval / exec (CWE-95)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                if node.func.id in ("eval", "exec"):
                    issues.append(StaticAnalysisIssue(
                        file_path=file_path,
                        line=node.lineno,
                        column=node.col_offset + 1,
                        rule_id="PY-SEC-DANGEROUS-EVAL",
                        severity=Severity.ERROR,
                        category=IssueCategory.SECURITY,
                        message=f"危険な動的コード実行関数 '{node.func.id}()' が呼び出されています。",
                        remediation="eval() / exec() を使用せず、安全なパーサー（ast.literal_evalやJSON等）に置き換えてください。",
                        cwe_id="CWE-95"
                    ))

            # B. コマンドインジェクション (subprocess with shell=True, os.system) (CWE-78)
            if isinstance(node, ast.Call):
                # os.system(...)
                if isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name):
                    if node.func.value.id == "os" and node.func.attr == "system":
                        issues.append(StaticAnalysisIssue(
                            file_path=file_path,
                            line=node.lineno,
                            column=node.col_offset + 1,
                            rule_id="PY-SEC-COMMAND-INJECTION",
                            severity=Severity.ERROR,
                            category=IssueCategory.SECURITY,
                            message="危険な 'os.system()' によるシェル実行が検出されました。",
                            remediation="'subprocess.run()' で引数をリスト形式で渡し、shell=Trueを避けてください。",
                            cwe_id="CWE-78"
                        ))
                # subprocess.run(..., shell=True)
                for kw in node.keywords:
                    if kw.arg == "shell" and isinstance(kw.value, ast.Constant) and kw.value.value is True:
                        issues.append(StaticAnalysisIssue(
                            file_path=file_path,
                            line=node.lineno,
                            column=node.col_offset + 1,
                            rule_id="PY-SEC-SUBPROCESS-SHELL-TRUE",
                            severity=Severity.ERROR,
                            category=IssueCategory.SECURITY,
                            message="subprocess実行で 'shell=True' が有効化されており、コマンドインジェクションの脆弱性があります。",
                            remediation="shell=False（デフォルト）とし、引数をリスト形式で渡してください。",
                            cwe_id="CWE-78"
                        ))

            # C. 安全でないデシリアライゼーション (pickle.loads) (CWE-502)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                if isinstance(node.func.value, ast.Name) and node.func.value.id == "pickle":
                    if node.func.attr in ("load", "loads"):
                        issues.append(StaticAnalysisIssue(
                            file_path=file_path,
                            line=node.lineno,
                            column=node.col_offset + 1,
                            rule_id="PY-SEC-INSECURE-DESERIALIZATION",
                            severity=Severity.ERROR,
                            category=IssueCategory.SECURITY,
                            message="安全でない pickle によるデシリアライゼーションが検出されました（任意コード実行のリスク）。",
                            remediation="信頼できない入力に対して pickle を使わず、JSONやProtocol Buffersを使用してください。",
                            cwe_id="CWE-502"
                        ))

            # D. 例外の完全握りつぶし (except: pass)
            if isinstance(node, ast.ExceptHandler):
                is_empty_pass = False
                if len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
                    is_empty_pass = True
                elif len(node.body) == 1 and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Constant) and node.body[0].value.value is Ellipsis:
                    is_empty_pass = True

                if is_empty_pass:
                    # except: または except Exception: の判定
                    is_broad = node.type is None or (isinstance(node.type, ast.Name) and node.type.id in ("Exception", "BaseException"))
                    if is_broad:
                        issues.append(StaticAnalysisIssue(
                            file_path=file_path,
                            line=node.lineno,
                            column=node.col_offset + 1,
                            rule_id="PY-ROB-BARE-EXCEPT-PASS",
                            severity=Severity.ERROR,
                            category=IssueCategory.ROBUSTNESS,
                            message="広範な例外の完全な握りつぶし (except: pass) が検出されました。障害の検知が不可能になります。",
                            remediation="具体的な例外型を指定し、ログ出力または再送出を行ってください。"
                        ))

        # 4. 生SQL文字列連結の正規表現スキャン (CWE-89)
        sql_pattern = re.compile(r"""(?i)(?:SELECT\s+.+\s+FROM|INSERT\s+INTO|UPDATE\s+.+\s+SET|DELETE\s+FROM)\s+.*(?:\+|%|f["'])""")
        lines = content.splitlines()
        for idx, line in enumerate(lines, start=1):
            if sql_pattern.search(line):
                # プレースホルダーパラメータ化されていない文字列連結
                if any(kw in line for kw in ["execute", "query", "sql"]) and ("+" in line or "f\"" in line or "f'" in line or "%" in line):
                    issues.append(StaticAnalysisIssue(
                        file_path=file_path,
                        line=idx,
                        column=1,
                        rule_id="PY-SEC-SQL-INJECTION",
                        severity=Severity.ERROR,
                        category=IssueCategory.SECURITY,
                        message="文字列結合またはf-stringによる動的SQL構築が検出されました (SQLインジェクション脆弱性)。",
                        snippet=line.strip()[:80],
                        remediation="プレースホルダー (? または :param) を用いたパラメータ化クエリを使用してください。",
                        cwe_id="CWE-89"
                    ))

        return issues

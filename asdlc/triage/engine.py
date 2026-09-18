import re
from typing import Dict, Any, List, Optional
from ..models import IssueType, IssuePriority, IssueTriageResult

class IssueAutoTriageEngine:
    """
    Issue Autoトリアージエンジン (2026年9月最新仕様):
    1. プロンプトインジェクション多層サニタイズ (Clinejection対策)
    2. 4次元分析 (Type, Priority, Component, Actionable Next Steps)
    3. ガバナンス・最小権限・説明責任の担保
    """

    INJECTION_PATTERNS = [
        r"(?i)ignore\s+(all\s+)?(previous|prior|above)\s+instructions?",
        r"(?i)disregard\s+(all\s+)?instructions?",
        r"(?i)system\s+prompt",
        r"(?i)you\s+are\s+now\s+in\s+dan\s+mode",
        r"(?i)bypass\s+security",
        r"(?i)print\s+(the\s+)?api\s*key",
        r"(?i)reveal\s+secret",
        r"(?i)curl\s+https?://",
        r"(?i)rm\s+-rf"
    ]

    COMPONENT_MAP = {
        "auth": ["login", "jwt", "oauth", "password", "token", "session", "認証", "ログイン", "認可"],
        "ui": ["button", "layout", "css", "screen", "table", "view", "modal", "画面", "デザイン", "表示"],
        "api": ["endpoint", "rest", "graphql", "http", "status", "route", "api", "レスポンス"],
        "database": ["sql", "prisma", "migration", "query", "db", "table", "schema", "データベース", "テーブル"],
        "ci_cd": ["action", "pipeline", "docker", "deploy", "build", "ci", "cd", "デプロイ", "ビルド"]
    }

    def sanitize(self, text: str) -> (str, bool, List[str]):
        """間接プロンプトインジェクションの検知とサニタイズ"""
        warnings = []
        sanitized = text
        detected = False
        
        for pat in self.INJECTION_PATTERNS:
            matches = re.findall(pat, sanitized)
            if matches:
                detected = True
                warnings.append(f"潜在的なプロンプトインジェクション構文を検出・無害化: {matches[0]}")
                sanitized = re.sub(pat, "[FILTERED_SECURITY_RISK]", sanitized)

        return sanitized, detected, warnings

    def triage(self, title: str, body: str, issue_id: Optional[str] = None) -> IssueTriageResult:
        full_text = f"{title} {body}".lower()
        sanitized_body, injection_detected, warnings = self.sanitize(body)

        # 1. Type Classification
        if any(w in full_text for w in ["vulnerability", "cve", "exploit", "secret", "leak", "脆弱性", "漏洩"]):
            issue_type = IssueType.SECURITY
        elif any(w in full_text for w in ["bug", "error", "fail", "crash", "exception", "defect", "バグ", "不具合", "例外", "落ちる"]):
            issue_type = IssueType.BUG
        elif any(w in full_text for w in ["feature", "request", "support", "add", "new", "要望", "追加", "機能", "欲しい"]):
            issue_type = IssueType.FEATURE
        elif any(w in full_text for w in ["refactor", "cleanup", "rewrite", "performance", "リファクタ", "改善", "高速化"]):
            issue_type = IssueType.REFACTOR
        elif any(w in full_text for w in ["how to", "question", "?", "質問", "教えて", "使い方"]):
            issue_type = IssueType.QUESTION
        else:
            issue_type = IssueType.CHORE

        # 2. Priority & Severity (4D Priority)
        if issue_type == IssueType.SECURITY or any(w in full_text for w in ["critical", "blocker", "down", "fatal", "緊急", "重大", "停止"]):
            priority = IssuePriority.P0_CRITICAL
        elif issue_type == IssueType.BUG and any(w in full_text for w in ["high", "major", "break", "重度"]):
            priority = IssuePriority.P1_HIGH
        elif issue_type in [IssueType.BUG, IssueType.FEATURE]:
            priority = IssuePriority.P2_MEDIUM
        else:
            priority = IssuePriority.P3_LOW

        # 3. Component Estimation
        estimated_comp = "general / core"
        for comp, keywords in self.COMPONENT_MAP.items():
            if any(kw in full_text for kw in keywords):
                estimated_comp = comp
                break

        # 4. Labels
        suggested_labels = [f"type:{issue_type.value}", f"priority:{priority.value.split()[0].lower()}"]
        if estimated_comp != "general / core":
            suggested_labels.append(f"comp:{estimated_comp}")
        if injection_detected:
            suggested_labels.append("security:prompt-injection-flagged")

        # 5. Missing Information Check
        missing_info = []
        if issue_type == IssueType.BUG:
            if not any(w in full_text for w in ["reproduce", "step", "再現", "手順"]):
                missing_info.append("再現手順 (Steps to Reproduce) が明記されていません。")
            if not any(w in full_text for w in ["version", "os", "env", "node", "python", "環境", "バージョン"]):
                missing_info.append("動作環境・バージョン情報が不足しています。")
        elif issue_type == IssueType.FEATURE:
            if not any(w in full_text for w in ["why", "use case", "user story", "背景", "ユースケース", "理由"]):
                missing_info.append("機能要望の背景ユースケース・目的が不足しています。")

        # 6. Actionable Next Step & Remediation
        if injection_detected:
            remediation = "【警告】不審な指示が検出されたためサニタイズされました。人間メンテナーの目視確認が必要です。"
            role = "Security Officer / Senior Maintainer"
        elif missing_info:
            remediation = "不足情報の提供依頼テンプレートをコメント投稿し、ユーザーからの回答を待機します。"
            role = "Triage Lead / Reporter"
        elif issue_type == IssueType.SECURITY:
            remediation = "非公開セキュリティアドバイザリへ移行し、Threat Defense Meister の緊急レビューを招集します。"
            role = "Security Lead"
        elif issue_type == IssueType.BUG and priority == IssuePriority.P0_CRITICAL:
            remediation = "即時ホットフィックスブランチを作成し、再現テストコード先行生成 (TDD) を開始します。"
            role = "Core Engine Engineer"
        else:
            remediation = "該当コンポーネントの仕様書 (spec.md) を参照し、反復開発バックログへ登録します。"
            role = "Feature Developer"

        matched_docs = []
        if estimated_comp == "auth":
            matched_docs.append("docs/ADR-0004-jwt-auth.md")
        elif estimated_comp == "ui":
            matched_docs.append("docs/DESIGN-ui-components.md")

        return IssueTriageResult(
            issue_id=issue_id,
            title=title,
            sanitized_body=sanitized_body,
            prompt_injection_detected=injection_detected,
            injection_warnings=warnings,
            issue_type=issue_type,
            priority=priority,
            estimated_component=estimated_comp,
            suggested_labels=suggested_labels,
            missing_information=missing_info,
            remediation_proposal=remediation,
            recommended_assignee_role=role,
            matched_adrs_or_specs=matched_docs
        )

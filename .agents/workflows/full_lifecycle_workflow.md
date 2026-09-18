---
title: "ASDLC Full Lifecycle Workflow (End-to-End SOP)"
doc_type: "workflow"
tags: ["sdlc", "waterfall-boost", "full-lifecycle", "asdlc"]
---

# ASDLC Full Lifecycle Workflow (全体開発ライフサイクル標準手順)

本ワークフローは、Issueの着信から自動トリアージ、ウォーターフォール各工程（Phase 1〜7）、マイスターズ審議会による品質ゲート、および Coding Agent によるコード合成に至る、**ASDLC エンドツーエンドの全体運用手順**を定めたものです。

---

## 🗺️ 全体オーケストレーションマップ

```mermaid
flowchart TD
    Issue["新着 Issue / 不具合・機能要求"] --> Triage["4D Autoトリアージ (asdlc triage)<br>・Clinejectionプロンプトインジェクション無害化<br>・Type / Priority / Component / Actionable Next Steps 判定"]
    Triage --> P1["Phase 1: 要件定義<br>(requirements.md)"]

    subgraph Waterfall["ウォーターフォール昇格ループ (asdlc status / advance)"]
        P1 --> Q1{"マイスターズ審議会 審査 1<br>(asdlc review)"}
        Q1 -->|PASS| P2["Phase 2: 基本設計<br>(basic_design.md, ADR)"]
        P2 --> Q2{"マイスターズ審議会 審査 2<br>(asdlc review)"}
        Q2 -->|PASS| P3["Phase 3: 詳細設計<br>(detailed_design.md)"]
        P3 --> Q3{"マイスターズ審議会 審査 3<br>(asdlc review)"}
        Q3 -->|PASS| P4["Phase 4: 実装・単体テスト<br>(Coding Agent: 3層コンテキスト & TDD)"]
        P4 --> Q4{"マイスターズ審議会 審査 4<br>(asdlc review & pytest)"}
        Q4 -->|PASS| P5["Phase 5: 結合・総合テスト<br>(Integration & E2E Tests)"]
        P5 --> Q5{"マイスターズ審議会 審査 5<br>(asdlc review)"}
        Q5 -->|PASS| P6["Phase 6: 本番リリース<br>(Deployment Plan & Release)"]
        P6 --> Q6{"マイスターズ審議会 審査 6<br>(asdlc review)"}
        Q6 -->|PASS| P7["Phase 7: 保守運用<br>(Monitoring, Runbook, SLA)"]
    end

    Q1 & Q2 & Q3 & Q4 & Q5 & Q6 -- FAIL --> Remediation["Remediation Loop: 指摘事項修正・再審査"]
    Remediation --> Waterfall
```

---

## 🌟 開発者の日常コマンドフロー

```bash
# 1. 新着Issueの自動分析とセキュリティ検査
asdlc triage "ユーザー一覧表示時にJWT期限切れで500エラーになる"

# 2. 現在のプロジェクト進行度とゲート状態を確認
asdlc status

# 3. 作成した仕様書をマイスターズ審議会に提出して審査
asdlc review docs/spec/detailed_design.md

# 4. 審査合格後、次フェーズへ安全に昇格
asdlc advance

# 5. Coding Agent による 3層コンテキスト優先コード合成
asdlc code "JWT期限切れ時に401 Unauthorizedとリフレッシュ案内を返却するハンドラー"
```

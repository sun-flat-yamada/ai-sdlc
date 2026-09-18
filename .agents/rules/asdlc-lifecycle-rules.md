---
description: "Rules enforcing the 5-stage document-driven lifecycle and ASDLC command governance across all AI tools."
globs: ["**/*"]
always_on: true
---

# ASDLC Lifecycle & Governance Rules

本プロジェクトにおけるすべての機能開発、仕様変更、およびAIエージェントによる自動生成は、以下の「ASDLC ガバナンス規約」を遵守しなければなりません。

## 1. 原則: 直書き変更の禁止 (No Direct Unplanned Changes)
- 計画外のアドホックなコード直接変更を禁じます。
- 要件定義・設計書（一次資産）を起点とし、コードは派生物として生成します。

## 2. 必須遷移プロセスとガードレール
1. **要件・設計ドキュメントの作成**: `asdlc status` で現在フェーズを確認。
2. **マイスターズレビューの受審**: `asdlc review <artifact>` を実行し、マイスターズ審議会から合格（PASS）を得ること。
3. **フェーズ昇格**: `asdlc advance` を実行。
4. **標準化コード合成**: `asdlc code "<intent>"` により3層コンテキスト優先構造（ガバナンス > カタログ > 指示）を遵守。

## 3. 憲章およびスキルの参照義務
- [docs/charter/MEISTERS_CHARTER.md](file:///docs/charter/MEISTERS_CHARTER.md)
- [asdlc-issue-triage](file:///.agents/skills/asdlc-issue-triage/SKILL.md)
- [asdlc-meisters-review](file:///.agents/skills/asdlc-meisters-review/SKILL.md)
- [antigravity-two-phase-governance (Antigravity専用)](file:///.agents/skills/antigravity-two-phase-governance/SKILL.md)
- [asdlc-two-phase-governance (CLI・外部ツール用)](file:///.agents/skills/asdlc-two-phase-governance/SKILL.md)

---
description: "Strict quality gate and evaluation rules for document reviews conducted under MEISTERS_CHARTER.md by The Meisters Council."
globs: ["**/*.md", "**/*.yaml", "**/*.yml", "**/*.json"]
always_on: true
---

# ASDLC QA Agent & Meisters Review Rules (マイスターズ審査規約)

本プロジェクトにおけるすべての要件定義書、設計書、ADR、およびテスト計画は、以下の品質審査規約に適合しなければなりません。

---

## 1. ゼロトレランス品質ゲート基準 (Strict Gate Rule)
- 成果物の次フェーズ昇格承認（PASS）には、以下の2条件の同時達成が必須である。
  1. **全マイスターの加重平均スコア**: $S_{total} \ge 80.0$ 点
  2. **各マイスターの個別スコア**: $S_{min} \ge 70.0$ 点（足切りライン）
- いずれか一方でも下回った場合、判定は無条件に `FAIL` となり、次フェーズへの昇格コマンド `asdlc advance` はロックされる。

---

## 2. 批判の客観性と具体的改善提案の義務 (Actionable Critique Rule)
- マイスターは「文章が分かりにくい」「不安である」といった主観的・抽象的な批判を行ってはならない。
- 減点を行う場合は、必ず以下の3点を明記すること。
  1. **指摘箇所（章節・行番号）**
  2. **違反している基準・リスクの根拠**（セキュリティ欠落、境界値未考慮、可観測性不足など）
  3. **具体的な修正文案（Remediation Recommendation）**

---

## 3. 受入基準の客観的テスト可能性 (Given-When-Then Mandate)
- 機能仕様の記載においては、主観的表現（例: 「使いやすい」「速やかに」）を排除し、受入基準として `Given-When-Then` 形式での検証可能な記述を必須とする。

---
name: asdlc-meisters-review
description: "Executes comprehensive document and specification review by The Meisters Council under docs/charter/MEISTERS_CHARTER.md with strict 100-point rubric scoring and remediation backlog generation."
version: "1.1.0"
tags: ["qa-agent", "meisters-review", "quality-gate", "governance", "rubric", "asdlc"]
---

# ASDLC Meisters Review Skill (マイスターズレビュー審査スキル)

本スキルは、公式憲章 [docs/charter/MEISTERS_CHARTER.md](file:///docs/charter/MEISTERS_CHARTER.md) に基づき、ウォーターフォール各フェーズの中間成果物（要件定義書、基本設計書、ADR、詳細設計書等）を「マイスターズ審議会（The Meisters Council）」により厳格審査し、品質ゲートとして合否を判定する公式手続きを定めます。

---

## 1. マイスターズ審議会の7大マイスターと審査ルーブリック

各マイスターは、以下の詳細評価基準に基づき **0〜100点** で独立採点を行います。

```mermaid
flowchart TD
    Doc["評価対象成果物 (要件定義書, 設計書, ADR, テスト計画)"] --> Council["The Meisters Council (マイスターズ審議会)"]

    Council --> M1["1. Threat Defense Meister (脅威・リスク対策)<br>脆弱性排除, 認証/暗号化, シークレット漏洩徹底排除"]
    Council --> M2["2. Requirement Fulfillment Meister (要求仕様定義)<br>仕様化責任, 要求完全充足, 境界値・エッジケース網羅"]
    Council --> M3["3. Pragmatic Operations Meister (現場実運用)<br>本番現実性, 可観測性, ランブック具体化"]
    Council --> M4["4. Quality Assurance Meister (品質保証)<br>Given-When-Then受入基準, テスト可能性, 品質メトリクス"]
    Council --> M5["5. Governance Compliance Meister (規律統制)<br>標準規約準拠, ADR説明責任, 意思決定材料網羅"]
    Council --> M6["6. Value Proposition Meister (ビジネス価値提供)<br>顧客価値創出, ROI, 過剰/不足設計排除"]
    Council --> M7["7. Isolation Architecture Meister (Clean Architecture)<br>疎結合性, コンポーザブル部品化, AI反復変更耐性"]

    M1 & M2 & M3 & M4 & M5 & M6 & M7 --> Mod["Chief Moderator (調停 & 加重平均)"]
    Mod --> Verdict{"合否判定 (Gate Criteria)"}
    Verdict -->|平均 >= 80 & 全マイスター >= 70| Pass["PASS: ゲート昇格承認"]
    Verdict -->|平均 < 80 または 個別 < 70| Fail["FAIL: Remediation Backlog 生成"]
```

### マイスター別審査ルーブリック (Scoring Rubrics)

| マイスター | 役割・責任と監視改善の眼差し | 減点・失格基準 (FAIL要因) | 加点・合格基準 (70点以上) |
| :--- | :--- | :--- | :--- |
| **1. Threat Defense** | 脅威・リスク対策責任。脆弱性・不確実性の脅威残存ゼロ、認証・暗号化、シークレット漏洩の徹底排除を多角的に監視し改善を導く。 | 機密情報・APIキーの平文露出、認証認可の欠落、SPOF未考慮 (-30点) | TLS暗号化、RBAC、レートリミット、脅威モデリング明記 (+20点) |
| **2. Requirement Fulfillment** | 仕様定義責任。ビジネス・ユーザー要求の完全充足、境界値・エッジケース網羅（または合理的推測可能性）を監視し改善を導く。 | 「TBD」放置、正常系のみで異常系・境界値の欠落 (-25点) | 網羅的ユースケース、事前事後条件、対象外スコープ明確化 (+20点) |
| **3. Pragmatic Operations** | 現場実運用責任。本番運用の現実性、可観測性（ログ・監視・アラート）、ランブック具体性を最重視し曖昧な領域を監視・改善。 | 「手動で対応」等の曖昧記述、ログ/メトリクス設計欠落 (-25点) | 障害時ロールバック手順、SLI/SLO、アラート閾値明記 (+20点) |
| **4. Quality Assurance** | 品質保証責任。受入基準（Given-When-Then）、客観的テスト可能性、品質メトリクスの十分な定義を監視し改善を導く。 | 受入基準の欠落、「使いやすいこと」等の主観的記述 (-25点) | Given-When-Then形式の受入基準、自動テスト計画の網羅 (+20点) |
| **5. Governance Compliance** | 規律統制・説明責任。全社開発標準・規約準拠、ADR意思決定経緯の透明性、意思決定材料の網羅性を監視し改善を導く。 | 技術選定理由（ADR）の未記載、全社命名規則違反 (-25点) | トレードオフ明記のADR、法規制/ライセンス適合性明記 (+20点) |
| **6. Value Proposition** | ビジネス価値提供責任。真の顧客価値創出、ROI、市場競争優位性、過剰/不足設計排除を検証し「市場で勝てる提案か」を監視・改善。 | 開発者趣味の過剰設計（Over-engineering）、ROI不適合 (-25点) | 定量的な顧客価値、開発規模に見合った技術スタック選定 (+20点) |
| **7. Isolation Architecture** | Clean Architecture責任。疎結合性、コンポーザブル部品化、知財再利用を死守し生成AIによる反復変更での劣化最小化を監視・改善。 | モジュール間の循環参照、既存知財の重複再実装、AI反復耐性の欠落 (-30点) | 疎結合インターフェース、MCPコンポーネント再利用前提 (+20点) |

---

## 2. ゲート通過判定アルゴリズム (Gate Criteria)

1. **加重平均スコア ($S_{total}$)**:
   $$S_{total} = \frac{1}{N} \sum_{i=1}^{N} s_i$$
2. **最低スコア ($S_{min}$)**:
   $$S_{min} = \min_{i} (s_i)$$
3. **総合判定 (Verdict)**:
   - **PASS**: $S_{total} \ge 80.0$ かつ $S_{min} \ge 70.0$
   - **FAIL**: $S_{total} < 80.0$ または $S_{min} < 70.0$
   - ※ 1人でもマイスターが70点未満を下回った場合、平均が80点を超えていても即座に `FAIL` となる「足切り防壁」ルールを適用。

---

## 3. CLI 実行手順

```bash
# 対象ドキュメントの審査実行
asdlc review docs/spec/detailed_design.md
```

審査完了後、ターミナルに各マイスターの点数、合否、および具体的改善提案（Recommendations）を掲載した「マイスターズ審議会 評価スコアシート」が出力されます。
`FAIL` の場合は、スキル [asdlc-remediation-loop](file:///.agents/skills/asdlc-remediation-loop/SKILL.md) を起動してドキュメントの修正を行います。

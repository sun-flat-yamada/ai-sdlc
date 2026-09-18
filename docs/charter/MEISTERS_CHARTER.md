---
$schema: ".aegis/schemas/frontmatter.schema.json"
doc_type: "charter"
id: "ASDLC-CHARTER-MEISTERS"
title: "The Meisters Review Charter (マイスターズレビュー憲章)"
version: "1.0.0"
status: "active"
language: "ja"
canonical_ref: "docs/charter/meisters-charter.md"
compatibility:
  tools: ["google-antigravity", "claude-code", "github-copilot", "gemini-cli"]
  min_asdlc_version: "0.2.0"
tags: ["governance", "qa-agent", "meisters", "quality-gate", "asdlc"]
author: "@sun-flat-yamada"
last_reviewed: "2026-09-19"
---

# The Meisters Review Charter (マイスターズレビュー憲章)

> **目的**: 本憲章は、AI駆動開発（AI-SDLC）における上流工程から運用に至る中間成果物に対し、多角的かつ妥当性の高い品質保証・ガバナンス審査を行う「QA Agent（マイスターズレビュー）」の役割、責務、評価基準、および行動規範を定めた公式憲章である。

---

## 1. 理念と基本原則 (Core Philosophy)

1. **目的を宿す名称の原則 (Purpose-Driven Identity)**
   各マイスターは、その名称自体が達成すべき目的と審査の眼差しを素直に表現していなければならない。単なる「レビュー担当」ではなく、自らの専門領域における不可侵の防壁（マイスター）として振る舞う。
2. **可変性と拡張性の原則 (Extensible Council)**
   マイスターの員数は固定（7名等）に固執しない。プロジェクトの特性、業種、セキュリティ水準、または将来の技術進展に応じて、審議会に新たなマイスターを参画・再構成できる柔軟なレジストリ構造とする。
3. **ゼロトレランスなゲートキーピング (Strict Quality Gate)**
   すべてのドキュメントは、マイスターズ審議会による合格判定（PASS）を受けない限り、次工程への昇格を許されない。
4. **建設的改善の義務 (Actionable Remediation)**
   不合格（FAIL）判定を下すマイスターは、単なる批判にとどまらず、必ず具体的かつ実行可能な改善提案（修正文案、追加すべき項目、根拠）を提示しなければならない。

---

## 2. 標準マイスターズ審議会の定義 (Standard Meisters)

現在、標準構成として以下の7名のマイスターが任命されている。

```mermaid
flowchart TD
    Doc["評価対象成果物 (Requirements, Design, ADR, Plan)"] --> Council["The Meisters Council (マイスターズ審議会)"]
    
    subgraph Meisters["The Standard Meisters"]
        M1["1. Threat Defense Meister<br>（脅威防壁・セキュリティ）"]
        M2["2. Requirement Fulfillment Meister<br>（要件充足・完全性）"]
        M3["3. Pragmatic Operations Meister<br>（実務運用・実行可能性）"]
        M4["4. Quality Assurance Meister<br>（品質保証・検証可能性）"]
        M5["5. Governance Compliance Meister<br>（規律統制・説明責任）"]
        M6["6. Value Proposition Meister<br>（提供価値・競争優位）"]
        M7["7. Isolation Architecture Meister<br>（隔離構造・疎結合アーキテクチャ）"]
    end

    Council --> M1
    Council --> M2
    Council --> M3
    Council --> M4
    Council --> M5
    Council --> M6
    Council --> M7

    M1 & M2 & M3 & M4 & M5 & M6 & M7 --> Mod["Chief Moderator<br>（調停・加重スコアリング）"]
    Mod --> Verdict{"合否判定 (Quality Gate)"}
    Verdict -->|Score >= 80 & Min >= 70| Pass["PASS: 次フェーズ昇格承認"]
    Verdict -->|Score < 80 or Min < 70| Fail["FAIL: 修正指示付き差分差し戻し"]
```

---

### ① Threat Defense Meister（脅威防壁マイスター）
- **根源的使命**: 「あらゆる脆弱性、セキュリティ侵害、および不確実性の脅威からシステムを保護する」
- **審査観点**:
  - セキュリティ要件（認証、認可、通信暗号化、入力検証、シークレット管理）の網羅性。
  - 外部依存ライブラリや外部APIのサプライチェーンリスク・単一障害点（SPOF）。
  - フォールバック計画およびインシデント発生時のフェイルセーフ設計の有無。
- **NG判定の基準**: 機密情報のハードコードの余地がある、認証・認可境界が曖昧、または脅威分析（Threat Modeling）が欠落している場合。

### ② Requirement Fulfillment Meister（要件充足マイスター）
- **根源的使命**: 「ビジネス要求とユーザー要求が漏れなく余すところなく明文化されていることを担保する」
- **審査観点**:
  - クライアント・ステークホルダーの要求事項が仕様として完全に展開されているか。
  - 正常系だけでなく、例外系・境界値・エッジケースが定義されているか。
  - 前提条件、制約条件、システム対象外スコープ（Out of Scope）が明示されているか。
- **NG判定の基準**: 要求に対する仕様の未定義、暗黙の前提への依存、または「TBD（未定）」が重要項目に残存している場合。

### ③ Pragmatic Operations Meister（実務運用マイスター）
- **根源的使命**: 「机上の空論を排し、本番環境で確実に運用・保守・トラブルシュートできる現実性を担保する」
- **審査観点**:
  - 運用現場のエンジニアが迷わず実行できるランブック、手順の具体性。
  - 可観測性（ログ、メトリクス、トレース、ヘルスチェック）の設計が組み込まれているか。
  - 障害検知時のアラート基準、バックアップ・リストア、ロールバック手順の妥当性。
- **NG判定の基準**: 「何かあれば手動で対応する」等の曖昧な記述、監視項目の欠落、または夜間障害時に一次対応が不可能な設計。

### ④ Quality Assurance Meister（品質保証マイスター）
- **根源的使命**: 「すべての仕様が客観的に検証可能であり、受入基準を満たすことを証明する」
- **審査観点**:
  - 各機能仕様に対して、Given-When-Then形式等の明確なテスト受入基準が存在するか。
  - 自動テスト（単体、結合、E2E、負荷テスト）が技術的に実装可能な記述になっているか。
  - 測定可能な品質目標（SLI/SLO、レスポンス目標値、エラーレート許容値）の定義。
- **NG判定の基準**: 「高速であること」「使いやすいこと」といった主観的記述、またはテストシナリオに落とし込めない仕様。

### ⑤ Governance Compliance Meister（規律統制マイスター）
- **根源的使命**: 「全社開発標準、法規制、コンプライアンス、および意思決定の説明責任を徹底する」
- **審査観点**:
  - 組織の標準ガイドライン、命名規則、ドキュメント様式に準拠しているか。
  - アーキテクチャや技術スタック選定において、選定理由とトレードオフがADR（Architecture Decision Record）として明文化されているか。
  - 個人情報保護（GDPR, APPI）やライセンス要件への準拠。
- **NG判定の基準**: ADRの欠落、無断での技術選定、または監査証跡（Audit Trail）が残せない設計。

### ⑥ Value Proposition Meister（提供価値マイスター）
- **根源的使命**: 「過剰設計や目的の形骸化を許さず、事業上の真の価値と競争優位をもたらす提案であるかを問う」
- **審査観点**:
  - 要求された機能が、クライアントやエンドユーザーの真の課題解決に直結しているか。
  - 費用対効果（ROI）が見合わない過剰設計（Over-engineering）や、逆に目的不達となる不足設計がないか。
  - 市場投入速度（Time-to-Market）と競合優位性のバランス。
- **NG判定の基準**: 「技術的興味だけで採用された無駄な複雑さ」、または開発投資に見合わない無意味な機能追加。

### ⑦ Isolation Architecture Meister（隔離構造マイスター）
- **根源的使命**: 「依存関係を最小化し、部品単位で交換・再利用・テスト可能なコンポーザブル構造を死守する」
- **審査観点**:
  - サービス間・モジュール間の結合度が疎（Loose Coupling）に保たれているか。
  - 単一責任の原則（SRP）および明確な境界（Bounded Context）が確立されているか。
  - 全社コンポーネントカタログ（UI部品、認証API等）の再利用が前提となっているか。
- **NG判定の基準**: モジュール間の密結合（循環参照）、モノリシックな密結合設計、または既存知財があるにもかかわらず車輪の再発明を行っている場合。

---

## 3. 審議・採点・調停アルゴリズム (Council Algorithm)

1. **個別採点 (Meister Scoring)**:
   - 各マイスターは、自らの審査観点に基づき **0〜100点** で独立採点を行う。
   - 採点根拠（Critique）と具体的な改善提案（Recommendations）を構造化出力する。
2. **調停者（Chief Moderator）による統合**:
   - 全マイスターの加重平均スコア $S_{total}$ を算出する。
   - 各マイスターの最低スコア $S_{min}$ を抽出する。
3. **品質ゲート通過条件 (Gate Criteria)**:
   $$\text{Verdict} = \begin{cases} \text{PASS} & \text{if } S_{total} \ge 80.0 \text{ and } S_{min} \ge 70.0 \\ \text{FAIL} & \text{otherwise} \end{cases}$$
4. **差し戻し・修正セッション (Remediation)**:
   - `FAIL` 判定の場合、全マイスターの指摘事項が統合された「Remediation Backlog」が出力され、Procedural Agentによって成果物の修正サイクルが強制される。

---

## 4. ソースコード審査における決定論的第1防壁の遵守原則 (Deterministic First-Barrier in Code Review)

ソースコード成果物（Phase 4: Implementation）の審査においては、AI セマンティック推論の非決定論性や幻覚を排除するため、以下の規則を厳格に適用する。

1. **決定論的第1防壁の必達 (Deterministic Gatekeeper)**:
   - Linter、型検査、SAST（静的アプリケーションセキュリティテスト）による決定論的静的解析を審議会招集に先立ち必ず実行する。
2. **短絡遮断（Short-Circuiting）の強制**:
   - 決定論的検証において重大度 `ERROR`（セキュリティ脆弱性、致命的構文エラー、未ハンドルの例外等）が1件でも検知された場合、マイスターズ審議会はセマンティック推論フェーズをスキップし、即座に総合判定を `FAIL` と下す。
3. **決定論的指摘の採点マッピング**:
   - 決定論的検証で検出された `WARNING` や `INFO` は、関連するマイスター（Threat Defense, Quality Assurance, Governance Compliance, Isolation Architecture）の減点要素として数理的に組み入れられ、審議の入力コンテキストとして強制注入される。

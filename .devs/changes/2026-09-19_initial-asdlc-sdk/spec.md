---
$schema: ".aegis/schemas/frontmatter.schema.json"
doc_type: "architecture_doc"
id: "ASDLC-CHANGE-001-SPEC"
title: "ASDLC SDK 要求分析 & 詳細機能仕様書"
version: "1.0.0"
status: "active"
language: "ja"
canonical_ref: ".devs/changes/2026-09-19_initial-asdlc-sdk/spec.md"
compatibility:
  tools: ["google-antigravity", "claude-code", "github-copilot", "gemini-cli"]
  min_asdlc_version: "0.2.0"
tags: ["spec", "requirements", "api", "data-model", "asdlc"]
author: "@sun-flat-yamada"
last_reviewed: "2026-09-19"
---

# ASDLC SDK 要求分析 & 詳細機能仕様書

## 1. ドメインモデル & データ構造

### 1.1 SDLC Phase 列挙型
```python
class Phase(str, Enum):
    PHASE_1_REQUIREMENTS = "phase_1_requirements"         # 要件定義
    PHASE_2_BASIC_DESIGN = "phase_2_basic_design"         # 基本設計 (ADR)
    PHASE_3_DETAIL_DESIGN = "phase_3_detail_design"       # 詳細設計 (API, Schema)
    PHASE_4_ITERATION = "phase_4_iteration"               # 反復開発・実装 (TDD)
    PHASE_5_INTEGRATION_TEST = "phase_5_integration_test" # 結合テスト (E2E)
    PHASE_6_PRODUCTION_RELEASE = "phase_6_production_release" # 本番リリース
    PHASE_7_MAINTENANCE = "phase_7_maintenance"           # 保守運用
```

### 1.2 マイスターズレビュー評価モデル (Meister Evaluation Model)
```python
class MeisterScore(BaseModel):
    meister: MeisterType
    score: int = Field(ge=0, le=100)
    verdict: ReviewVerdict # PASS / FAIL
    critique: str
    recommendations: List[str]

class MeisterEvaluation(BaseModel):
    document_name: str
    phase: Phase
    total_score: float = Field(ge=0, le=100)
    min_score: int
    verdict: ReviewVerdict
    meister_scores: List[MeisterScore]
    summary: str
    remediation_required: bool
    charter_ref: str = "docs/charter/MEISTERS_CHARTER.md"
```

### 1.3 Issue 4Dトリアージモデル (Issue 4D Triage Model)
```python
class IssueTriageResult(BaseModel):
    issue_id: Optional[str]
    title: str
    sanitized_body: str
    prompt_injection_detected: bool
    injection_warnings: List[str]
    issue_type: IssueType # bug, feature, refactor, security, question, chore
    priority: IssuePriority # P0_CRITICAL, P1_HIGH, P2_MEDIUM, P3_LOW
    estimated_component: str
    suggested_labels: List[str]
    missing_information: List[str]
    remediation_proposal: str
    recommended_assignee_role: str
    matched_adrs_or_specs: List[str]
```

---

## 2. インターフェース仕様 (CLI Commands)

| コマンド | 引数 | 動作概要 |
| :--- | :--- | :--- |
| `asdlc status` | なし | 現在のフェーズ、主要タスク、必須成果物、およびガードレール状態を表示。 |
| `asdlc triage` | `<target>` (タイトルまたはファイルパス) | Issueの自動4次元分類、優先度判定、およびプロンプトインジェクションサニタイズを実行。 |
| `asdlc review` | `<artifact>` (ドキュメント名) | マイスターズレビュー憲章に基づきマイスターズ審議会が成果物を多角採点し、合否判定スコアシートを出力。 |
| `asdlc advance` | なし | ガードレール（成果物存在・レビューPASS）を検証し、次フェーズへ昇格。 |
| `asdlc code` | `<intent>` (開発指示文) | 3層コンテキスト（ガバナンス > カタログ > 指示）を合成し、標準化コード仕様を出力。 |
| `asdlc init` | なし | リポジトリにASDLC構成と各AIツール用設定ファイルを展開。 |

---

## 3. セキュリティ & サニタイズ要件
- **間接プロンプトインジェクション検知**: `ignore previous instructions`, `system prompt`, `dan mode`, `curl http` 等の構文を正規表現およびセマンティックフィルタで検知し、置換無害化する。
- **ASCII安全コンソール出力**: Windows環境（CP932/Shift_JIS）でのUnicodeEncodeErrorを防止するため、絵文字に依存せず洗練されたASCIIタグ（`[!]`, `[OK]`, `[SUCCESS]`, `[INFO]`）を用いる。

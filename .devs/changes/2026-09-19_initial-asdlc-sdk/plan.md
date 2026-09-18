---
$schema: ".aegis/schemas/frontmatter.schema.json"
doc_type: "architecture_doc"
id: "ASDLC-CHANGE-001-PLAN"
title: "ASDLC SDK 開発計画書 & WBS"
version: "1.0.0"
status: "active"
language: "ja"
canonical_ref: ".devs/changes/2026-09-19_initial-asdlc-sdk/plan.md"
compatibility:
  tools: ["google-antigravity", "claude-code", "github-copilot", "gemini-cli"]
  min_asdlc_version: "0.2.0"
tags: ["plan", "wbs", "testing-strategy", "milestones", "asdlc"]
author: "@sun-flat-yamada"
last_reviewed: "2026-09-19"
---

# ASDLC SDK 開発計画書 & WBS

## 1. 開発マイルストーン

```mermaid
timeline
    title ASDLC SDK 開発ロードマップ
    Phase 1 : 基礎設計と憲章制定 : docs/charter/MEISTERS_CHARTER.md策定 : 3大エージェント仕様策定
    Phase 2 : コアエンジン実装 : asdlcパッケージ構築 : 4Dトリアージエンジン実装 : マイスターズレビューエンジン実装
    Phase 3 : ガバナンス統合 : agent-aegis-harness資産移植 : skills / rules / multi-AI設定
    Phase 4 : 検証と公開準備 : 自動テストスイート実行 : README / LICENSE / Makefile整備
```

---

## 2. タスク詳細 WBS

- [x] **M1: コアアーキテクチャ刷新**
  - [x] パッケージ名およびコマンド名を `asdlc` に改定
  - [x] `asdlc/models.py` にマイスターモデル・トリアージモデルを定義
  - [x] `asdlc/orchestrator.py` のライフサイクル制御実装
- [x] **M2: 4D Issue Autoトリアージの実装**
  - [x] Clinejection防御サニタイズ層の実装
  - [x] 4次元分析（Type, Priority, Component, Next Steps）
- [x] **M3: マイスターズレビュー（QA Agent: マイスターズ審議会）の実装**
  - [x] `docs/charter/MEISTERS_CHARTER.md` 憲章の策定
  - [x] 7マイスターのプロファイルと合否判定アルゴリズムの実装
- [x] **M4: ガバナンス・マルチAIツール資産の移植**
  - [x] `agent-aegis-harness` からskills/rulesを移植
  - [x] `CLAUDE.md`, `.github/copilot-instructions.md`, `.gemini/GEMINI.md` の配備
- [x] **M5: 品質検証とドキュメント整備**
  - [x] `tests/test_asdlc.py` による自動テスト（5件全パス）
  - [x] `pip install -e .` の実機動作確認
  - [x] GitHub公開用ドキュメント（README, LICENSE, CONTRIBUTING, Makefile）の整備

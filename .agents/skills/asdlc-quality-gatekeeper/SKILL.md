---
name: asdlc-quality-gatekeeper
description: "Verifies mandatory artifacts, Proof of Review human approvals, and Meisters Review PASS certificates before authorizing phase progression via asdlc advance."
version: "1.0.0"
tags: ["procedural-agent", "quality-gate", "governance", "guardrails", "asdlc"]
---

# ASDLC Quality Gatekeeper Skill

本スキルは、ウォーターフォール開発の各工程（Phase 1〜7）において、**未成熟な成果物や形骸化したレビューによる後工程への不具合流出を物理的に遮断**するゲートキーピング手続きを定めます。

---

## 1. ガードレール検査マトリクス (Phase-by-Phase Verification)

各フェーズで昇格（`asdlc advance`）を認可する前に、以下の3つの検証レイヤーを機械的に走査します。

```mermaid
flowchart TD
    Req["昇格要求 (asdlc advance)"] --> C1{"Check 1: 必須成果物の存在"}
    C1 -->|欠落あり| Block1["昇格拒絶: 未作成ファイルを提示"]
    C1 -->|全ファイル存在| C2{"Check 2: マイスターズレビュー合否"}
    C2 -->|FAIL または未受審| Block2["昇格拒絶: FAIL要因を提示"]
    C2 -->|PASS (80点以上 & 個別70点以上)| C3{"Check 3: Proof of Review (人間の証跡)"}
    C3 -->|未承認 / 質問未回答| Block3["昇格拒絶: 人間のレビュー回答を要求"]
    C3 -->|承認証跡あり| Advance["昇格認可: 次フェーズへ状態遷移"]
```

| フェーズ | 必須成果物 (Check 1) | マイスター審査要件 (Check 2) | 人間レビュー証跡 (Check 3) |
| :--- | :--- | :--- | :--- |
| **Phase 1: 要件定義** | `requirements.md` | $S_{total} \ge 80, S_{min} \ge 70$ | 要件スコープ確認・クライアント合意 |
| **Phase 2: 基本設計** | `basic_design.md`, `ADR-*.md` | $S_{total} \ge 80, S_{min} \ge 70$ | アーキテクチャ選定・ADR承認 |
| **Phase 3: 詳細設計** | `detailed_design.md` | $S_{total} \ge 80, S_{min} \ge 70$ | API仕様・受入基準（Given-When-Then）確認 |
| **Phase 4: 実装・単体テスト** | `src/`, `tests/test_*.py` | $S_{total} \ge 80, S_{min} \ge 70$ | カバレッジ確認・コード差分レビュー |
| **Phase 5: 結合・総合テスト** | `tests/integration/`, `test_report.md` | $S_{total} \ge 80, S_{min} \ge 70$ | 総合不具合ゼロ承認・パフォーマンステスト合格 |
| **Phase 6: 本番リリース** | `deploy_plan.md`, `release_notes.md` | $S_{total} \ge 80, S_{min} \ge 70$ | リリース判定会議承認・本番反映承認 |
| **Phase 7: 保守運用** | `runbook.md`, `alerts_config.yaml` | $S_{total} \ge 80, S_{min} \ge 70$ | 運用引継ぎ完了・SLA監視開始確認 |

---

## 2. コマンドラインでの動作

```bash
# 現在のゲート状態を確認
asdlc status

# 条件を満たして次フェーズへ昇格
asdlc advance
```

未達条件が存在する場合、ターミナル上にブロック理由が明示され、終了コード `1` で昇格が阻止されます。

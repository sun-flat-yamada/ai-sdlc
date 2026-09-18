---
name: antigravity-two-phase-governance
description: "Implements Google Antigravity two-phase governance: pre-execution planning consensus (implementation_plan.md + human review) and post-execution evidence sealing (walkthrough.md)."
---

# Google Antigravity Two-Phase Governance Skill

本スキルは、**Google Antigravity 環境専用** において AI エージェントの自律変更を安全に統制するための **「二段階ガバナンス (Two-Phase Evidence & Review)」** 手続きを規定します。

> [!IMPORTANT]
> **適用範囲**: 本スキルは Google Antigravity 固有のアーティファクトシステムおよび UI 機構に特化しています。Claude Code、Cursor、Gemini CLI 等の他コーディングツール環境では、本スキルではなく [asdlc-two-phase-governance](../asdlc-two-phase-governance/SKILL.md) を使用してください。

```mermaid
sequenceDiagram
    autonumber
    actor User as 人間 (USER)
    participant Agent as Antigravity Agent
    participant Planning as Planning Mode (implementation_plan.md)
    participant Codebase as ワークスペース (Codebase)
    participant Walkthrough as 事後検証 (walkthrough.md)

    rect rgb(240, 248, 255)
    Note over Agent, Planning: Phase 1: 事前計画と合意形成 (Pre-Execution Consensus)
    Agent->>Planning: implementation_plan.md を作成 (厳格英語見出し & ArtifactMetadata)
    Agent->>User: レビュー待機 (UIの [Proceed] ボタン有効化)
    User-->>Agent: レビュー承認 ([Proceed] ボタン押下)
    end

    rect rgb(255, 250, 240)
    Note over Agent, Codebase: Phase 2: 自律実装と実証 (Execution & Verification)
    Agent->>Codebase: ソースコード実装・編集
    Agent->>Codebase: 自動テスト実行 (pytest / asdlc eval)
    Agent->>Walkthrough: walkthrough.md を作成・エビデンス封印
    Agent->>User: 完了報告
    end
```

---

## 1. Phase 1: 事前計画と人間承認 (Planning Mode)

エージェントはいかなる非自明なソースコード変更も、人間による明示的承認（[Proceed] ボタンの押下）を得る前に行ってはなりません。

### Proceed ボタンを確実に発火させるための 4 大鉄則

Antigravity の UI パーサーが `implementation_plan.md` を「実行可能計画」と認識して `[Proceed]` ボタンを表示するためには、以下の 4 条件の **100% 同時達成** が必須です。

1. **正規パスへの配置**:
   - 配置パス: `<appDataDir>\brain\<conversation-id>/implementation_plan.md`
   - ワークスペース配下（例: `.devs/...` 等）ではなく、必ず Antigravity 公式の brain ディレクトリに出力すること。

2. **必須英語見出しの完全一致（翻訳・改変・独自追加による置換の全面禁止）**:
   - UI パーサーは以下の **英語見出し** を正規表現で検出します。日本語化したり、類似の独自見出し（例: `## 変更対象ファイルと提案内容` 等）に置き換えるとパーサーをすり抜け、**Proceed ボタンが消滅** します。
   - 以下の完全テンプレートを厳格に維持してください：

   ```markdown
   # [Goal Description]

   Provide a brief description of the problem, any background context, and what the change accomplishes.

   ## User Review Required

   Document anything that requires user review or feedback, for example, breaking changes or significant design decisions. Use GitHub alerts (IMPORTANT/WARNING/CAUTION) to highlight critical items.

   ## Open Questions

   Any clarifying or design questions for the user that will impact the implementation plan. (If none, explicitly write "None".)

   ## Proposed Changes

   Group files by component (e.g., package, feature area, dependency layer) and order logically (dependencies first). Separate components with horizontal rules for visual clarity.

   ### [Component Name]

   Summary of what will change in this component, separated by files:
   #### [MODIFY] [file basename](file:///absolute/path/to/modifiedfile)
   #### [NEW] [file basename](file:///absolute/path/to/newfile)
   #### [DELETE] [file basename](file:///absolute/path/to/deletedfile)

   ## Verification Plan

   Summary of how you will verify that your changes have the desired effects.

   ### Automated Tests
   - The commands of any automated tests you'll run.

   ### Manual Verification
   - Manual verification steps.
   ```

3. **`write_to_file` 呼び出し時の `ArtifactMetadata` 必須指定**:
   - `implementation_plan.md` 書き込み時は、必ず以下のメタデータを付与すること：
     - `RequestFeedback: true` (Proceed ボタン生成のトリガーフラグ)
     - `UserFacing: true`
     - `Summary: "<変更概要の簡潔な説明>"`
   - ※ `ask_question` ツールの呼び出しは禁止です。疑問点はすべて `## Open Questions` に記載し、承認は UI の `[Proceed]` ボタンに一任します。

4. **計画出力直後のターン即時終了**:
   - 計画アーティファクト作成後は、チャットで計画内容を長文再要約してはなりません（UI の状態機械が質問中と誤認するのを防ぐため）。
   - 「実装計画を作成しました。内容をご確認いただき、よろしければ [Proceed] を押してください」等の簡潔な案内のみを出力し、**他のツール呼び出しを行わずにターンを終了** します。

---

## 2. Phase 2: 自律実行と事後検証 (Walkthrough Sealing)

ユーザーが `[Proceed]` ボタンを押下（`<USER_REQUEST>Proceed</USER_REQUEST>`）したことを確認した後、エージェントは自律的に実装を実行し、事後エビデンスを封印します。

### 手順
1. **安全な実装**:
   - 計画に記載されたファイルのみを変更し、計画外のスコープ逸脱を行わない。
   - 既存のコメント・スタイルの維持と変更の最小化。
2. **検証テストの自動実行**:
   - `python -m pytest` 等の自動テストスイートを実行。
   - 失敗した場合は直ちに自己修復し、全件 Green になるまで検証を反復。
3. **ASDLC 実機検証**:
   - `python -m asdlc.cli.main eval` 等を実行し、静的評価・ルーブリック評価が 100.0 点満点であることを確認。
4. **`walkthrough.md` の出力**:
   - 配置パス: `<appDataDir>\brain\<conversation-id>/walkthrough.md`
   - 実装内容、実行されたテストログ、検証結果、Before/After 差分を記録。
   - `ArtifactMetadata(UserFacing=true, RequestFeedback=false)` を設定。
5. **ユーザーへの最終完了報告**:
   - 成果物リンクを提示して完了を報告。

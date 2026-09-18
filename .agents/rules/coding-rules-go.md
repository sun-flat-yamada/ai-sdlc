---
description: "Language-specific coding rules for Go enforcing Go 1.22+, Effective Go, explicit error handling, table-driven tests, and goroutine safety."
globs: ["**/*.go"]
always_on: false
---

# ASDLC Go Coding Governance Rules (Go 固有コーディング規約)

本規約は、Go 開発において適用される Tier 2 言語特化ナレッジパックです。

---

## 1. ランタイム & 言語仕様
- **対象バージョン**: Go 1.22 以上。
- **Effective Go 原則**:
  - パニック（`panic` / `recover`）を通常の制御フローとして使用することを厳禁とする（致命的な起動時設定エラー等を除く）。
  - 名前付き戻り値の乱用を避け、可読性を優先する。

---

## 2. 明示的エラーハンドリング (Explicit Error Handling)
- **Error Wrapping & Inspection**:
  - エラーを無視（`_ = fn()`）してはならない。必ず直ちにハンドリングする。
  - Go 1.13+ 標準の `fmt.Errorf("...: %w", err)` によるエラーラップ、および `errors.Is`, `errors.As` による判定を徹底する。

---

## 3. 並行処理 & リソース管理
- **Goroutine リーク防止**:
  - すべての非同期 goroutine にはライフサイクル制御（`context.Context` またはキャンセルチャネル）を紐付け、孤立 goroutine を作らない。
- **同期制御**:
  - チャネルまたは `sync.Mutex` / `sync.RWMutex` / `sync/atomic` を適切に使い分け、データ競合（Data Race）を撲滅する（`-race` フラグ検証必須）。

---

## 4. テスト駆動開発 (testing)
- **テスト基盤**: 標準 `testing` パッケージを採用。
- **テーブル駆動テスト (Table-Driven Tests)**:
  - 構造体スライス `tests := []struct{ name string; ... }` と `t.Run(tt.name, func(t *testing.T) { ... })` によるテーブル駆動テストを標準パターンとする。

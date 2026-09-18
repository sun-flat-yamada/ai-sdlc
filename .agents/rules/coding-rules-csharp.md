---
description: "Language-specific coding rules for C# enforcing C# 12+ / .NET 8+, Nullable Reference Types, records, async/await best practices, and xUnit TDD."
globs: ["**/*.cs"]
always_on: false
---

# ASDLC C# Coding Governance Rules (C# 固有コーディング規約)

本規約は、C# / .NET 開発において適用される Tier 2 言語特化ナレッジパックです。

---

## 1. ランタイム & 言語仕様
- **対象バージョン**: C# 12 以上 / .NET 8 以上（LTS 推奨）。
- **最新言語機能の標準活用**:
  - 不変エンティティ・DTO には `record` / `record struct` を使用し、値の等価性とイミュータビリティを担保する。
  - プライマリコンストラクタ（Primary Constructors）を活用し、依存関係の注入を簡潔に記述する。
  - パターンマッチング（`switch` 式、プロパティパターン）を用いて可読性を向上させる。

---

## 2. Null 安全性 (Nullable Reference Types)
- **Null 許容参照型の有効化**:
  - すべてのプロジェクトで `<Nullable>enable</Nullable>` を必須とする。
  - Null 非許容プロパティの初期化漏れ（CS8618）を放置せず、必須プロパティには `required` 修飾子またはコンストラクタ初期化を徹底する。
  - 未検証の `!`（null 免除演算子）の多用を禁止し、パターンマッチングや `ArgumentNullException.ThrowIfNull` による防御的検証を行うこと。

---

## 3. 非同期処理 & リソース管理
- **async / await の規律**:
  - `async void` の使用を禁止（イベントハンドラを除く）。必ず `Task` または `Task<T>`、高頻度アロケーションには `ValueTask<T>` を返すこと。
  - 長時間実行や I/O 処理には必ず `CancellationToken` を引数として伝播させ、適切なキャンセル処理を実装すること。
  - 非同期処理の同期ブロック（`.Result` や `.Wait()`）を厳禁とし、デッドロックを防止する。
- **リソース解放**:
  - `IDisposable` / `IAsyncDisposable` を実装するオブジェクトは `using var` 宣言または `await using` で確実に破棄すること。

---

## 4. パフォーマンス & メモリ効率
- **不要な割り当ての排除**:
  - 大量データや文字列処理では `ReadOnlySpan<T>`、`Memory<T>`、`ArrayPool<T>` を活用し、ヒープアロケーションと GC 負荷を抑制する。

---

## 5. テスト駆動開発 (xUnit)
- **テスト基盤**: `xUnit` を標準テストフレームワークとし、`FluentAssertions` および `Moq` / `NSubstitute` を併用する。
- **受入基準テスト**:
  - `[Fact]` / `[Theory]` と `[InlineData]` を用いて Given-When-Then 受入基準および境界値テストを網羅すること。

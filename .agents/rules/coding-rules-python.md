---
description: "Language-specific coding rules for Python enforcing Python 3.10+, PEP 8, Pydantic v2 type safety, pytest TDD, and asyncio best practices."
globs: ["**/*.py"]
always_on: false
---

# ASDLC Python Coding Governance Rules (Python 固有コーディング規約)

本規約は、Python 開発において適用される Tier 2 言語特化ナレッジパックです。

---

## 1. ランタイム & 言語仕様
- **対象バージョン**: Python 3.10 以上（最新安定板推奨）。
- **最新構文の積極活用**:
  - 型ヒントにおける PEP 604 ユニオン構文（`int | str`）を推奨し、レガシーな `Union[int, str]` の使用を避ける。
  - パターンマッチング（`match/case`）を適切に活用して複雑な条件分岐を平坦化する。

---

## 2. 型安全性 & バリデーション
- **Pydantic v2 の標準採用**:
  - 外部 I/O、設定管理、API リクエスト/レスポンス、ドメインエンティティには `pydantic.BaseModel` を使用し、実行時型バリデーションを徹底する。
- **型アノテーションの厳格化**:
  - すべてのパブリック関数・メソッドに引数と戻り値の型ヒントを必須とする。
  - 曖昧な `Any` の多用を避け、ジェネリクス（`TypeVar`）や `Protocol` を用いて型安全性を担保する。

---

## 3. コード品質 & 静的解析
- **Ruff 準拠**:
  - PEP 8 スタイル、インポート順序（isort 準拠）、未使用変数・インポートの撲滅。
  - 循環インポートを厳禁とし、必要に応じて型チェック時限定の `from typing import TYPE_CHECKING` を活用する。

---

## 4. 非同期処理 & ロギング
- **asyncio 設計**:
  - 非同期関数内で同期ブロッキング処理（`time.sleep` や同期 I/O）を実行してはならない。
- **構造化ロギング**:
  - `print` 文によるデバッグ出力の本番混入を禁止。標準ライブラリの `logging` または構造化ロガーを使用し、JSON形式での出力に対応させる。

---

## 5. テスト駆動開発 (pytest)
- **テスト基盤**: `pytest` を標準テストランナーとする。
- **フィクスチャとモック**:
  - `unittest.mock` または `pytest-mock` を用い、外部依存（DB、外部API）を確実に隔離したユニットテストを作成する。
  - Given-When-Then 構造に基づき、境界値・例外発生系を含むテストケースを網羅する。

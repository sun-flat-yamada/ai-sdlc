---
description: "Language-specific coding rules for C++ enforcing C++20/C++23 standards, RAII, smart pointers, exception safety, and GoogleTest/Catch2 TDD."
globs: ["**/*.cpp", "**/*.hpp", "**/*.cc", "**/*.cxx", "**/*.hxx"]
always_on: false
---

# ASDLC C++ Coding Governance Rules (C++ 固有コーディング規約)

本規約は、モダン C++ 開発において適用される Tier 2 言語特化ナレッジパックです。

---

## 1. 言語標準 & モダン C++ イディオム
- **対象バージョン**: ISO/IEC C++20 または C++23 標準。
- **モダン機能の標準適用**:
  - `std::string_view` および `std::span` によるゼロコピー引数受け渡し。
  - Concepts（制約テンプレート）を用いた型安全なジェネリクス設計。
  - `auto` の適切な使用（冗長な型宣言の平坦化）。

---

## 2. リソース管理 & ポインタ安全性 (RAII Principle)
- **生ポインタによるリソース所有の禁止**:
  - `new` / `delete` の直接使用を厳禁とする。
  - リソース所有には `std::unique_ptr` を基本とし、共有が必要な場合のみ `std::shared_ptr` / `std::weak_ptr` を使用する。
- **Rule of Zero / Five**:
  - デストラクタ・コピーコンストラクタ・ムーブコンストラクタ・代入演算子の設計は RAII クラス（スマートポインタ、標準コンテナ）に任せ、「Rule of Zero」を最優先とする。
  - カスタムリソース管理クラスを作成する場合は「Rule of Five」を厳格に実装すること。

---

## 3. 型安全 & 例外安全性
- **キャスト規則**:
  - Cスタイルキャスト `(Type)val` を全面禁止。必ず `static_cast`, `dynamic_cast`, `reinterpret_cast`, `const_cast` を意図を明確にして使い分けること。
- **例外安全性保証**:
  - 基本保証（Basic Guarantee）および強い例外安全保証（Strong Exception Guarantee）を意識した設計を行う。
  - 例外を投げない関数には明示的に `noexcept` を付与し、最適化と安全性を高める。

---

## 4. 静的解析 & サニタイザー
- **Clang-Tidy 準拠**:
  - `modernize-*`, `cppcoreguidelines-*`, `bugprone-*` チェックを必須とする。
- **サニタイザー検証**:
  - CI パイプラインおよびローカル検証において `ASan` (AddressSanitizer) および `UBSan` (UndefinedBehaviorSanitizer) を有効化してテストを実行すること。

---

## 5. テスト駆動開発 (GoogleTest / Catch2)
- **テスト基盤**: `GoogleTest (gtest)` または `Catch2` を採用。
- **受入基準テスト**:
  - `TEST(AcceptanceCriteria, GivenWhenThenScenario)` マクロ等を用い、受入基準・境界条件・例外送出（`EXPECT_THROW`）を検証すること。

---
description: "Language-specific coding rules for C enforcing C11/C17/C23 standards, memory safety, buffer overflow prevention, explicit error codes, and Unity/CUnit TDD."
globs: ["**/*.c", "**/*.h"]
always_on: false
---

# ASDLC C Coding Governance Rules (C 言語固有コーディング規約)

本規約は、C 言語開発において適用される Tier 2 言語特化ナレッジパックです。

---

## 1. 言語標準 & コンパイラ警告
- **対象バージョン**: ISO/IEC C11 / C17 / C23 標準。
- **厳格なコンパイル警告**:
  - GCC / Clang において `-Wall -Wextra -Wpedantic -Werror -Wformat=2 -Wconversion -Wshadow` を必須とする。
  - すべての暗黙の型変換や符号付き/符号なしの比較警告を解消すること。

---

## 2. メモリ安全性 & バッファオーバーフロー対策
- **安全な関数使用の強制**:
  - `gets()`, `strcpy()`, `strcat()`, `sprintf()` 等の境界未検証関数の使用を厳禁とする。
  - 代替として `strncpy()`, `strncat()`, `snprintf()`、または境界チェック付き関数を使用すること。
- **動的メモリ管理 (Dynamic Memory Management)**:
  - `malloc()` / `calloc()` の戻り値の NULL チェックを必須とする。
  - メモリ割り当てと解放（`free`）のライフサイクル所有権を明確にし、解放後はポインタに直ちに `NULL` を代入して Use-After-Free を防止する。
  - ポインタ演算の乱用を避け、配列のインデックス境界外アクセスを厳重に排除する。

---

## 3. エラーハンドリング & 戻り値検証
- **戻り値チェックの徹底**:
  - システムコールや標準ライブラリ関数の戻り値ステータス（-1 や NULL）を必ず検証すること。
- **型定義と列挙型**:
  - `typedef enum { STATUS_OK = 0, STATUS_ERR = -1, ... } Status_t;` 等の明示的なステータス型を定義し、エラーコードを契約化する。

---

## 4. 静的解析 & 動的サニタイザー
- **解析ツール適用**:
  - `Cppcheck` および `Clang-Tidy` による静的解析をパスすること。
  - テスト実行時は `AddressSanitizer (-fsanitize=address,undefined)` を有効化し、メモリリーク・UB（未定義動作）を検知・撲滅すること。

---

## 5. テスト駆動開発 (Unity / CUnit)
- **テスト基盤**: `Unity`、`CUnit`、または `GoogleTest`（C++ラッパー）を採用。
- **受入基準テスト**:
  - Given-When-Then 構造に基づき、正常系・NULLポインタ引数・境界値バッファ・メモリ枯渇時のフェイルセーフを検証するテストケースを網羅すること。

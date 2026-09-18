---
description: "Language-specific coding rules for TypeScript/JavaScript enforcing TypeScript 5+, Strict Mode, noImplicitAny, Zod schema validation, and Vitest TDD."
globs: ["**/*.ts", "**/*.tsx", "**/*.js", "**/*.jsx"]
always_on: false
---

# ASDLC TypeScript Coding Governance Rules (TypeScript 固有コーディング規約)

本規約は、TypeScript / JavaScript 開発において適用される Tier 2 言語特化ナレッジパックです。

---

## 1. ランタイム & コンパイラ設定
- **対象バージョン**: TypeScript 5.0 以上。
- **Strict Mode 必須**:
  - `tsconfig.json` において `"strict": true` を有効化する。
  - `noImplicitAny`, `strictNullChecks`, `exactOptionalPropertyTypes` を遵守し、暗黙の `any` を厳禁とする。
  - やむを得ず型が定まらない場合は `unknown` を使用し、型ガード（Type Narrowing）を適用する。

---

## 2. スキーマ駆動型バリデーション (Zod)
- **境界防御 (Boundary Defense)**:
  - 外部入力（API リクエストボディ、URL パラメータ、環境変数、JSON）は必ず `zod` スキーマでパース・検証し、型推論（`z.infer<typeof Schema>`）を活用する。

---

## 3. モジュールシステム & コーディング規約
- **ES Modules (ESM) 原則**:
  - `import / export` を統一使用し、CommonJS の `require()` の使用を禁止する。
- **ドキュメンテーション**:
  - 公開インターフェース・関数には JSDoc/TSDoc コメントを記述し、パラメータの意味と例外条件を明記する。

---

## 4. テスト駆動開発 (Vitest / Jest)
- **テスト基盤**: `Vitest`（Node.js/Next.js/Vite）または `Jest` を標準テストランナーとする。
- **BDD/TDD 構造**:
  - `describe` / `it` / `expect` を用い、受入基準の Given-When-Then 条件を検証する。
  - 非同期テストには必ず `async/await` を使用し、Promise のアンハンドルド・リジェクトを防止する。

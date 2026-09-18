---
description: "Universal language-agnostic coding governance rules enforcing OWASP security, Clean Architecture/SRP, spec acceptance criteria, and anti-reinvention of components."
globs: ["**/*"]
always_on: true
---

# ASDLC Universal Coding Governance Rules (全社共通・言語非依存コーディング規約)

本プロジェクトにおけるすべてのソースコード生成・変更は、プログラミング言語・ランタイムを問わず、以下の普遍的ガバナンスを不可侵の制約として厳格に遵守しなければなりません。

---

## 1. 3層コンテキスト優先構造の遵守 (Context Priority Rule)
1. **Tier 1 (不可侵全社普遍ガバナンス - Language-Agnostic Core)**:
   - パスワード・APIキー・シークレットの平文ハードコードを全面厳禁とする（必ず環境変数またはKMS経由で取得）。
   - すべての外部ネットワーク通信は暗号化通信（HTTPS/TLS）を必須とする。
   - SQLクエリ等のデータソース呼び出しは直接文字列結合を禁止し、ORMまたはパラメータ化プレースホルダーを強制する。
2. **Tier 2 (言語・ランタイム別ナレッジパック - Language-Specific Packs)**:
   - 対象言語（Python, TypeScript, Go等）の公式標準規約・型安全性・リンター規約に厳格に準拠する。
3. **Tier 3 (コンポーネントカタログ & 車輪の再発明撲滅 - Anti-Reinvention)**:
   - 既存知財の重複実装（車輪の再発明）を禁止する。認証、UIテーブル、監査ロガー、エラーハンドラーなどの基盤処理は、MCP ComponentRegistry から検索して社内標準部品をインポートすること。
4. **Tier 4 (開発者個別意図 - Local Intent)**:
   - 開発者の指示・ドメインロジックは上位制約（Tier 1〜3）に反しない範囲で正確に具現化すること。

---

## 2. テスト駆動開発と受入基準の義務化 (Zero Untested Code Rule)
- 自動テストのないコードを生成・納品してはならない。
- 新規モジュールやAPIエンドポイントを作成する場合、必ず仕様書の受入基準（Given-When-Then）に対応する自動テストコードを先行または同時に生成すること。
- 対象言語の標準テストランナーによるテスト実行が全件合格（100% Green）することを確認すること。

---

## 3. 型安全とコンポーザブル疎結合 (Type Safety & Loose Coupling)
- 各言語における最強の静的型付け機構・バリデーション機構を有効化し、未検証な動的型の乱用を避けること。
- モジュール間の循環インポート・循環依存を禁止し、単一責任の原則（SRP）に従ってインターフェースと実装を疎結合に保つこと。


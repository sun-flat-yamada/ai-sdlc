from typing import Dict, Any, List, Optional
from enum import Enum
import re
from pathlib import Path

class TargetLanguage(str, Enum):
    PYTHON = "python"
    TYPESCRIPT = "typescript"
    GO = "go"
    C = "c"
    CPP = "cpp"
    CSHARP = "csharp"
    AGNOSTIC = "agnostic"

class CodingAgent:
    """
    ③ Coding Agent:
    エンジニアに意識させない開発標準化とコンポーザブル知財再利用を司るエージェント。
    2026年最新の「4層知識階層 (Layered Knowledge Architecture)」を厳格に適用：
      Tier 1: 言語非依存・全社普遍ガバナンス (OWASP, Clean Architecture, Given-When-Then, 車輪の再発明撲滅)
      Tier 2: 言語別ナレッジパック (Python/TypeScript/Go/C/C++/C# 等の動的射影)
      Tier 3: 多言語コンポーネントカタログ (MCP ComponentRegistry 経由)
      Tier 4: 開発者個別意図 (Local Intent & Prompt)
    """

    def __init__(self, mcp_client=None):
        self.mcp_client = mcp_client
        self._init_component_catalog()

    def _init_component_catalog(self):
        """多言語対応コンポーネントカタログの初期化"""
        self.component_catalog = {
            # --- TypeScript / Frontend ---
            "ts_jwt_auth": {
                "id": "auth-jwt-ts",
                "name": "@enterprise/jwt-auth-middleware",
                "language": TargetLanguage.TYPESCRIPT.value,
                "version": "2.4.0",
                "description": "全社標準OAuth2/JWT認証・RBAC認可ミドルウェア (Express/Fastify/Next.js)",
                "recommended_for": ["login", "authentication", "jwt", "auth", "oauth", "認証", "ログイン"],
                "import_statement": "import { JWTAuthGuard, requireRoles } from '@enterprise/jwt-auth-middleware';"
            },
            "ts_ui_datagrid": {
                "id": "ui-datagrid-ts",
                "name": "@enterprise/ui-datagrid",
                "language": TargetLanguage.TYPESCRIPT.value,
                "version": "3.1.2",
                "description": "アクセシビリティ・ソート・ページネーション準拠データグリッドコンポーネント",
                "recommended_for": ["table", "list", "datatable", "grid", "datagrid", "一覧", "テーブル", "画面"],
                "import_statement": "import { EnterpriseDataGrid } from '@enterprise/ui-datagrid';"
            },
            "ts_logger": {
                "id": "logger-ts",
                "name": "@enterprise/structured-logger",
                "language": TargetLanguage.TYPESCRIPT.value,
                "version": "1.8.0",
                "description": "OpenTelemetry対応構造化監査ロガー (Node.js/Browser)",
                "recommended_for": ["log", "logging", "audit", "trace", "ログ", "監査"],
                "import_statement": "import { AuditLogger } from '@enterprise/structured-logger';"
            },
            # --- Python / Backend ---
            "py_jwt_auth": {
                "id": "auth-jwt-py",
                "name": "corp_auth.jwt",
                "language": TargetLanguage.PYTHON.value,
                "version": "2.1.0",
                "description": "全社標準OAuth2/JWT認証・RBAC認可ミドルウェア (FastAPI/Flask)",
                "recommended_for": ["login", "authentication", "jwt", "auth", "oauth", "認証", "ログイン"],
                "import_statement": "from corp_auth.jwt import JWTAuthGuard, require_roles"
            },
            "py_logger": {
                "id": "logger-py",
                "name": "corp_audit.logger",
                "language": TargetLanguage.PYTHON.value,
                "version": "2.0.0",
                "description": "OpenTelemetry対応構造化監査ロガー (Python 3.10+)",
                "recommended_for": ["log", "logging", "audit", "trace", "ログ", "監査"],
                "import_statement": "from corp_audit.logger import AuditLogger"
            },
            "py_errors": {
                "id": "errors-py",
                "name": "corp_common.errors",
                "language": TargetLanguage.PYTHON.value,
                "version": "1.4.0",
                "description": "RFC 7807準拠 ProblemDetails 例外ハンドリング基盤",
                "recommended_for": ["error", "exception", "problemdetails", "エラー", "例外"],
                "import_statement": "from corp_common.errors import ProblemDetailsMiddleware"
            },
            # --- Go / Systems ---
            "go_jwt_auth": {
                "id": "auth-jwt-go",
                "name": "go.corp/auth/jwt",
                "language": TargetLanguage.GO.value,
                "version": "1.2.0",
                "description": "全社標準OAuth2/JWT認証ミドルウェア (net/http, Gin, Echo)",
                "recommended_for": ["login", "authentication", "jwt", "auth", "oauth", "認証", "ログイン"],
                "import_statement": 'import "go.corp/auth/jwt"'
            },
            "go_logger": {
                "id": "logger-go",
                "name": "go.corp/telemetry/logger",
                "language": TargetLanguage.GO.value,
                "version": "1.5.0",
                "description": "高スループット構造化監査ロガー (uber-go/zapベース)",
                "recommended_for": ["log", "logging", "audit", "trace", "ログ", "監査"],
                "import_statement": 'import "go.corp/telemetry/logger"'
            },
            # --- C / Embedded & Systems ---
            "c_sec_buffer": {
                "id": "sec-buffer-c",
                "name": "@enterprise/c-sec-buffer",
                "language": TargetLanguage.C.value,
                "version": "1.1.0",
                "description": "境界検証・バッファオーバーフロー防止セキュアメモリ管理基盤",
                "recommended_for": ["buffer", "memory", "overflow", "バッファ", "メモリ", "組込み"],
                "import_statement": "#include <enterprise/sec_buffer.h>"
            },
            # --- C++ / Modern Systems ---
            "cpp_safe_ptr": {
                "id": "safe-ptr-cpp",
                "name": "@enterprise/cpp-safe-ptr",
                "language": TargetLanguage.CPP.value,
                "version": "2.0.0",
                "description": "RAIIセキュアリソース管理・スマートポインタ・ゼロコピー基盤",
                "recommended_for": ["raii", "pointer", "memory", "スマートポインタ", "ポインタ", "低遅延"],
                "import_statement": "#include <enterprise/safe_ptr.hpp>"
            },
            # --- C# / .NET Enterprise ---
            "cs_jwt_auth": {
                "id": "auth-jwt-csharp",
                "name": "Enterprise.Security.Authentication",
                "language": TargetLanguage.CSHARP.value,
                "version": "3.0.0",
                "description": "全社標準OAuth2/JWT認証・RBAC認可ミドルウェア (ASP.NET Core / .NET 8+)",
                "recommended_for": ["login", "authentication", "jwt", "auth", "oauth", "認証", "ログイン"],
                "import_statement": "using Enterprise.Security.Authentication;"
            },
            "cs_logger": {
                "id": "audit-logger-csharp",
                "name": "Enterprise.Diagnostics.Logging",
                "language": TargetLanguage.CSHARP.value,
                "version": "2.2.0",
                "description": "OpenTelemetry対応構造化監査ロガー (.NET 8+ / Serilog連携)",
                "recommended_for": ["log", "logging", "audit", "trace", "ログ", "監査"],
                "import_statement": "using Enterprise.Diagnostics.Logging;"
            }
        }

    def detect_target_language(self, intent_description: str, file_hint: Optional[str] = None) -> TargetLanguage:
        """プロンプトやファイル名からターゲットプログラミング言語を自動検出"""
        if file_hint:
            ext = Path(file_hint).suffix.lower()
            if ext in [".py", ".pyi"]:
                return TargetLanguage.PYTHON
            elif ext in [".ts", ".tsx", ".js", ".jsx"]:
                return TargetLanguage.TYPESCRIPT
            elif ext in [".go"]:
                return TargetLanguage.GO
            elif ext in [".c", ".h"]:
                return TargetLanguage.C
            elif ext in [".cpp", ".hpp", ".cc", ".cxx", ".hxx"]:
                return TargetLanguage.CPP
            elif ext in [".cs"]:
                return TargetLanguage.CSHARP

        text = intent_description.lower()

        # C# (.NET) keywords
        if any(k in text for k in ["c#", "csharp", "dotnet", ".net", "nuget", "xunit", "entity framework", "asp.net", "linq"]):
            return TargetLanguage.CSHARP

        # C++ keywords
        if any(k in text for k in ["c++", "cpp", "googletest", "gtest", "catch2", "cmake", "boost", "raii", "スマートポインタ"]):
            return TargetLanguage.CPP

        # C keywords
        if any(k in text for k in ["c言語", "embedded", "組込み", "組み込み", "c11", "c17", "c23", "valgrind", "malloc"]):
            return TargetLanguage.C
        if re.search(r"\bc\s+(?:言語|プログラム|コード|モジュール)\b", text) or re.search(r"\b言語\s*:\s*c\b", text):
            return TargetLanguage.C

        # TypeScript / JavaScript keywords
        if any(k in text for k in ["typescript", "ts", "javascript", "react", "vue", "next", "vitest", "jest", "npm", "pnpm", "node"]):
            return TargetLanguage.TYPESCRIPT

        # Go keywords
        if any(k in text for k in ["golang", "go言語", "goroutine", "gin", "gorm", "go test"]):
            return TargetLanguage.GO
        if re.search(r"\bgo\b", text):
            return TargetLanguage.GO

        # Python keywords
        if any(k in text for k in ["python", "fastapi", "django", "flask", "pydantic", "pytest", "ruff", "pip", "uv"]):
            return TargetLanguage.PYTHON

        # デフォルト判定 (UIや画面に言及があればTypeScript、それ以外はPython)
        if any(k in text for k in ["画面", "フロント", "コンポーネント", "ui"]):
            return TargetLanguage.TYPESCRIPT

        return TargetLanguage.PYTHON

    def get_agnostic_governance_rules(self) -> List[str]:
        """Tier 1: 言語非依存・全社普遍ガバナンス規約 (不可侵Core)"""
        return [
            "【全社セキュリティ規約 (OWASP Top 10)】パスワード・APIキー・シークレットの平文ハードコードを全面厳禁とする。環境変数またはKMSから取得せよ。",
            "【通信ガバナンス】すべての外部ネットワーク通信は暗号化通信（HTTPS/TLS）を必須とする。",
            "【データ保護】SQLクエリ等の外部呼び出しは文字列結合を禁止し、ORMまたはパラメータ化プレースホルダーを使用せよ。",
            "【アーキテクチャ標準】Clean Architecture / 単一責任の原則 (SRP) を遵守し、疎結合なコンポーザブル設計を維持せよ。",
            "【TDD受入基準】仕様書の Given-When-Then 受入基準に対応した自動テストコードを必ず生成せよ（Zero Untested Code）。",
            "【知財再利用強制】車輪の再発明を禁止する。社内共通コンポーネントが存在する場合は独自実装せず再利用せよ。"
        ]

    def get_language_specific_rules(self, language: TargetLanguage) -> List[str]:
        """Tier 2: 言語・ランタイム特化ナレッジパック (動的射影)"""
        if language == TargetLanguage.PYTHON:
            return [
                "【Python 3.10+ 標準】型ヒントにおける PEP 604 ユニオン構文 (`int | str`) を使用し、レガシーな `Union` を避けること。",
                "【Pydantic v2 型安全性】外部 I/O やエンティティには `pydantic.BaseModel` を適用し、厳格なバリデーションを行うこと。",
                "【コード品質】PEP 8 および Ruff に準拠し、曖昧な `Any` の多用や循環インポートを排除すること。",
                "【非同期設計】asyncio 内での同期ブロッキング処理を禁止すること。",
                "【テスト規約】`pytest` を用い、Given-When-Then 受入基準および境界値・例外系テストを網羅すること。"
            ]
        elif language == TargetLanguage.TYPESCRIPT:
            return [
                "【TypeScript Strict Mode】tsconfig の `strict: true` 必須。`any` 型の使用を禁止し、未確定型には `unknown` と型ガードを用いること。",
                "【Zod スキーマ検証】外部入力（APIリクエスト、環境変数、JSON）は必ず Zod スキーマで境界防御を行うこと。",
                "【モジュール規約】ES Modules (ESM) を統一使用し、CommonJS の `require()` を禁止すること。",
                "【ドキュメンテーション】すべての公開関数・型定義に JSDoc/TSDoc 形式の仕様コメントを付与すること。",
                "【テスト規約】`Vitest` または `Jest` を用い、`describe/it/expect` で受入基準を検証すること。"
            ]
        elif language == TargetLanguage.GO:
            return [
                "【Effective Go】パニック（`panic/recover`）を通常の制御フローに使用せず、明示的エラーハンドリングを徹底すること。",
                "【明示的エラー処理】エラーは無視せず直ちに処理し、`fmt.Errorf(\"...: %w\", err)` によるラップと `errors.Is/As` 判定を行うこと。",
                "【並行処理安全性】すべての goroutine に `context.Context` ライフサイクルを紐付け、データ競合（Race condition）を撲滅すること。",
                "【テスト規約】標準 `testing` パッケージによるテーブル駆動テスト (`tests := []struct{...}`) を採用すること。"
            ]
        elif language == TargetLanguage.C:
            return [
                "【C11/C17/C23 標準】厳格なコンパイラ警告 (`-Wall -Wextra -Wpedantic -Werror -Wconversion`) を遵守すること。",
                "【メモリ安全性】`gets`, `strcpy`, `sprintf` 等の境界未検証関数を厳禁とし、`strncpy`, `snprintf` またはセキュア関数を使用すること。",
                "【ポインタ管理】動的メモリの NULL チェックを必須とし、`free` 後の直ちなる `NULL` 代入により Use-After-Free を防止すること。",
                "【静的解析 & サニタイザー】`Clang-Tidy`, `Cppcheck` を適用し、テスト時は `AddressSanitizer (-fsanitize=address,undefined)` を有効化すること。",
                "【テスト規約】Unity / CUnit による Given-When-Then 受入基準および NULL 引数・境界値テストを網羅すること。"
            ]
        elif language == TargetLanguage.CPP:
            return [
                "【C++20/C++23 モダン規約】`std::string_view`, `std::span` によるゼロコピー受け渡しおよび Concepts による型安全制約を適用すること。",
                "【RAII & ポインタ安全性】`new`/`delete` の直接使用を厳禁とし、`std::unique_ptr` / `std::shared_ptr` と「Rule of Zero/Five」を徹底すること。",
                "【キャスト & 例外安全】Cスタイルキャストを全面禁止し、`static_cast` 等を使用すること。例外を投げない関数には `noexcept` を明示すること。",
                "【サニタイザー検証】`ASan` (AddressSanitizer) および `UBSan` を有効化してメモリリーク・未定義動作を撲滅すること。",
                "【テスト規約】GoogleTest (`TEST(AcceptanceCriteria, ...)` / `EXPECT_THROW`) または Catch2 で受入基準を検証すること。"
            ]
        elif language == TargetLanguage.CSHARP:
            return [
                "【C# 12+ / .NET 8+】不変エンティティには `record` を使用し、プライマリコンストラクタとパターンマッチングを活用すること。",
                "【Null 許容参照型】`<Nullable>enable</Nullable>` を必須とし、必須プロパティには `required` 修飾子、事前検証には `ArgumentNullException.ThrowIfNull` を用いること。",
                "【非同期 & リソース管理】`async void` を禁止し、`CancellationToken` を伝播させること。`using var` / `await using` でリソース破棄を徹底すること。",
                "【メモリ効率】不要なヒープアロケーションを抑え、高頻度処理には `ReadOnlySpan<T>` や `ValueTask<T>` を活用すること。",
                "【テスト規約】`xUnit` (`[Fact]`, `[Theory]`) および `FluentAssertions` により Given-When-Then 受入基準を網羅すること。"
            ]
        return [
            "【言語標準】対象言語の公式スタイルガイドラインおよび最強の型検査・リンター規約に準拠すること。"
        ]

    def search_reusable_components(
        self,
        intent_description: str,
        target_language: Optional[TargetLanguage] = None
    ) -> List[Dict[str, Any]]:
        """MCP ComponentRegistry をセマンティック照合し、推奨部品を言語フィルタ付きで検索"""
        intent = intent_description.lower()
        matched = []
        
        for key, comp in self.component_catalog.items():
            if any(tag in intent for tag in comp["recommended_for"]):
                matched.append(comp)

        # ターゲット言語が指定されている場合、その言語の部品を上位にソート
        if target_language and target_language != TargetLanguage.AGNOSTIC:
            matched.sort(
                key=lambda x: 0 if x.get("language") == target_language.value else 1
            )
            
        return matched

    def synthesize_code_context(
        self,
        developer_prompt: str,
        lang: Optional[str] = None,
        file_hint: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        4層知識優先構造に基づき、コーディングコンテキストを動的に合成する。
        後方互換性のため layer_1_governance / layer_2_standards / layer_3_developer_intent も維持。
        """
        target_lang = TargetLanguage(lang) if lang and lang in [l.value for l in TargetLanguage] else self.detect_target_language(developer_prompt, file_hint)
        
        # Tier 1: 言語非依存普遍ガバナンス
        tier1_agnostic = self.get_agnostic_governance_rules()
        
        # Tier 2: 言語特化ナレッジパック
        tier2_language_pack = self.get_language_specific_rules(target_lang)
        
        # Tier 3: 多言語コンポーネントカタログ
        reusable = self.search_reusable_components(developer_prompt, target_lang)
        
        tier3_catalog_standards = []
        if reusable:
            for comp in reusable:
                tier3_catalog_standards.append(
                    f"【推奨再利用コンポーネント ({comp['language'].upper()})】新規作成せず `{comp['name']}` ({comp['version']}) を再利用せよ: {comp['description']}\n  - インポート構文: `{comp.get('import_statement', comp['name'])}`"
                )
        else:
            tier3_catalog_standards.append("【アーキテクチャ標準】疎結合なコンポーザブルアーキテクチャ設計を維持せよ。")

        # 互換性 Layer 1 & Layer 2 の生成
        layer1_compat = list(tier1_agnostic)
        layer2_compat = list(tier2_language_pack) + list(tier3_catalog_standards)

        return {
            # 2026年最新 4層構造キー
            "tier_1_governance_agnostic": tier1_agnostic,
            "tier_2_language_pack": tier2_language_pack,
            "tier_3_standards_catalog": tier3_catalog_standards,
            "tier_4_developer_intent": developer_prompt,
            "detected_language": target_lang.value,
            # 後方互換キー
            "layer_1_governance": layer1_compat,
            "layer_2_standards": layer2_compat,
            "layer_3_developer_intent": developer_prompt,
            "reusable_components_detected": reusable
        }

    def generate_scaffolding(
        self,
        intent_description: str,
        lang: Optional[str] = None
    ) -> Dict[str, str]:
        """TDD先行テストとカタログ再利用コードのスキャフォールディングを多言語対応で合成"""
        target_lang = TargetLanguage(lang) if lang and lang in [l.value for l in TargetLanguage] else self.detect_target_language(intent_description)
        reusable = self.search_reusable_components(intent_description, target_lang)
        
        imports = []
        for r in reusable:
            stmt = r.get("import_statement", f"// {r['name']}")
            imports.append(f"{stmt} // Reused from {r['name']} ({r['version']}): {r['description']}")

        if target_lang == TargetLanguage.TYPESCRIPT:
            test_code = (
                "import { describe, it, expect, beforeEach } from 'vitest';\n\n"
                "describe('Acceptance Criteria Test Suite (TDD RED)', () => {\n"
                "  beforeEach(() => {\n"
                "    // Given: 初期状態および前提条件のセットアップ\n"
                "  });\n\n"
                "  it('test_acceptance_criteria: 正常系および受入基準の検証', async () => {\n"
                "    // When: 対象機能の実行\n"
                "    // Then: 結果・戻り値・副作用の検証\n"
                "    expect(true).toBe(true);\n"
                "  });\n"
                "});\n"
            )
        elif target_lang == TargetLanguage.GO:
            test_code = (
                "package main\n\n"
                "import (\n"
                "\t\"testing\"\n"
                ")\n\n"
                "// TestAcceptanceCriteria: Given-When-Then 受入基準に基づくテーブル駆動テスト (TDD RED)\n"
                "func TestAcceptanceCriteria(t *testing.T) {\n"
                "\ttests := []struct {\n"
                "\t\tname    string\n"
                "\t\t// Given: 入力パラメータ\n"
                "\t\twantErr bool\n"
                "\t}{\n"
                "\t\t{\n"
                "\t\t\tname: \"test_acceptance_criteria: 正常系実行\",\n"
                "\t\t\twantErr: false,\n"
                "\t\t},\n"
                "\t}\n"
                "\tfor _, tt := range tests {\n"
                "\t\tt.Run(tt.name, func(t *testing.T) {\n"
                "\t\t\t// When & Then: 対象実行と検証\n"
                "\t\t})\n"
                "\t}\n"
                "}\n"
            )
        elif target_lang == TargetLanguage.C:
            test_code = (
                "#include <stdio.h>\n"
                "#include <assert.h>\n\n"
                "// test_acceptance_criteria: Given-When-Then 受入基準に基づく自動先行テスト (TDD RED)\n"
                "void test_acceptance_criteria(void) {\n"
                "    // Given: 初期状態および前提条件のセットアップ\n"
                "    // When: 対象機能の実行\n"
                "    // Then: 結果・戻り値・副作用の検証\n"
                "    assert(1 == 1);\n"
                "}\n\n"
                "int main(void) {\n"
                "    test_acceptance_criteria();\n"
                "    printf(\"All C acceptance criteria passed.\\n\");\n"
                "    return 0;\n"
                "}\n"
            )
        elif target_lang == TargetLanguage.CPP:
            test_code = (
                "#include <gtest/gtest.h>\n\n"
                "// Given-When-Then 受入基準に基づく自動先行テスト (TDD RED)\n"
                "TEST(AcceptanceCriteriaTest, TestAcceptanceCriteria) {\n"
                "    // Given: 初期状態および前提条件のセットアップ\n"
                "    // When: 対象機能の実行\n"
                "    // Then: 結果・戻り値・副作用の検証\n"
                "    EXPECT_TRUE(true);\n"
                "}\n"
            )
        elif target_lang == TargetLanguage.CSHARP:
            test_code = (
                "using Xunit;\n\n"
                "namespace Enterprise.Tests\n"
                "{\n"
                "    public class AcceptanceCriteriaTests\n"
                "    {\n"
                "        [Fact]\n"
                "        public void TestAcceptanceCriteria()\n"
                "        {   // Given: 初期状態および前提条件のセットアップ\n"
                "            // When: 対象機能の実行\n"
                "            // Then: 結果・戻り値・副作用の検証\n"
                "            Assert.True(true);\n"
                "        }\n"
                "    }\n"
                "}\n"
            )
        else: # PYTHON
            test_code = (
                "import pytest\n\n"
                "def test_acceptance_criteria():\n"
                "    \"\"\"\n"
                "    Given-When-Then 受入基準に基づく自動先行テスト (TDD RED)\n"
                "    \"\"\"\n"
                "    # Given: 初期状態および前提条件のセットアップ\n"
                "    # When: 対象機能の実行\n"
                "    # Then: 結果・戻り値・副作用の検証\n"
                "    assert True\n"
            )

        return {
            "target_language": target_lang.value,
            "reusable_imports": "\n".join(imports) if imports else "# 既存共通部品の検出なし (新規モジュール作成)",
            "tdd_test_scaffold": test_code
        }

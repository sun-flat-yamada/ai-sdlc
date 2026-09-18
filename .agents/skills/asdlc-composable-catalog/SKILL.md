---
name: asdlc-composable-catalog
description: "Discovers, registers, and integrates reusable enterprise components via Model Context Protocol (MCP) to enforce Isolation Architecture and prevent reinventing the wheel across multiple languages."
version: "1.1.0"
tags: ["mcp", "component-catalog", "reusability", "composable-architecture", "polyglot", "asdlc"]
---

# ASDLC Composable Catalog Skill

本スキルは、全社中央ナレッジベース（Agent Knowledge Base）に登録された共通コンポーネントを、**MCP (Model Context Protocol)** 経由で言語別・機能別に探索・再利用し、「車輪の再発明（Reinventing the Wheel）」を撲滅するための手続きを定めます。

---

## 1. 多言語コンポーネントレジストリスキーマ (Component Registry Schema)

各コンポーネントは対象言語属性を保持してインデックス化され、MCPツール経由でセマンティック検索されます。

```yaml
id: "auth-jwt-guard"
name: "Enterprise JWT Authentication Middleware"
language: "python" # [python | typescript | go | agnostic]
layer: "security"
package: "corp_auth.jwt"
import_statement: "from corp_auth.jwt import JWTAuthGuard, require_roles"
description: "全社標準JWT認証・RBAC認可ミドルウェア。Token有効期限検証、秘密鍵ローテーション、監査ログ連携内蔵。"
tags: ["auth", "jwt", "security", "rbac", "middleware", "認証", "ログイン"]
dependencies: ["pyjwt>=2.8.0", "cryptography>=42.0.0"]
```

---

## 2. カタログ探索 & 自動インポート手順

1. **要求機能のキーワード・言語抽出**:
   - 開発者のプロンプトおよび仕様書から、基盤機能（認証、DB接続、ロギング、キャッシュ、UIテーブル等）と対象言語（Python/TS/Go等）を抽出。
2. **MCP セマンティック照合 & 言語フィルタリング**:
   - `MCP.search_components(query=..., language=...)` を呼び出し、対象言語に適合する既存知財（適合スコア $\ge 0.75$）をリストアップ。
3. **コード置換・インポートの強制**:
   - 新規に関数やクラスを一から実装するのではなく、社内標準パッケージのインポートコードを出力。
   - 独自実装を試みた場合は、警告フラグ `ANTI_REINVENTION_TRIGGERED` を発行してレビューで指摘。

---

## 3. 多言語標準配備カタログ一覧（例）

| コンポーネントID | 言語 | 名称・役割 | インポート文 |
| :--- | :--- | :--- | :--- |
| `auth-jwt-python` | Python | 全社標準OAuth2/JWT・RBAC認証 | `from corp_auth.jwt import JWTAuthGuard, require_roles` |
| `auth-jwt-ts` | TypeScript | 全社標準OAuth2/JWTミドルウェア | `import { JWTAuthGuard, requireRoles } from '@enterprise/jwt-auth-middleware';` |
| `auth-jwt-go` | Go | 全社標準OAuth2/JWTミドルウェア | `import "go.corp/auth/jwt"` |
| `ui-table-component` | TypeScript | 共通アクセシブルデータグリッド | `import { EnterpriseDataTable } from '@enterprise/ui-datagrid';` |
| `db-audit-logger-py` | Python | OpenTelemetry対応構造化監査ロガー | `from corp_audit.logger import AuditLogger` |
| `db-audit-logger-ts` | TypeScript | 構造化監査ロガー | `import { AuditLogger } from '@enterprise/structured-logger';` |
| `db-audit-logger-go` | Go | 高スループット構造化監査ロガー | `import "go.corp/telemetry/logger"` |
| `sec-buffer-c` | C | 境界検証セキュアバッファ・メモリ管理 | `#include <enterprise/sec_buffer.h>` |
| `safe-ptr-cpp` | C++ | RAIIセキュアリソース管理・スマートポインタ | `#include <enterprise/safe_ptr.hpp>` |
| `auth-jwt-csharp` | C# | 全社標準OAuth2/JWT認証・RBACミドルウェア | `using Enterprise.Security.Authentication;` |
| `audit-logger-csharp` | C# | OpenTelemetry構造化監査ロガー | `using Enterprise.Diagnostics.Logging;` |


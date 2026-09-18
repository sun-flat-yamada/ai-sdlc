# [BUG] JWT認証の有効期限切れ時に500エラーが発生する

## 動作環境
- Node.js 20.11.0, Express 4.19
- @enterprise/jwt-auth-middleware 2.4.0

## 再現手順
1. 有効期限（exp）が切れたJWTトークンを Authorization ヘッダーに付与して GET /api/v1/users を叩く。
2. 401 Unauthorized ではなく 500 Internal Server Error が返却され、サーバーが例外クラッシュする。

## 期待される動作
失効したトークンに対しては安全に 401 Unauthorized が返却され、サーバーがクラッシュしないこと。

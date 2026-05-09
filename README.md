# BtoB Energy Management Backend

フロントエンド `step3-2_BtoB_frontend` に対応するバックエンドAPI

## 技術スタック

- **Framework**: FastAPI
- **Database**: SQLite (開発用)
- **ORM**: SQLAlchemy
- **認証**: JWT Bearer Token

## セットアップ

### 1. 仮想環境の作成

```bash
cd step3-2_BtoB_backend
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 2. 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 3. 初期データの投入

```bash
python init_db.py
```

### 4. サーバー起動

```bash
python run.py
```

または

```bash
uvicorn app.main:app --reload --port 8000
```

## API ドキュメント

サーバー起動後、以下のURLでAPIドキュメントを確認できます：

- Swagger UI: http://localhost:8000/api/v1/docs
- ReDoc: http://localhost:8000/api/v1/redoc

## テストアカウント

| アカウント | メール | パスワード | 権限 |
|-----------|--------|-----------|------|
| 管理者 | admin@example.com | admin123 | Admin |
| 一般ユーザー | user1@example.com | password123 | User |

## API エンドポイント一覧

### 認証
- `POST /api/v1/login/access-token` - ログイン
- `POST /api/v1/users/` - ユーザー登録

### ユーザー
- `GET /api/v1/users/me` - 現在のユーザー情報取得
- `PUT /api/v1/users/me` - ユーザー情報更新

### デバイス
- `GET /api/v1/devices/` - デバイス一覧
- `GET /api/v1/devices/{id}` - デバイス詳細
- `POST /api/v1/devices/` - デバイス作成
- `PUT /api/v1/devices/{id}` - デバイス更新
- `DELETE /api/v1/devices/{id}` - デバイス削除

### エネルギーレコード
- `GET /api/v1/energy-records/` - レコード一覧
- `GET /api/v1/energy-records/daily-summary` - 日次サマリー
- `POST /api/v1/energy-records/` - レコード作成
- `PUT /api/v1/energy-records/{id}` - レコード更新
- `DELETE /api/v1/energy-records/{id}` - レコード削除

### ポイント
- `GET /api/v1/mobile/points/balance` - ポイント残高
- `GET /api/v1/mobile/points/history` - ポイント履歴
- `POST /api/v1/mobile/redeem` - ポイント交換
- `GET /api/v1/admin/points/employees` - 従業員ポイント一覧

### リワード/インセンティブ
- `GET /api/v1/rewards/` - リワード一覧
- `GET /api/v1/incentives/rewards` - インセンティブ一覧
- `POST /api/v1/incentives/rewards` - リワード作成
- `PUT /api/v1/incentives/rewards/{id}` - リワード更新

### メトリクス
- `GET /api/v1/metrics/kpi` - KPI取得
- `GET /api/v1/metrics/monthly-usage` - 月次使用量
- `GET /api/v1/metrics/co2-trend` - CO2削減トレンド
- `GET /api/v1/metrics/yoy-usage` - 前年比較

### レポート
- `POST /api/v1/reports/generate/preview` - レポートプレビュー
- `POST /api/v1/reports/generate` - レポート生成
- `GET /api/v1/reports/generate/status/{id}` - 生成状況確認
- `GET /api/v1/reports/generate/download/{id}` - レポートダウンロード

## フロントエンドとの接続

フロントエンドの `.env.local` を以下のように設定：

```
NEXT_PUBLIC_API_BASE=http://localhost:8000/api/v1
```

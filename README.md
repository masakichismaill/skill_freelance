# スキルフリマ

スキルを売買できるマーケットプレイスアプリ。出品者がスキルを登録し、購入者が Stripe で決済・取引を完了するまでのフローをカバーします。

## 使用技術

| カテゴリ | 技術 |
|---|---|
| バックエンド | Python 3 / Django 4.2 |
| フロントエンド | Bootstrap 5（CDN） |
| データベース | SQLite（開発）|
| 決済 | Stripe Checkout |
| 画像処理 | Pillow |
| 静的ファイル配信（本番） | WhiteNoise |
| 環境変数管理 | django-environ |

## ローカル起動手順

```bash
# 1. リポジトリをクローン
git clone <repository-url>
cd skill_freelance

# 2. 仮想環境を作成・有効化
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 依存パッケージをインストール
pip install -r requirements.txt

# 4. 環境変数ファイルを作成
cp .env.example .env
# .env を開いて Stripe テストキーを入力

# 5. マイグレーション実行
python3 manage.py migrate

# 6. スーパーユーザー作成
python3 manage.py createsuperuser

# 7. 開発サーバー起動
python3 manage.py runserver
```

ブラウザで `http://127.0.0.1:8000/` を開く。

## 環境変数一覧（.env）

| 変数名 | 説明 | 例 |
|---|---|---|
| `STRIPE_SECRET_KEY` | Stripe シークレットキー（テスト用） | `sk_test_xxx` |
| `STRIPE_PUBLISHABLE_KEY` | Stripe 公開可能キー（テスト用） | `pk_test_xxx` |
| `DJANGO_SECRET_KEY` | Django シークレットキー（**本番のみ**） | 任意の長い文字列 |
| `ALLOWED_HOSTS` | 許可ホスト名（**本番のみ**・カンマ区切り） | `example.com,www.example.com` |

> テストキーは [Stripe ダッシュボード](https://dashboard.stripe.com/test/apikeys) から取得してください。

## 画面一覧

| URL | 機能 | 認証 |
|---|---|---|
| `/` | トップページ | 不要 |
| `/register/` | 会員登録 | 不要 |
| `/login/` | ログイン | 不要 |
| `/logout/` | ログアウト（POST） | 要 |
| `/mypage/` | マイページ（bio・登録日） | 要 |
| `/mypage/orders/` | 購入履歴一覧 | 要 |
| `/skills/` | スキル一覧（検索・絞り込み・ページネーション） | 不要 |
| `/skills/new/` | スキル出品 | 要 |
| `/skills/<pk>/` | スキル詳細 | 不要 |
| `/skills/<pk>/edit/` | スキル編集（出品者のみ） | 要 |
| `/skills/<pk>/delete/` | スキル削除確認（出品者のみ） | 要 |
| `/users/<pk>/` | 出品者プロフィール・レビュー一覧 | 不要 |
| `/orders/checkout/<skill_id>/` | Stripe Checkout セッション作成 | 要 |
| `/orders/success/` | 決済完了ページ | 要 |
| `/orders/<pk>/` | 取引詳細・メッセージ | 購入者/出品者 |
| `/orders/<pk>/complete/` | 取引完了（POST・出品者のみ） | 要 |
| `/orders/<pk>/review/` | レビュー投稿（購入者のみ） | 要 |
| `/admin/` | 管理画面 | スタッフのみ |

## 本番デプロイ

```bash
# 本番設定を使用
DJANGO_SETTINGS_MODULE=skill_freelance.settings_production

# 静的ファイルを収集
python3 manage.py collectstatic --noinput

# gunicorn で起動（例）
gunicorn skill_freelance.wsgi:application
```

# 営業インセンティブポイント交換システム

[![Django](https://img.shields.io/badge/Django-4.2.7-green.svg)](https://djangoproject.com/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3.0-purple.svg)](https://getbootstrap.com/)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org/)

営業マンに対してポイントを付与し、付与されたポイントでギフト商品と交換できるWebアプリケーション

## 🎯 システム概要

### 主要機能
- **ポイント付与・管理**: 管理者による月次ポイント付与（デジタルギフト6:企業商品4の比率）
- **商品交換**: デジタルギフトと企業オリジナル商品の交換
- **履歴管理**: ポイント付与・交換履歴の詳細管理
- **有効期限管理**: 付与から6ヶ月後の月末に自動失効
- **管理者機能**: ユーザー管理、商品管理、交換状況管理
- **ホワイトレーベル対応**: 企業ブランディングのカスタマイズ

### 利用者
- **営業マン**: ポイント確認・ギフト交換
- **管理者**: ポイント付与・ユーザー管理・商品管理

## 🛠️ 技術スタック

### Backend
- **Django 4.2.7**: Webフレームワーク
- **SQLite**: データベース（PostgreSQL移行可能）
- **Python 3.8+**: プログラミング言語

### Frontend
- **Django Templates**: テンプレートエンジン
- **Bootstrap 5.3.0**: UIフレームワーク
- **Abukumaデザインシステム**: ギフティー社デザインシステム準拠
- **Bootstrap Icons**: アイコンライブラリ

### セキュリティ
- Django標準認証システム
- CSRF対策
- XSS対策
- SQLインジェクション対策

## 📦 インストール・セットアップ

### 必要条件
- Python 3.8以上
- pip
- Git

### 1. リポジトリのクローン
```bash
git clone https://github.com/junozone1110/test-overseasalesincentive.git
cd test-overseasalesincentive
```

### 2. 仮想環境の作成・有効化
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 3. 依存関係のインストール
```bash
pip install -r requirements.txt
```

### 4. データベースの初期化
```bash
python manage.py migrate
```

### 5. 管理者ユーザーの作成
```bash
python manage.py createsuperuser
```

### 6. 開発サーバーの起動
```bash
python manage.py runserver
```

ブラウザで http://localhost:8000 にアクセス

## 🎨 ホワイトレーベル設定

環境変数で企業ブランディングをカスタマイズ可能：

```bash
# .env ファイル作成例
COMPANY_NAME=貴社名
SYSTEM_NAME=営業成果インセンティブシステム
SYSTEM_SHORT_NAME=インセンティブ
COMPANY_LOGO_URL=https://example.com/logo.png
COMPANY_COLOR_PRIMARY=#2c5282
COMPANY_COLOR_SECONDARY=#4a5568
COMPANY_URL=https://example.com
SUPPORT_EMAIL=support@example.com
COPYRIGHT_TEXT=© 2024 貴社名. All rights reserved.
```

詳細は `WHITE_LABEL_SETUP.md` を参照

## 📊 データベース設計

### 主要テーブル
- **Users**: ユーザー情報（カスタムユーザーモデル）
- **PointCategories**: ポイントカテゴリ（デジタルギフト/企業商品）
- **Points**: ポイント付与情報
- **Products**: 交換可能商品
- **PointTransactions**: ポイント取引履歴
- **ProductExchanges**: 商品交換履歴

## 🔧 管理機能

### Django Admin
- ユーザー管理
- ポイント付与
- 商品管理
- 交換申請管理
- 取引履歴確認

管理画面: http://localhost:8000/admin/

## 🎯 主要画面

### 営業マン向け
1. **ダッシュボード**: ポイント残高表示
2. **商品一覧**: 交換可能商品の閲覧
3. **商品詳細**: 商品情報と交換機能
4. **ポイント履歴**: 付与・交換履歴
5. **交換履歴**: 商品交換状況

### 管理者向け
1. **管理ダッシュボード**: システム全体の状況
2. **ポイント付与**: 個別・一括付与機能
3. **商品管理**: 商品の追加・編集
4. **交換管理**: 交換申請の承認・処理
5. **レポート**: 各種統計情報

## 🔒 セキュリティ機能

- **認証**: Django標準認証 + カスタムユーザーモデル
- **認可**: 管理者・一般ユーザー権限分離
- **CSRF対策**: 全フォームでCSRFトークン使用
- **XSS対策**: テンプレートの自動エスケープ
- **SQLインジェクション対策**: Django ORM使用

## 📈 運用・保守

### ログ
- Django標準ログ機能
- エラー・アクセスログ記録

### バックアップ
```bash
# データベースバックアップ
python manage.py dumpdata > backup.json

# リストア
python manage.py loaddata backup.json
```

### 定期メンテナンス
```bash
# 期限切れポイントの削除
python manage.py shell -c "
from points.models import Point
Point.objects.filter(expires_at__lt=timezone.now()).update(is_expired=True)
"
```

## 🚀 本番環境デプロイ

### 環境設定
```bash
# 本番環境用設定
DEBUG=False
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=your-domain.com
```

### 推奨構成
- **Web Server**: Nginx
- **WSGI Server**: Gunicorn
- **Database**: PostgreSQL
- **Static Files**: AWS S3 / CDN
- **Platform**: AWS EC2 / Docker

## 🧪 テスト

```bash
# テスト実行
python manage.py test

# カバレッジ確認
pip install coverage
coverage run --source='.' manage.py test
coverage report
```

## 📋 開発ロードマップ

### Phase 1: 基盤構築 ✅
- Django プロジェクト初期化
- 認証機能実装
- 基本的な管理画面

### Phase 2: コア機能実装 ✅
- ポイント付与機能
- 商品管理機能
- ポイント交換機能
- 履歴機能

### Phase 3: UI/UX改善 ✅
- Abukumaデザインシステム適用
- レスポンシブ対応
- ホワイトレーベル対応

### Phase 4: 今後の拡張予定
- [ ] CSV一括ポイント付与機能
- [ ] メール通知機能
- [ ] API提供（モバイルアプリ対応）
- [ ] 外部ギフトサービス連携
- [ ] 多言語対応

## 🤝 コントリビューション

1. このリポジトリをフォーク
2. フィーチャーブランチを作成 (`git checkout -b feature/AmazingFeature`)
3. 変更をコミット (`git commit -m 'Add some AmazingFeature'`)
4. ブランチにプッシュ (`git push origin feature/AmazingFeature`)
5. プルリクエストを作成

## 📄 ライセンス

このプロジェクトはMITライセンスの下で公開されています。詳細は `LICENSE` ファイルを参照してください。

## 📞 サポート

- **Issues**: GitHub Issues
- **Email**: zone+github@giftee.co
- **Documentation**: プロジェクト内の各種ドキュメント

## 🙏 謝辞

- [Django](https://djangoproject.com/) - 素晴らしいWebフレームワーク
- [Bootstrap](https://getbootstrap.com/) - 美しいUIコンポーネント
- [Abukuma Design System](https://github.com/giftee/design-system) - ギフティー社デザインシステム

---

**開発者**: zone (zone+github@giftee.co)  
**最終更新**: 2024年9月24日

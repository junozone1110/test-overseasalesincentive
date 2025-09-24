# 営業インセンティブポイント交換サービス 実装計画書

## 1. 要件概要

### 1.1 システム概要
営業マンに対してポイントを付与し、付与されたポイントでギフト商品と交換できるWebアプリケーション

### 1.2 利用者
- **営業マン（数百名）**: ポイント確認・ギフト交換
- **管理者**: ポイント付与・ユーザー管理・商品管理

### 1.3 主要機能
- ポイント付与・管理（カテゴリ別：デジタルギフト6:企業商品4）
- ギフト商品交換
- 有効期限管理（付与から6ヶ月後の月末）
- 履歴管理

## 2. 技術仕様

### 2.1 技術スタック
- **Backend**: Python + Django
- **Database**: SQLite
- **Frontend**: Django Templates + Bootstrap
- **Deploy**: AWS（EC2 + RDS移行可能な設計）

### 2.2 システム構成
```
[ユーザー] → [AWS ALB] → [EC2: Django App] → [SQLite DB]
                            ↓
                     [S3: Static Files]
```

## 3. データベース設計

### 3.1 主要テーブル

#### Users（ユーザー）
```sql
- id (PK)
- username (unique)
- password_hash
- email
- full_name
- is_admin (boolean)
- created_at
- updated_at
```

#### PointCategories（ポイントカテゴリ）
```sql
- id (PK)
- name (デジタルギフト/企業商品)
- ratio (60/40)
- created_at
```

#### Points（ポイント）
```sql
- id (PK)
- user_id (FK)
- category_id (FK)
- amount
- issued_at
- expires_at
- remaining_amount
- reason
```

#### Products（商品）
```sql
- id (PK)
- category_id (FK)
- name
- description
- required_points
- is_active
- created_at
- updated_at
```

#### PointTransactions（ポイント取引履歴）
```sql
- id (PK)
- user_id (FK)
- transaction_type (grant/use)
- amount
- reason
- product_id (FK, nullable)
- created_at
```

## 4. 画面設計概要

### 4.1 営業マン向け画面
1. **ログイン画面**
2. **ダッシュボード**
   - 保有ポイント表示（カテゴリ別）
   - 有効期限警告
   - 最近の取引履歴
3. **商品一覧・交換画面**
   - カテゴリ別商品表示
   - ポイント交換機能
4. **履歴確認画面**
   - ポイント付与履歴
   - 商品交換履歴

### 4.2 管理者向け画面
1. **管理者ログイン**
2. **ユーザー管理**
   - 一覧・検索・編集・新規登録
3. **ポイント付与**
   - 個別付与フォーム
   - 一括付与フォーム
4. **商品管理**
   - 商品登録・編集・削除
5. **レポート**
   - ユーザー別ポイント状況
   - 商品交換状況

## 5. 主要機能の実装詳細

### 5.1 ポイント付与ロジック
```python
def grant_points(user, total_points, reason):
    # カテゴリ別にポイント分割（6:4）
    digital_points = int(total_points * 0.6)
    corporate_points = total_points - digital_points
    
    # 有効期限計算（6ヶ月後の月末）
    expires_at = calculate_expiry_date(datetime.now())
    
    # ポイント付与
    Point.objects.create(
        user=user,
        category=digital_category,
        amount=digital_points,
        expires_at=expires_at,
        reason=reason
    )
```

### 5.2 ポイント消費ロジック（FIFO）
```python
def consume_points(user, category, required_points):
    # 有効期限が近い順で取得
    available_points = Point.objects.filter(
        user=user,
        category=category,
        remaining_amount__gt=0,
        expires_at__gte=timezone.now()
    ).order_by('expires_at')
    
    # ポイント消費処理（FIFO）
    remaining_required = required_points
    for point in available_points:
        if remaining_required <= 0:
            break
        # 消費処理...
```

### 5.3 有効期限計算
```python
def calculate_expiry_date(issued_date):
    # 6ヶ月後の月を計算
    expiry_month = issued_date.month + 6
    expiry_year = issued_date.year
    if expiry_month > 12:
        expiry_year += 1
        expiry_month -= 12
    
    # 月末日を取得
    last_day = calendar.monthrange(expiry_year, expiry_month)[1]
    return datetime(expiry_year, expiry_month, last_day, 23, 59, 59)
```

## 6. 開発フェーズ

### Phase 1: 基盤構築（2-3週間）
- Django プロジェクト初期化
- データベース設計・マイグレーション
- 認証機能実装
- 基本的な管理画面

### Phase 2: コア機能実装（3-4週間）
- ポイント付与機能
- 商品管理機能
- ポイント交換機能
- 履歴機能

### Phase 3: UI/UX改善（2週間）
- フロントエンド改善
- レスポンシブ対応
- バリデーション強化

### Phase 4: テスト・デプロイ（1-2週間）
- 単体テスト・結合テスト
- AWS環境構築
- 本番デプロイ

**総開発期間: 8-11週間**

## 7. 技術的考慮事項

### 7.1 セキュリティ
- Django標準の認証機能活用
- CSRF対策
- SQLインジェクション対策
- パスワードハッシュ化

### 7.2 パフォーマンス
- データベースインデックス設計
- クエリ最適化
- 静的ファイルのCDN配信

### 7.3 拡張性
- 将来のユーザー数増加に対応可能な設計
- SQLiteからPostgreSQLへの移行パス
- API化の準備（Django REST Framework導入可能）

## 8. 将来の拡張予定

### 8.1 短期拡張（Phase 5）
- CSV一括ポイント付与機能
- より詳細なレポート機能
- メール通知機能

### 8.2 中長期拡張
- API提供（モバイルアプリ対応）
- 外部ギフトサービス連携
- ポイント比率の動的設定
- 多言語対応

## 9. リスクと対策

### 9.1 技術的リスク
- **SQLiteの同時接続制限**: PostgreSQLへの移行準備
- **ポイント計算の整合性**: トランザクション処理の徹底

### 9.2 運用リスク
- **データバックアップ**: 定期バックアップの自動化
- **有効期限管理**: バッチ処理による定期的なクリーンアップ

## 10. 開発リソース見積もり

### 10.1 推奨チーム構成
- バックエンドエンジニア: 1名
- フロントエンドエンジニア: 1名
- プロジェクトマネージャー: 1名（兼任可）

### 10.2 工数見積もり
- 設計・実装: 200-250時間
- テスト: 50-70時間
- デプロイ・運用準備: 30-40時間

**総工数: 280-360時間**
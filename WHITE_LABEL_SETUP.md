# ホワイトレーベル設定ガイド

本システムは企業向けホワイトレーベル提供に対応しています。以下の環境変数を設定することで、各企業のブランディングに合わせてカスタマイズできます。

## 設定可能な項目

### 基本情報
- `COMPANY_NAME`: 企業名（例: "ABC商事株式会社"）
- `SYSTEM_NAME`: システム名（例: "営業成果インセンティブシステム"）
- `SYSTEM_SHORT_NAME`: ナビゲーション表示用の短縮名（例: "インセンティブ"）

### ブランディング
- `COMPANY_LOGO_URL`: 企業ロゴのURL（40px高さ推奨）
- `COMPANY_COLOR_PRIMARY`: メインカラー（例: "#2c5282"）
- `COMPANY_COLOR_SECONDARY`: サブカラー（例: "#4a5568"）

### 連絡先・リンク
- `COMPANY_URL`: 企業サイトURL
- `SUPPORT_EMAIL`: サポートメールアドレス
- `COPYRIGHT_TEXT`: コピーライト表記

## 設定例

```env
# 基本情報
COMPANY_NAME=ABC商事株式会社
SYSTEM_NAME=営業成果インセンティブシステム
SYSTEM_SHORT_NAME=インセンティブ

# ブランディング
COMPANY_LOGO_URL=https://example.com/logo.png
COMPANY_COLOR_PRIMARY=#2c5282
COMPANY_COLOR_SECONDARY=#4a5568

# 連絡先
COMPANY_URL=https://abc-trading.example.com
SUPPORT_EMAIL=support@abc-trading.example.com
COPYRIGHT_TEXT=© 2024 ABC商事株式会社. All rights reserved.
```

## 適用される箇所

### ヘッダー
- ナビゲーションバーに企業ロゴとシステム名を表示
- 企業カラーでブランディング

### フッター
- 企業名、システム名
- 企業サイトとサポートへのリンク
- コピーライト表記

### 全体デザイン
- ボタン、リンクなどのメインカラーを企業色に変更
- タイトルバーに企業名を表示

## デフォルト値

設定しない場合は以下のデフォルト値が使用されます：

```
COMPANY_NAME: "株式会社サンプル"
SYSTEM_NAME: "営業インセンティブシステム"
SYSTEM_SHORT_NAME: "インセンティブ"
COMPANY_COLOR_PRIMARY: "#0d6efd" (Bootstrap Blue)
COMPANY_COLOR_SECONDARY: "#6c757d" (Bootstrap Gray)
COMPANY_URL: "https://example.com"
SUPPORT_EMAIL: "support@example.com"
COPYRIGHT_TEXT: "© 2024 株式会社サンプル. All rights reserved."
```

## 実装詳細

- 設定は `incentive_system/settings.py` の `COMPANY_SETTINGS` で管理
- テンプレートでは `{{ COMPANY_SETTINGS.COMPANY_NAME }}` のように使用
- CSS変数を使用してカラーテーマを動的に適用

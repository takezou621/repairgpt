# RepairGPT 多言語対応 (Internationalization) 実装ガイド

## 概要

RepairGPTに日本語と英語の多言語対応を実装しました。ユーザーは言語選択により、UIとAPIレスポンスの両方で希望する言語を選択できます。

## 実装した機能

### 1. 国際化 (i18n) システム
- **場所**: `src/i18n/`
- **機能**: 翻訳キーベースの多言語システム
- **対応言語**: 英語 (en)、日本語 (ja)

### 2. フロントエンド多言語対応
- **場所**: `src/ui/repair_app.py`, `src/ui/language_selector.py`
- **機能**: 
  - サイドバーの言語切り替えウィジェット
  - 全UIテキストの動的翻訳
  - デバイス選択肢の多言語化
  - スキルレベルの多言語化

### 3. バックエンド多言語対応
- **場所**: `src/api/`
- **機能**:
  - FastAPI middleware での自動言語検出
  - APIレスポンスの多言語化
  - Accept-Language ヘッダーサポート
  - クエリパラメータでの言語指定

## 使用方法

### フロントエンド (Streamlit)

```python
from i18n import _

# 翻訳キーを使用
title = _("app.title")
button_text = _("ui.buttons.send")

# パラメータ付き翻訳
message = _("ui.messages.found_guides", count=5)
```

### バックエンド (FastAPI)

```python
from api import get_localized_response, get_localized_error

# 多言語レスポンス
return get_localized_response(
    request,
    "api.success.message",
    data=result
)

# 多言語エラー
raise get_localized_error(
    request,
    "api.errors.not_found",
    status_code=404
)
```

### API使用例

```bash
# 英語でのAPIリクエスト
curl -X GET "http://localhost:8000/devices" \
  -H "Accept-Language: en"

# 日本語でのAPIリクエスト
curl -X GET "http://localhost:8000/devices?lang=ja"
```

## ファイル構造

```
src/
├── i18n/
│   ├── __init__.py          # i18nシステムの核となるクラス
│   └── locales/
│       ├── en.json          # 英語翻訳
│       └── ja.json          # 日本語翻訳
├── ui/
│   ├── repair_app.py        # 多言語対応済みメインUI
│   └── language_selector.py # 言語選択コンポーネント
└── api/
    ├── __init__.py          # FastAPI i18n middleware
    └── routes.py            # 多言語対応APIルート
```

## 翻訳キー構造

翻訳ファイルはドット記法によるネストした構造を使用:

```json
{
  "app": {
    "title": "RepairGPT - AI Repair Assistant",
    "subtitle": "AI-Powered Electronic Device Repair Assistant"
  },
  "ui": {
    "buttons": {
      "send": "Send 🚀",
      "clear_chat": "Clear Chat 🗑️"
    },
    "labels": {
      "device_type": "Device Type"
    }
  }
}
```

## 新しい翻訳の追加

### 1. 翻訳キーの追加

`src/i18n/locales/en.json` と `src/i18n/locales/ja.json` に新しいキーを追加:

```json
{
  "new_feature": {
    "title": "New Feature",
    "description": "This is a new feature with {parameter}"
  }
}
```

### 2. コードでの使用

```python
from i18n import _

title = _("new_feature.title")
description = _("new_feature.description", parameter="example")
```

## 言語検出の仕組み

### フロントエンド
1. セッション状態から言語を取得
2. デフォルト言語: 英語 (en)
3. ユーザーが言語セレクターで変更可能

### バックエンド
1. クエリパラメータ `?lang=ja` を最優先
2. `Accept-Language` ヘッダーから検出
3. フォールバック: 英語 (en)

## テスト

### Streamlitアプリの起動
```bash
cd /Users/kawai/dev/repairgpt
streamlit run src/ui/repair_app.py
```

### FastAPI サーバーの起動
```bash
cd /Users/kawai/dev/repairgpt
uvicorn src.api.main:app --reload
```

## 拡張方法

### 新しい言語の追加

1. `src/i18n/locales/` に新しい言語ファイル追加 (例: `fr.json`)
2. `src/ui/language_selector.py` の言語辞書に追加
3. 必要に応じてフォント・レイアウト調整

### 新しい翻訳領域の追加

1. 翻訳JSONファイルに新しいセクション追加
2. コードで `_()` 関数を使用して翻訳キー参照
3. パラメータ化が必要な場合は `{variable}` 記法使用

## 注意事項

1. **翻訳キーの一貫性**: 英語と日本語で同じキー構造を保つ
2. **フォールバック**: 翻訳が見つからない場合は英語版、それも無い場合はキー自体を表示
3. **パフォーマンス**: 翻訳ファイルはアプリ起動時に一度だけ読み込み
4. **セキュリティ**: ユーザー入力の翻訳キーは検証が必要

## トラブルシューティング

### 翻訳が表示されない
- 翻訳ファイルのJSON構文をチェック
- キーの大文字小文字を確認
- `i18n.reload_translations()` で翻訳ファイルを再読み込み

### 言語が切り替わらない
- セッション状態がクリアされているかチェック
- ブラウザキャッシュをクリア
- コンソールでJavaScriptエラーをチェック

---

この多言語対応により、RepairGPTは日本語と英語のユーザーの両方に対応し、グローバルな利用が可能になりました。
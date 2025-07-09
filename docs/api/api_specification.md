# RepairGPT API仕様書

## 1. API概要

### 1.1 ベースURL
```
開発環境: http://localhost:8000
本番環境: https://api.repairgpt.com
```

### 1.2 認証
- **認証方式**: API Key認証
- **ヘッダー**: `Authorization: Bearer {api_key}`

### 1.3 共通レスポンス形式
```json
{
  "success": true,
  "data": {},
  "error": null,
  "timestamp": "2024-01-01T00:00:00Z"
}
```

## 2. エラーコード

| コード | 説明 | HTTPステータス |
|--------|------|----------------|
| 400 | 不正なリクエスト | 400 |
| 401 | 認証エラー | 401 |
| 403 | アクセス拒否 | 403 |
| 404 | リソースが見つからない | 404 |
| 429 | レート制限超過 | 429 |
| 500 | サーバー内部エラー | 500 |
| 503 | サービス利用不可 | 503 |

## 3. Chat API

### 3.1 チャット開始
```http
POST /api/v1/chat/start
```

**Request Body:**
```json
{
  "device_type": "nintendo_switch",
  "user_id": "user_123",
  "session_id": "session_456"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "session_id": "session_456",
    "welcome_message": "Nintendo Switchの修理についてお手伝いします。どのような問題でしょうか？",
    "suggested_questions": [
      "電源が入らない",
      "画面が映らない",
      "Joy-Conが動かない"
    ]
  }
}
```

### 3.2 メッセージ送信
```http
POST /api/v1/chat/message
```

**Request Body:**
```json
{
  "session_id": "session_456",
  "message": "電源が入らないのですが、どうしたらいいでしょうか？",
  "images": [
    {
      "filename": "switch_front.jpg",
      "data": "base64_encoded_image_data",
      "mime_type": "image/jpeg"
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "response": "電源の問題ですね。まず充電ケーブルを確認してください。",
    "repair_steps": [
      {
        "step": 1,
        "description": "充電ケーブルが正しく接続されているか確認",
        "warning": "作業前に完全に電源を切断してください",
        "image_url": "https://example.com/step1.jpg"
      }
    ],
    "tools_required": ["プラスドライバー"],
    "estimated_time": "15分",
    "difficulty": "beginner"
  }
}
```

### 3.3 チャット履歴取得
```http
GET /api/v1/chat/history/{session_id}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "session_id": "session_456",
    "messages": [
      {
        "id": "msg_001",
        "sender": "user",
        "content": "電源が入らない",
        "timestamp": "2024-01-01T10:00:00Z"
      },
      {
        "id": "msg_002",
        "sender": "bot",
        "content": "充電ケーブルを確認してください",
        "timestamp": "2024-01-01T10:00:05Z"
      }
    ]
  }
}
```

## 4. Device API

### 4.1 対応デバイス一覧
```http
GET /api/v1/devices
```

**Response:**
```json
{
  "success": true,
  "data": {
    "devices": [
      {
        "id": "nintendo_switch",
        "name": "Nintendo Switch",
        "category": "gaming_console",
        "supported_issues": ["power", "display", "controller"],
        "image_url": "https://example.com/switch.jpg"
      },
      {
        "id": "ps5",
        "name": "PlayStation 5",
        "category": "gaming_console",
        "supported_issues": ["power", "disc_drive", "overheating"],
        "image_url": "https://example.com/ps5.jpg"
      }
    ]
  }
}
```

### 4.2 デバイス詳細取得
```http
GET /api/v1/devices/{device_id}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "nintendo_switch",
    "name": "Nintendo Switch",
    "category": "gaming_console",
    "description": "Nintendo Switch本体の修理ガイド",
    "common_issues": [
      {
        "issue": "power",
        "description": "電源が入らない",
        "frequency": 0.3
      },
      {
        "issue": "joycon_drift",
        "description": "Joy-Conスティックのドリフト",
        "frequency": 0.4
      }
    ],
    "specifications": {
      "release_year": 2017,
      "manufacturer": "Nintendo",
      "model_variants": ["OLED", "Lite"]
    }
  }
}
```

## 5. Repair API

### 5.1 修理ガイド検索
```http
GET /api/v1/repairs/search
```

**Query Parameters:**
- `device`: デバイスID
- `issue`: 問題の種類
- `difficulty`: 難易度 (beginner/intermediate/advanced)
- `limit`: 取得件数 (default: 10)

**Response:**
```json
{
  "success": true,
  "data": {
    "repairs": [
      {
        "id": "repair_001",
        "title": "Nintendo Switch電源問題の修理",
        "device": "nintendo_switch",
        "issue": "power",
        "difficulty": "beginner",
        "estimated_time": "30分",
        "success_rate": 0.85,
        "tools_required": ["プラスドライバー", "マルチメーター"],
        "parts_required": ["充電ケーブル"]
      }
    ],
    "total": 1
  }
}
```

### 5.2 修理ガイド詳細
```http
GET /api/v1/repairs/{repair_id}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "repair_001",
    "title": "Nintendo Switch電源問題の修理",
    "device": "nintendo_switch",
    "issue": "power",
    "difficulty": "beginner",
    "estimated_time": "30分",
    "tools_required": ["プラスドライバー", "マルチメーター"],
    "parts_required": ["充電ケーブル"],
    "safety_warnings": [
      "作業前に完全に電源を切断してください",
      "静電気除去を行ってください"
    ],
    "steps": [
      {
        "step": 1,
        "title": "充電ケーブル確認",
        "description": "充電ケーブルが正しく接続されているか確認してください",
        "image_url": "https://example.com/step1.jpg",
        "warning": "ケーブルを無理に引っ張らないでください"
      },
      {
        "step": 2,
        "title": "電源ボタン長押し",
        "description": "電源ボタンを12秒間長押しして完全シャットダウンを行います",
        "image_url": "https://example.com/step2.jpg"
      }
    ],
    "success_rate": 0.85,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
}
```

## 6. Image API

### 6.1 画像アップロード
```http
POST /api/v1/images/upload
```

**Request Body (multipart/form-data):**
```
file: binary_image_data
session_id: session_456
description: "Nintendo Switch front view"
```

**Response:**
```json
{
  "success": true,
  "data": {
    "image_id": "img_001",
    "url": "https://example.com/images/img_001.jpg",
    "analysis": {
      "device_detected": "nintendo_switch",
      "confidence": 0.95,
      "issues_detected": [
        {
          "issue": "screen_damage",
          "confidence": 0.8,
          "location": "upper_left"
        }
      ]
    }
  }
}
```

### 6.2 画像解析
```http
POST /api/v1/images/analyze
```

**Request Body:**
```json
{
  "image_id": "img_001",
  "device_type": "nintendo_switch",
  "analysis_type": "damage_detection"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "analysis_id": "analysis_001",
    "device_detected": "nintendo_switch",
    "confidence": 0.95,
    "issues": [
      {
        "type": "screen_crack",
        "severity": "moderate",
        "location": {
          "x": 150,
          "y": 200,
          "width": 100,
          "height": 50
        },
        "repair_recommendation": "画面交換が必要です"
      }
    ],
    "processed_at": "2024-01-01T10:00:00Z"
  }
}
```

## 7. User API

### 7.1 ユーザー登録
```http
POST /api/v1/users/register
```

**Request Body:**
```json
{
  "username": "user123",
  "email": "user@example.com",
  "password": "secure_password"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "user_id": "user_123",
    "username": "user123",
    "email": "user@example.com",
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

### 7.2 ユーザー修理履歴
```http
GET /api/v1/users/{user_id}/repair-history
```

**Response:**
```json
{
  "success": true,
  "data": {
    "repairs": [
      {
        "session_id": "session_456",
        "device": "nintendo_switch",
        "issue": "power",
        "status": "completed",
        "success": true,
        "started_at": "2024-01-01T10:00:00Z",
        "completed_at": "2024-01-01T10:30:00Z"
      }
    ],
    "total": 1
  }
}
```

## 8. Admin API

### 8.1 システム統計
```http
GET /api/v1/admin/stats
```

**Response:**
```json
{
  "success": true,
  "data": {
    "total_sessions": 1000,
    "total_users": 500,
    "success_rate": 0.75,
    "popular_devices": [
      {
        "device": "nintendo_switch",
        "count": 400
      },
      {
        "device": "ps5",
        "count": 300
      }
    ],
    "common_issues": [
      {
        "issue": "power",
        "count": 200
      },
      {
        "issue": "display",
        "count": 150
      }
    ]
  }
}
```

## 9. レート制限

### 9.1 制限値
- **Chat API**: 60回/分
- **Image API**: 30回/分
- **その他API**: 100回/分

### 9.2 ヘッダー
```http
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 59
X-RateLimit-Reset: 1640995200
```

## 10. WebSocket API

### 10.1 リアルタイムチャット
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/chat/{session_id}');

// メッセージ送信
ws.send(JSON.stringify({
  type: 'message',
  content: 'こんにちは'
}));

// メッセージ受信
ws.onmessage = function(event) {
  const data = JSON.parse(event.data);
  console.log('Received:', data);
};
```

## 11. SDK例

### 11.1 Python SDK
```python
from repairgpt_sdk import RepairGPTClient

client = RepairGPTClient(api_key="your_api_key")

# チャット開始
session = client.chat.start(device_type="nintendo_switch")

# メッセージ送信
response = client.chat.send_message(
    session_id=session.session_id,
    message="電源が入らない"
)

print(response.response)
```

### 11.2 JavaScript SDK
```javascript
import { RepairGPTClient } from 'repairgpt-sdk';

const client = new RepairGPTClient('your_api_key');

// チャット開始
const session = await client.chat.start({
  deviceType: 'nintendo_switch'
});

// メッセージ送信
const response = await client.chat.sendMessage({
  sessionId: session.sessionId,
  message: '電源が入らない'
});

console.log(response.response);
```

## 12. OpenAPI 仕様

### 12.1 Swagger UI
- **開発環境**: http://localhost:8000/docs
- **本番環境**: https://api.repairgpt.com/docs

### 12.2 OpenAPI JSON
```bash
# OpenAPI 仕様をダウンロード
curl -o openapi.json http://localhost:8000/openapi.json
```

### 12.3 型定義生成
```bash
# TypeScript型定義生成
npx openapi-typescript openapi.json --output src/types/api.ts

# Python型定義生成
openapi-python-client generate --path openapi.json
```

## 13. 認証・認可

### 13.1 JWT トークン認証
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "user123",
  "password": "secure_password"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "token_type": "bearer",
    "expires_in": 3600
  }
}
```

### 13.2 トークン更新
```http
POST /api/v1/auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### 13.3 権限レベル
- **guest**: 基本的な診断機能のみ
- **user**: 全ての修理機能、履歴保存
- **premium**: 高度な診断、優先サポート
- **admin**: システム管理機能

## 14. バージョニング

### 14.1 API バージョン
- **現在**: v1
- **サポート**: v1のみ
- **非推奨**: なし

### 14.2 バージョン指定
```http
# URL パス
GET /api/v1/devices

# ヘッダー
GET /api/devices
Accept: application/vnd.repairgpt.v1+json
```

### 14.3 変更ログ
#### v1.0.0 (2024-01-01)
- 初回リリース
- 基本的なチャット機能
- 画像アップロード機能

#### v1.1.0 (予定)
- WebSocket対応
- 修理履歴検索機能
- 詳細な画像解析

## 15. トラブルシューティング

### 15.1 よくあるエラー

#### 認証エラー (401)
```json
{
  "success": false,
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Invalid or expired token"
  }
}
```

**解決方法:**
- トークンの有効期限を確認
- 新しいトークンを取得

#### レート制限エラー (429)
```json
{
  "success": false,
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded. Try again in 60 seconds."
  }
}
```

**解決方法:**
- 指定された時間待機
- リクエスト頻度を調整

#### 画像サイズエラー (400)
```json
{
  "success": false,
  "error": {
    "code": "IMAGE_TOO_LARGE",
    "message": "Image size exceeds 5MB limit"
  }
}
```

**解決方法:**
- 画像を圧縮
- 対応形式を確認

### 15.2 デバッグ情報
```bash
# API状態確認
curl -X GET http://localhost:8000/health

# 詳細なエラー情報
curl -X GET http://localhost:8000/health/detailed
```

## 16. サポート・連絡先

### 16.1 技術サポート
- **Email**: api-support@repairgpt.com
- **Discord**: #api-support
- **GitHub Issues**: https://github.com/takezou621/repairgpt/issues

### 16.2 API変更通知
- **Webhook**: システム変更の通知
- **メール**: 重要な変更のお知らせ
- **Change Log**: https://api.repairgpt.com/changelog

---

**最終更新日**: 2024-01-09  
**バージョン**: 1.2.0  
**メンテナー**: RepairGPT開発チーム
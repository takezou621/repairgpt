# RepairGPT コーディング規約

## 1. 言語別コーディング規約

### 1.1 Python（主要開発言語）

#### 1.1.1 基本原則
- **PEP 8**: Python Enhancement Proposal 8に準拠
- **PEP 257**: Docstring規約に準拠
- **型ヒント**: Python 3.9+ の型ヒントを必須使用

#### 1.1.2 コード構造
```python
"""モジュールの説明をここに記載する.

このモジュールは修理ガイドの管理を行う。
"""

import os
import sys
from typing import Dict, List, Optional, Union
from datetime import datetime

from sqlalchemy import create_engine
from pydantic import BaseModel, Field

# 定数
DEFAULT_TIMEOUT = 30
MAX_RETRY_COUNT = 3
SUPPORTED_DEVICES = ["nintendo_switch", "ps5", "iphone"]


class RepairGuide(BaseModel):
    """修理ガイドのデータモデル."""
    
    id: str = Field(..., description="修理ガイドID")
    title: str = Field(..., min_length=1, max_length=200)
    device_id: str = Field(..., description="対象デバイスID")
    difficulty: str = Field("medium", regex="^(beginner|intermediate|advanced)$")
    estimated_time: Optional[int] = Field(None, ge=1, description="見積もり時間(分)")
    
    class Config:
        """Pydanticの設定."""
        
        schema_extra = {
            "example": {
                "id": "repair_001",
                "title": "Nintendo Switch電源問題修理",
                "device_id": "nintendo_switch",
                "difficulty": "beginner",
                "estimated_time": 30
            }
        }


def get_repair_guide(guide_id: str) -> Optional[RepairGuide]:
    """修理ガイドを取得する.
    
    Args:
        guide_id: 修理ガイドID
        
    Returns:
        修理ガイドオブジェクト、見つからない場合はNone
        
    Raises:
        DatabaseError: データベース接続エラー
        ValidationError: 入力値が不正な場合
    """
    if not guide_id:
        raise ValueError("guide_id is required")
    
    try:
        # データベース処理
        result = _fetch_from_database(guide_id)
        return RepairGuide(**result) if result else None
    except DatabaseError as e:
        logger.error(f"Database error in get_repair_guide: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_repair_guide: {e}")
        raise DatabaseError("Failed to retrieve repair guide")


def _fetch_from_database(guide_id: str) -> Optional[Dict]:
    """データベースから修理ガイドを取得する（プライベート関数）."""
    # プライベート関数の実装
    pass
```

#### 1.1.3 命名規則
```python
# 変数・関数：snake_case
user_name = "john_doe"
device_count = 5

def get_user_profile(user_id: str) -> UserProfile:
    pass

# クラス：PascalCase
class RepairBotClient:
    pass

# 定数：UPPER_CASE
API_BASE_URL = "https://api.repairgpt.com"
DEFAULT_TIMEOUT = 30

# プライベート関数・変数：アンダースコア始まり
def _validate_input(data: str) -> bool:
    pass

# 魔法数字の排除
MAX_RETRY_COUNT = 3  # 良い例
for i in range(MAX_RETRY_COUNT):
    pass

# 悪い例
for i in range(3):  # 3の意味が不明
    pass
```

#### 1.1.4 例外処理
```python
class RepairGPTError(Exception):
    """RepairGPT関連のベース例外."""
    pass

class DeviceNotSupportedError(RepairGPTError):
    """サポートされていないデバイスの例外."""
    pass

class APIConnectionError(RepairGPTError):
    """API接続エラー."""
    pass

def call_external_api(endpoint: str) -> Dict:
    """外部APIを呼び出す."""
    try:
        response = requests.get(endpoint, timeout=DEFAULT_TIMEOUT)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        raise APIConnectionError(f"Timeout calling {endpoint}")
    except requests.exceptions.ConnectionError:
        raise APIConnectionError(f"Connection error to {endpoint}")
    except requests.exceptions.HTTPError as e:
        raise APIConnectionError(f"HTTP error: {e}")
    except ValueError as e:
        raise APIConnectionError(f"Invalid JSON response: {e}")
```

#### 1.1.5 ログ記録
```python
import logging

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def process_repair_request(device_id: str, issue: str) -> str:
    """修理リクエストを処理する."""
    logger.info(f"Processing repair request: device={device_id}, issue={issue}")
    
    try:
        result = _generate_repair_guidance(device_id, issue)
        logger.info(f"Successfully generated repair guidance for {device_id}")
        return result
    except Exception as e:
        logger.error(f"Failed to process repair request: {e}")
        raise
```

### 1.2 JavaScript/TypeScript（フロントエンド）

#### 1.2.1 基本原則
- **ESLint**: Airbnb設定を基本とする
- **TypeScript**: 型安全性を重視
- **関数型プログラミング**: 副作用を最小化

#### 1.2.2 命名規則
```typescript
// 変数・関数：camelCase
const userName = 'john_doe';
const deviceCount = 5;

const getUserProfile = async (userId: string): Promise<UserProfile> => {
  // 実装
};

// クラス・インターフェース：PascalCase
interface RepairGuide {
  id: string;
  title: string;
  deviceId: string;
  difficulty: 'beginner' | 'intermediate' | 'advanced';
}

class RepairBotClient {
  // 実装
}

// 定数：UPPER_CASE
const API_BASE_URL = 'https://api.repairgpt.com';
const DEFAULT_TIMEOUT = 30000;

// 型定義
type DeviceType = 'nintendo_switch' | 'ps5' | 'iphone';
type RepairStatus = 'pending' | 'in_progress' | 'completed' | 'failed';
```

## 2. ファイル・ディレクトリ構成

### 2.1 Python プロジェクト構成
```
src/
├── chatbot/
│   ├── __init__.py
│   ├── repair_bot.py
│   └── conversation_manager.py
├── clients/
│   ├── __init__.py
│   ├── ifixit_client.py
│   └── llm_client.py
├── models/
│   ├── __init__.py
│   ├── database.py
│   ├── repair_guide.py
│   └── user.py
├── api/
│   ├── __init__.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── chat.py
│   │   └── repair.py
│   └── middleware/
├── utils/
│   ├── __init__.py
│   ├── logger.py
│   └── validators.py
└── config/
    ├── __init__.py
    └── settings.py
```

### 2.2 設定ファイル
```python
# config/settings.py
import os
from typing import Optional
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """アプリケーション設定."""
    
    # データベース設定
    database_url: str = Field(..., env="DATABASE_URL")
    database_echo: bool = Field(False, env="DATABASE_ECHO")
    
    # API設定
    openai_api_key: Optional[str] = Field(None, env="OPENAI_API_KEY")
    claude_api_key: Optional[str] = Field(None, env="CLAUDE_API_KEY")
    
    # アプリケーション設定
    debug: bool = Field(False, env="DEBUG")
    log_level: str = Field("INFO", env="LOG_LEVEL")
    
    class Config:
        """Pydanticの設定."""
        
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
```

## 3. データベース操作

### 3.1 SQLAlchemy モデル
```python
# models/repair_guide.py
from sqlalchemy import Column, String, Integer, Text, DECIMAL, Boolean, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.sql import func
from database import Base


class RepairGuide(Base):
    """修理ガイドモデル."""
    
    __tablename__ = "repair_guides"
    
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    title = Column(String(200), nullable=False)
    device_id = Column(String(50), nullable=False)
    issue_id = Column(String(50), nullable=False)
    difficulty = Column(String(20), nullable=False, default="medium")
    estimated_time = Column(Integer)  # minutes
    success_rate = Column(DECIMAL(3, 2), default=0.0)
    tools_required = Column(ARRAY(Text))
    parts_required = Column(ARRAY(Text))
    safety_warnings = Column(ARRAY(Text))
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    def __repr__(self) -> str:
        return f"<RepairGuide(id={self.id}, title={self.title})>"
```

### 3.2 データアクセス層
```python
# models/repositories/repair_guide_repository.py
from typing import List, Optional
from sqlalchemy.orm import Session
from models.repair_guide import RepairGuide


class RepairGuideRepository:
    """修理ガイドリポジトリ."""
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def get_by_id(self, guide_id: str) -> Optional[RepairGuide]:
        """IDで修理ガイドを取得."""
        return self.db.query(RepairGuide).filter(RepairGuide.id == guide_id).first()
    
    def get_by_device_and_issue(self, device_id: str, issue_id: str) -> List[RepairGuide]:
        """デバイスと問題で修理ガイドを検索."""
        return (
            self.db.query(RepairGuide)
            .filter(
                RepairGuide.device_id == device_id,
                RepairGuide.issue_id == issue_id,
                RepairGuide.is_active == True
            )
            .order_by(RepairGuide.success_rate.desc())
            .all()
        )
    
    def create(self, guide_data: dict) -> RepairGuide:
        """新しい修理ガイドを作成."""
        guide = RepairGuide(**guide_data)
        self.db.add(guide)
        self.db.commit()
        self.db.refresh(guide)
        return guide
```

## 4. テストコード規約

### 4.1 テストファイル構成
```python
# tests/unit/test_repair_bot.py
import pytest
from unittest.mock import Mock, patch
from src.chatbot.repair_bot import RepairBot


class TestRepairBot:
    """RepairBotのテストクラス."""
    
    def setup_method(self):
        """各テストメソッドの前に実行される."""
        self.repair_bot = RepairBot()
    
    def test_ask_basic_question(self):
        """基本的な質問のテスト."""
        # Given
        question = "Nintendo Switchの電源が入らない"
        
        # When
        response = self.repair_bot.ask(question)
        
        # Then
        assert response is not None
        assert "充電" in response
    
    @patch('src.chatbot.repair_bot.openai_client')
    def test_ask_with_api_error(self, mock_openai):
        """API エラー時のテスト."""
        # Given
        mock_openai.chat.completions.create.side_effect = Exception("API Error")
        question = "テスト質問"
        
        # When & Then
        with pytest.raises(APIConnectionError):
            self.repair_bot.ask(question)
    
    @pytest.mark.parametrize("device,issue,expected", [
        ("nintendo_switch", "power", "充電"),
        ("ps5", "overheating", "冷却"),
        ("iphone", "screen", "画面"),
    ])
    def test_device_specific_responses(self, device, issue, expected):
        """デバイス固有の応答テスト."""
        # Given
        question = f"{device}の{issue}問題"
        
        # When
        response = self.repair_bot.ask(question)
        
        # Then
        assert expected in response
```

### 4.2 テストデータ管理
```python
# tests/fixtures/repair_data.py
import pytest
from models.repair_guide import RepairGuide


@pytest.fixture
def sample_repair_guide():
    """サンプル修理ガイド."""
    return {
        "id": "repair_001",
        "title": "Nintendo Switch電源問題修理",
        "device_id": "nintendo_switch",
        "issue_id": "power",
        "difficulty": "beginner",
        "estimated_time": 30,
        "tools_required": ["プラスドライバー"],
        "parts_required": ["充電ケーブル"],
        "safety_warnings": ["電源を切断してください"]
    }

@pytest.fixture
def mock_database(monkeypatch):
    """モックデータベース."""
    mock_db = Mock()
    monkeypatch.setattr("src.models.database.get_db", lambda: mock_db)
    return mock_db
```

## 5. API開発規約

### 5.1 FastAPI エンドポイント
```python
# api/routes/repair.py
from fastapi import APIRouter, HTTPException, Depends
from typing import List
from models.repair_guide import RepairGuide
from api.dependencies import get_current_user
from api.schemas.repair import RepairGuideResponse, RepairGuideCreate


router = APIRouter(prefix="/api/v1/repair", tags=["repair"])


@router.get("/guides", response_model=List[RepairGuideResponse])
async def get_repair_guides(
    device_id: str,
    issue_id: str,
    limit: int = 10,
    current_user: User = Depends(get_current_user)
):
    """修理ガイドを取得する."""
    try:
        guides = repair_service.get_guides(
            device_id=device_id,
            issue_id=issue_id,
            limit=limit
        )
        return guides
    except ServiceError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/guides", response_model=RepairGuideResponse)
async def create_repair_guide(
    guide_data: RepairGuideCreate,
    current_user: User = Depends(get_current_user)
):
    """新しい修理ガイドを作成する."""
    try:
        guide = repair_service.create_guide(guide_data.dict())
        return guide
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
```

### 5.2 スキーマ定義
```python
# api/schemas/repair.py
from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime


class RepairGuideBase(BaseModel):
    """修理ガイドの基本スキーマ."""
    
    title: str = Field(..., min_length=1, max_length=200)
    device_id: str = Field(..., description="デバイスID")
    issue_id: str = Field(..., description="問題ID")
    difficulty: str = Field("medium", regex="^(beginner|intermediate|advanced)$")
    estimated_time: Optional[int] = Field(None, ge=1, le=480)
    
    @validator('device_id')
    def validate_device_id(cls, v):
        """デバイスIDの検証."""
        if v not in SUPPORTED_DEVICES:
            raise ValueError(f"Unsupported device: {v}")
        return v


class RepairGuideCreate(RepairGuideBase):
    """修理ガイド作成スキーマ."""
    
    tools_required: List[str] = Field(default_factory=list)
    parts_required: List[str] = Field(default_factory=list)
    safety_warnings: List[str] = Field(default_factory=list)
    description: Optional[str] = None


class RepairGuideResponse(RepairGuideBase):
    """修理ガイド応答スキーマ."""
    
    id: str
    success_rate: float
    created_at: datetime
    updated_at: datetime
    
    class Config:
        """Pydanticの設定."""
        
        orm_mode = True
```

## 6. セキュリティ規約

### 6.1 入力検証
```python
from html import escape
from typing import Any

def sanitize_user_input(user_input: str) -> str:
    """ユーザー入力をサニタイズする."""
    if not isinstance(user_input, str):
        raise TypeError("Input must be a string")
    
    # 長さ制限
    if len(user_input) > 1000:
        raise ValueError("Input too long")
    
    # HTMLエスケープ
    sanitized = escape(user_input)
    
    # 危険なパターンの除去
    dangerous_patterns = ["<script", "javascript:", "onload="]
    for pattern in dangerous_patterns:
        if pattern in sanitized.lower():
            raise ValueError("Dangerous content detected")
    
    return sanitized
```

### 6.2 認証・認可
```python
# api/dependencies.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from config.settings import settings


security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """現在のユーザーを取得する."""
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
    
    user = get_user_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user
```

## 7. パフォーマンス最適化

### 7.1 データベースクエリ最適化
```python
# 悪い例：N+1クエリ
def get_repair_guides_bad():
    guides = db.query(RepairGuide).all()
    for guide in guides:
        # 各ガイドに対して個別クエリが発生
        steps = db.query(RepairStep).filter(RepairStep.guide_id == guide.id).all()

# 良い例：JOINを使用
def get_repair_guides_good():
    return (
        db.query(RepairGuide)
        .options(joinedload(RepairGuide.steps))
        .all()
    )
```

### 7.2 キャッシュ利用
```python
from functools import lru_cache
from redis import Redis

redis_client = Redis(host='localhost', port=6379, db=0)

@lru_cache(maxsize=128)
def get_device_info(device_id: str) -> dict:
    """デバイス情報を取得（メモリキャッシュ）."""
    return _fetch_device_from_db(device_id)

def get_repair_guide_cached(guide_id: str) -> Optional[dict]:
    """修理ガイドを取得（Redisキャッシュ）."""
    cache_key = f"repair_guide:{guide_id}"
    
    # キャッシュから取得
    cached_guide = redis_client.get(cache_key)
    if cached_guide:
        return json.loads(cached_guide)
    
    # データベースから取得
    guide = _fetch_guide_from_db(guide_id)
    if guide:
        # キャッシュに保存（1時間）
        redis_client.setex(cache_key, 3600, json.dumps(guide))
    
    return guide
```

## 8. コード品質チェック

### 8.1 自動フォーマット
```bash
# Black（コードフォーマッター）
black src/ tests/

# isort（import文の整理）
isort src/ tests/

# flake8（構文チェック）
flake8 src/ tests/
```

### 8.2 型チェック
```bash
# mypy（型チェック）
mypy src/

# 設定ファイル（mypy.ini）
[mypy]
python_version = 3.9
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True
```

### 8.3 セキュリティチェック
```bash
# bandit（セキュリティチェック）
bandit -r src/

# safety（依存関係の脆弱性チェック）
safety check
```

## 9. 継続的改善

### 9.1 コードレビューチェックリスト
- [ ] 命名規則に従っているか
- [ ] 型ヒントが適切に付与されているか
- [ ] 例外処理が適切に実装されているか
- [ ] テストが十分に書かれているか
- [ ] セキュリティ上の問題がないか
- [ ] パフォーマンスに問題がないか
- [ ] ドキュメントが更新されているか

### 9.2 定期的なコード品質向上
- **月次**: 静的解析ツールの結果確認
- **四半期**: 技術的負債の棚卸し
- **半年**: コーディング規約の見直し
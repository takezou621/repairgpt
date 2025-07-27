# 🔧 RepairGPT

"Empowering everyone to repair anything"  
AI × 分解 × 循環社会 = RepairGPT

## 🧠 What is RepairGPT?

RepairGPT is a **fully functional** open-source AI-powered electronic device repair assistant. It provides expert guidance for diagnosing and fixing consumer electronics including game consoles, smartphones, laptops, and other devices using advanced LLMs and multimodal capabilities.

**✅ Currently Implemented Features:**
- 🤖 **AI Repair Assistant** - Enhanced chatbot with built-in knowledge base
- 📚 **Offline Repair Database** - 4 comprehensive repair guides (Nintendo Switch, iPhone, Laptop, PlayStation 5)
- 🌐 **iFixit Integration** - Online repair guide search and access
- 🖥️ **Web Interface** - Complete Streamlit-based UI
- 📷 **Image Upload Support** - Visual repair assistance
- 🛡️ **Safety-First Approach** - Detailed warnings and professional tips
- 🎯 **Context-Aware Guidance** - Device-specific and skill-level appropriate advice

## 🚀 Quick Start Guide

### Step 1: Prerequisites

Ensure you have Python 3.9+ installed:
```bash
python3 --version
```

### Step 2: Clone the Repository

```bash
git clone https://github.com/takezou621/repairgpt.git
cd repairgpt
```

### Step 3: Install Dependencies

```bash
pip3 install -r requirements.txt
```

**Required packages will be installed:**
- streamlit (Web UI)
- requests (API communication)
- pillow (Image processing)
- And other essential dependencies

### Step 4: Launch RepairGPT

**Option A: Using the launcher script (Recommended)**
```bash
python3 run_app.py
```

**Option B: Direct Streamlit execution**
```bash
streamlit run src/ui/repair_app.py
```

### Step 5: Access the Application

1. **Open your web browser**
2. **Navigate to:** `http://localhost:8501`
3. **Start using RepairGPT!**

## 📱 How to Use RepairGPT

### 1. Device Setup
- Select your device type from the sidebar
- Enter device model (optional)
- Describe your issue
- Set your skill level

### 2. Get Repair Guidance
- **Chat Interface**: Ask questions about your repair issue
- **Online Guides**: Search iFixit database for device-specific guides
- **Offline Guides**: Access built-in comprehensive repair guides
- **Image Upload**: Upload photos for visual assistance

### 3. Follow Safety Guidelines
- Review safety warnings before starting
- Gather recommended tools and parts
- Follow step-by-step instructions
- Test your repair thoroughly

## 🎯 Available Repair Guides

**Built-in Offline Guides:**
1. **Nintendo Switch Joy-Con Drift** - Complete 7-step repair process
2. **iPhone Screen Replacement** - Professional-grade repair guide
3. **Laptop Boot Issues** - Comprehensive troubleshooting steps
4. **PlayStation 5 Overheating** - Thermal management and cleaning

**Online Integration:**
- Full iFixit database access
- Real-time guide search
- Community-contributed content

## ⚙️ Configuration (Optional)

### Enable AI Features
For enhanced AI capabilities, add API keys to your environment:

```bash
# For OpenAI GPT models
export OPENAI_API_KEY="your-api-key-here"

# For Anthropic Claude models  
export ANTHROPIC_API_KEY="your-api-key-here"

# For Hugging Face models (optional)
export HUGGINGFACE_API_KEY="your-api-key-here"
```

**Note:** RepairGPT works fully without API keys using the built-in knowledge base.

## 🛠️ Troubleshooting

### Common Issues

**Port already in use:**
```bash
streamlit run src/ui/repair_app.py --server.port=8502
```

**Module import errors:**
```bash
pip3 install --upgrade -r requirements.txt
```

**Permission issues on macOS/Linux:**
```bash
chmod +x run_app.py
```

### Getting Help

1. Check the troubleshooting section above
2. Review the built-in debug information (enable in sidebar)
3. Open an issue on GitHub with detailed error information

## 🏗️ Project Structure

```
repairgpt/
├── 🚀 run_app.py              # Application launcher
├── 📦 requirements.txt        # Dependencies
├── 📂 src/                    # Main implementation
│   ├── chat/                  # AI chatbot system
│   ├── clients/               # iFixit API integration
│   ├── data/                  # Offline repair database
│   ├── prompts/               # Repair prompt templates
│   ├── schemas/               # Data schemas
│   └── ui/                    # Streamlit web interface
├── 📂 docs/                   # Comprehensive documentation
└── 📂 .github/workflows/      # Smart automation system
```

## 🧪 Testing

Verify your installation:
```bash
python3 -c "
import sys
sys.path.insert(0, 'src')
from data.offline_repair_database import OfflineRepairDatabase
print('✅ RepairGPT installation successful!')
print(f'Available guides: {len(OfflineRepairDatabase().guides)}')
"
```

## 📊 MVP Release Status

**Current Status**: 🟢 MVP Ready (100/100 score)  
**Documentation**: 📄 [MVP Release Status Report](docs/MVP_RELEASE_STATUS.md)

RepairGPT has achieved MVP readiness with:
- ✅ Complete core functionality and UI
- ✅ Comprehensive documentation structure  
- ✅ Smart automation system
- ✅ Multi-language support (i18n)
- ✅ All setup and configuration files ready

## 🔄 Updates and Maintenance

RepairGPT includes a smart automation system that:
- Automatically processes new repair guides
- Updates the knowledge base
- Manages issue tracking and resolution
- Maintains MVP documentation and status

The system runs on scheduled intervals and maintains the project automatically.

## 🛠️ Development & Code Quality

RepairGPT utilizes **Lefthook** for automated code quality management and CI/CD optimization.

### Quick Development Setup

```bash
# Install development dependencies
pip install -r requirements.txt

# Install Lefthook (Git hooks manager)
brew install lefthook          # macOS
# or: curl -1sLf 'https://dl.cloudsmith.io/public/evilmartians/lefthook/setup.deb.sh' | sudo -E bash && sudo apt install lefthook

# Enable automated code quality hooks
lefthook install
```

### Automated Quality Checks

**Pre-commit hooks** (automatic):
- 🎨 **Black formatting** (88-character line limit)
- 📦 **Import sorting** with isort
- 🔍 **flake8 linting** (PEP8 compliance)

**Pre-push hooks**:
- 🧪 **Unit tests** execution
- ✅ **Integration tests** validation

### Development Workflow

```bash
# Normal development - hooks run automatically
git add .
git commit -m "feat: add new repair feature"  # Auto-formatting applied
git push                                      # Tests run automatically

# Skip hooks if needed (emergencies only)
LEFTHOOK=0 git commit -m "emergency fix"
```

**Benefits**:
- ✅ 95% reduction in CI/CD failures
- ✅ Consistent code formatting across team
- ✅ Automatic PEP8 compliance
- ✅ Early bug detection

📚 **Full Documentation**: [Lefthook Setup Guide](docs/development/lefthook-guide.md)

## 🔧 Test Auto-Fix System

RepairGPTには、GitHub Actionsでテストが失敗した際に自動的に修復を試みるシステムが実装されています。

### 機能概要

- 🔍 **自動検出**: テスト失敗を自動的に検出
- 🛠️ **パターン分析**: 一般的なエラーパターンを識別
- 🔧 **自動修復**: 可能な場合は自動的に修正を適用
- 🔄 **PR作成**: 修正内容を含むPRを自動作成

### 修復可能なエラーパターン

1. **Import エラー**
   - モジュールのインポート漏れ
   - 相対/絶対インポートの問題

2. **Type エラー**
   - NoneType チェックの欠落
   - 型の不一致

3. **Mock エラー**
   - Mock オブジェクトの設定ミス
   - MagicMock への変換

4. **Fixture エラー**
   - pytest fixture の未定義
   - fixture のスコープ問題

5. **非同期エラー**
   - asyncio マーカーの欠落
   - イベントループの競合

### 使用方法

テスト自動修復は以下のタイミングで自動的に実行されます：

1. **自動トリガー**: Test Automation ワークフローが失敗した時
2. **手動トリガー**: workflow_dispatch で任意のワークフローIDを指定

```yaml
# 手動実行例
workflow_dispatch:
  workflow_run_id: "1234567890"
```

### 安全性

- 修正は必ずPRとして作成され、レビュー可能
- 元のコードは保持され、変更は追跡可能
- 複雑な修正は行わず、単純で安全な修正のみ実施

## 🚀 Claude Code エージェント活用ベストプラクティス

RepairGPTの開発では、Claude Codeの専門エージェント機能を活用して効率的な開発を実現しています。

### 利用可能なエージェント

1. **`kiro-task-organizer`** - プロジェクトドキュメントを分析し、タスクを適切に分割
2. **`task-executor-pr-creator`** - タスクの実装、テスト作成、PR作成を自動化
3. **`code-quality-inspector`** - コード品質の詳細分析と改善提案
4. **`qa-engineer-tester`** - 包括的な品質保証テストとバグ修正

### カスタムコマンド

効率的な開発のために以下のカスタムコマンドを用意しています：

```bash
# タスクの計画と分割
/organize-tasks "修理ガイドのマルチモーダル対応を実装"

# タスクの実装とPR作成
/implement-task TASK-001

# コード品質チェック
/check-quality src/services/image_analysis.py

# 包括的なQAテスト
/qa-test 修理ガイド生成API

# フル開発ワークフロー（全エージェント連携）
/full-workflow "AI診断機能の精度向上"
```

### 推奨開発ワークフロー

#### 1. 新機能開発
```
1. /organize-tasks で機能をタスクに分割
2. /implement-task で各タスクを実装
3. /check-quality でコード品質を確認
4. /qa-test で統合テストを実行
```

#### 2. バグ修正
```
1. /qa-test でバグを特定・再現
2. /implement-task で修正を実装
3. /check-quality で修正コードの品質確認
```

#### 3. リファクタリング
```
1. /check-quality で改善点を特定
2. /organize-tasks でリファクタリング計画
3. /implement-task で段階的に実装
4. /qa-test でリグレッションテスト
```

### ベストプラクティス

1. **段階的実行**
   - 大きな機能は必ず`/organize-tasks`で分割してから実装
   - 1つのタスクは1コミットで完了できるサイズに

2. **品質優先**
   - 実装後は必ず`/check-quality`を実行
   - 発見された問題は即座に修正

3. **テスト駆動**
   - `/implement-task`実行時は必ずテストを含める
   - カバレッジ80%以上を維持

4. **継続的検証**
   - 定期的に`/qa-test`で全体の品質を確認
   - パフォーマンスとセキュリティを常に監視

### 実践例

```bash
# 例: iFixit API統合の強化
/organize-tasks "iFixit API統合を強化してキャッシュ機能を追加"
# → タスクリストが生成される

/implement-task TASK-001  # Redisキャッシュ基盤の実装
/check-quality src/clients/ifixit_client.py
/implement-task TASK-002  # キャッシュ戦略の実装
/qa-test iFixit API統合  # 全体の品質確認
```

詳細は[CLAUDE.md](CLAUDE.md)のエージェント活用ガイドを参照してください。

## 🤝 Contributing

Interested in building the future of self-repair AI?  
Feel free to fork, open issues, or contact us via GitHub Discussions!

## 📄 License

MIT License


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

## 🤝 Contributing

Interested in building the future of self-repair AI?  
Feel free to fork, open issues, or contact us via GitHub Discussions!

## 📄 License

MIT License


# RepairGPT Technology Stack

## Core Technologies

### Backend
- **Python 3.9+**: Primary development language
- **FastAPI 0.100+**: REST API framework with async support
- **SQLAlchemy 2.0+**: Database ORM with async capabilities
- **Alembic 1.11+**: Database migrations
- **Pydantic 2.0+**: Data validation and serialization
- **Redis 4.6+**: Caching and session management

### Frontend
- **Streamlit 1.25+**: Web UI framework
- **Responsive Design**: Mobile-friendly interface

### AI/ML Stack
- **OpenAI API**: GPT-4 for repair guidance and image analysis
- **Anthropic Claude**: Advanced reasoning for complex diagnostics
- **Langchain**: Prompt management and LLM orchestration
- **Pillow/OpenCV**: Image processing

### Database
- **SQLite**: Development environment
- **PostgreSQL 14+**: Production environment

### Development Tools
- **Lefthook**: Git hooks for code quality
- **Black**: Code formatting (120 char line limit)
- **flake8**: Linting with PEP8 compliance
- **isort**: Import sorting
- **pytest**: Testing framework with coverage
- **mypy**: Type checking

## Common Commands

### Development Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Install development hooks
lefthook install

# Run application
python run_app.py
# or
streamlit run src/ui/repair_app.py
```

### Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test categories
pytest -m unit
pytest -m integration
pytest -m automation
```

### Code Quality
```bash
# Format code (automatic via hooks)
black src/ tests/ --line-length=120
isort src/ tests/ --profile black

# Lint code
flake8 src/ tests/ --max-line-length=120

# Type checking
mypy src/
```

### Database
```bash
# Initialize database
python scripts/init_db.py

# Run migrations
alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "description"
```

### Docker
```bash
# Development environment
docker-compose -f docker-compose.dev.yml up

# Production environment
docker-compose up

# Build specific service
docker-compose build api
```

## Environment Configuration

### Required Environment Variables
- `REPAIRGPT_OPENAI_API_KEY`: OpenAI API key (sk-...)
- `REPAIRGPT_CLAUDE_API_KEY`: Claude API key (sk-ant-...)
- `REPAIRGPT_SECRET_KEY`: JWT secret key (32+ chars)
- `REPAIRGPT_DATABASE_URL`: Database connection string

### Optional Configuration
- `REPAIRGPT_ENVIRONMENT`: development/staging/production
- `REPAIRGPT_DEBUG`: Enable debug mode
- `REPAIRGPT_LOG_LEVEL`: Logging level
- `REPAIRGPT_IFIXIT_API_KEY`: iFixit API integration
# RepairGPT Project Structure

## Directory Organization

### Source Code (`src/`)
```
src/
├── api/                    # FastAPI backend
│   ├── main.py            # Application entry point
│   ├── models.py          # Pydantic models
│   └── routes/            # API route modules
├── auth/                  # Authentication & JWT
├── chat/                  # LLM chatbot system
│   ├── llm_chatbot.py     # Main chatbot logic
│   ├── prompt_templates.py # Prompt management
│   └── streaming_chat.py   # Real-time chat
├── clients/               # External API clients
│   └── ifixit_client.py   # iFixit integration
├── config/                # Configuration management
│   ├── settings.py        # Full settings with validation
│   └── settings_simple.py # Simplified settings
├── data/                  # Data access layer
│   └── offline_repair_database.py
├── database/              # Database models & CRUD
│   ├── database.py        # DB connection
│   ├── models.py          # SQLAlchemy models
│   └── crud.py            # Database operations
├── features/              # Feature modules
├── i18n/                  # Internationalization
│   └── locales/           # Translation files
├── prompts/               # AI prompt templates
├── schemas/               # Data schemas & validation
├── services/              # Business logic services
│   ├── image_analysis.py  # Image processing
│   └── repair_guide_service.py
├── ui/                    # Streamlit frontend
│   ├── repair_app.py      # Main UI application
│   ├── language_selector.py
│   └── responsive_design.py
└── utils/                 # Utility functions
    ├── logger.py          # Logging configuration
    └── security.py        # Security utilities
```

### Tests (`tests/`)
```
tests/
├── automation/            # Automation system tests
├── fixtures/              # Test fixtures & data
├── integration/           # Integration tests
│   └── test_api/         # API endpoint tests
├── unit/                  # Unit tests
│   ├── test_auth/        # Authentication tests
│   ├── test_chat/        # Chatbot tests
│   └── test_data/        # Data layer tests
├── conftest.py           # Pytest configuration
└── requirements-test.txt  # Test dependencies
```

### Documentation (`docs/`)
```
docs/
├── api/                   # API documentation
├── architecture/          # System architecture
├── deployment/            # Deployment guides
├── development/           # Development guidelines
│   ├── coding_standards.md
│   ├── lefthook-guide.md
│   └── testing_strategy.md
├── setup/                 # Setup instructions
└── specs/                 # Technical specifications
```

## Naming Conventions

### Python Files & Modules
- **snake_case**: All Python files, functions, variables
- **PascalCase**: Classes and Pydantic models
- **UPPER_CASE**: Constants and environment variables
- **Private functions**: Prefix with underscore `_function_name`

### API Routes
- **REST conventions**: `/api/v1/resource`
- **Kebab-case**: Multi-word endpoints `/repair-guides`
- **Plural nouns**: Collection endpoints `/devices`, `/guides`

### Database
- **snake_case**: Table names, column names
- **Plural tables**: `repair_guides`, `user_sessions`
- **Foreign keys**: `device_id`, `user_id`

## File Organization Patterns

### Feature-Based Structure
Each major feature has its own module with:
- Models (Pydantic schemas)
- Services (business logic)
- Routes (API endpoints)
- Tests (unit & integration)

### Layered Architecture
1. **Presentation Layer**: `ui/` (Streamlit), `api/routes/` (FastAPI)
2. **Business Logic**: `services/`, `features/`
3. **Data Access**: `database/`, `clients/`
4. **Infrastructure**: `config/`, `utils/`

## Import Conventions

### Absolute Imports
```python
from src.config.settings import settings
from src.database.models import RepairGuide
from src.services.repair_guide_service import RepairGuideService
```

### Relative Imports (within same package)
```python
from .models import RepairGuide
from ..config.settings import settings
```

### Import Grouping (isort configuration)
1. Standard library imports
2. Third-party imports
3. Local application imports

## Configuration Management

### Environment-Based Settings
- **Development**: SQLite, debug mode, verbose logging
- **Staging**: PostgreSQL, reduced logging
- **Production**: PostgreSQL, security headers, rate limiting

### Settings Files
- `settings.py`: Full configuration with Pydantic validation
- `settings_simple.py`: Lightweight configuration
- `.env.example`: Environment variable template

## Security Patterns

### Input Validation
- All user inputs validated with Pydantic models
- Sanitization functions in `utils/security.py`
- File upload validation for images

### Authentication
- JWT tokens for API authentication
- Role-based access control
- Session management with Redis

### API Security
- Rate limiting per IP
- CORS configuration
- Security headers in production
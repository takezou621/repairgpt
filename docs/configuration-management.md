# Configuration Management with Pydantic Settings

## Overview

RepairGPT uses Pydantic Settings for comprehensive configuration management, providing type-safe, validated settings with environment-specific configurations.

## Implementation Status

✅ **Fully Implemented** - Issue #59 completed

## Features

### 1. Environment-Based Configuration

The system supports multiple environments:
- **Development**: Debug enabled, SQLite database, relaxed security
- **Staging**: Testing environment with production-like settings
- **Production**: Strict security, PostgreSQL required, validated settings
- **Testing**: In-memory database, disabled caching

### 2. Settings Structure

Located in `src/config/settings.py`:

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Environment Configuration
    environment: Environment
    debug: bool
    log_level: LogLevel
    
    # Security Configuration
    secret_key: str
    allowed_hosts: List[str]
    cors_origins: List[str]
    
    # API Keys
    openai_api_key: Optional[str]
    claude_api_key: Optional[str]
    ifixit_api_key: Optional[str]
    
    # Database Configuration
    database_url: str
    database_pool_size: int
    
    # ... and more
```

### 3. Environment Variables

All settings can be configured via environment variables with the `REPAIRGPT_` prefix:

```bash
REPAIRGPT_ENVIRONMENT=production
REPAIRGPT_SECRET_KEY=your-secret-key-min-32-chars
REPAIRGPT_DATABASE_URL=postgresql://user:pass@host:5432/db
REPAIRGPT_OPENAI_API_KEY=sk-your-api-key
```

### 4. Validation Features

#### API Key Validation
- OpenAI keys must start with `sk-`
- Claude keys must start with `sk-ant-`
- Format validation prevents invalid keys

#### Production Safeguards
- Secret key required (32+ characters)
- No wildcard hosts allowed
- No localhost CORS origins
- SQLite database blocked
- Debug mode disabled

#### Security Headers
```python
{
    "Strict-Transport-Security": "max-age=31536000",
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Content-Security-Policy": "default-src 'self'..."
}
```

### 5. Configuration Access

#### Import Settings
```python
from src.config import settings

# Access settings
api_key = settings.openai_api_key
is_prod = settings.is_production()
cors_config = settings.get_cors_config()
```

#### Dependency Injection
```python
from src.config.settings import get_settings

def my_endpoint(settings: Settings = Depends(get_settings)):
    return {"environment": settings.environment}
```

### 6. File Structure

```
src/config/
├── __init__.py          # Package initialization
└── settings.py          # Main settings class

.env.example             # Environment template
```

## Usage Examples

### 1. Basic Configuration

```python
# Access current settings
from src.config import settings

if settings.is_development():
    print(f"Running in development mode on port {settings.api_port}")

# Get API configuration
api_keys = settings.get_api_keys()
```

### 2. Environment-Specific Logic

```python
# Automatic environment detection
if settings.environment == Environment.PRODUCTION:
    # Production-only features
    enable_monitoring()
    
# Use utility methods
if settings.is_testing():
    # Test-specific behavior
    use_mock_services()
```

### 3. Validation in Action

```python
# These will raise validation errors:
# - In production with missing secret key
# - With invalid API key formats
# - With SQLite in production
# - With localhost CORS in production
```

## Security Best Practices

1. **Never commit secrets** - Use environment variables
2. **Rotate keys regularly** - Update API keys periodically
3. **Use strong secret keys** - 32+ random characters
4. **Enable HTTPS** - Required for production
5. **Configure CORS properly** - Restrict to actual domains
6. **Monitor configuration** - Log validation errors

## Production Checklist

Before deploying to production:

- [ ] Set `REPAIRGPT_ENVIRONMENT=production`
- [ ] Configure secure `REPAIRGPT_SECRET_KEY`
- [ ] Set proper `REPAIRGPT_ALLOWED_HOSTS`
- [ ] Configure production `REPAIRGPT_DATABASE_URL`
- [ ] Add valid API keys for required services
- [ ] Review CORS origins
- [ ] Disable debug mode
- [ ] Enable security headers
- [ ] Configure rate limiting

## Troubleshooting

### Common Issues

1. **"Secret key must be set in production"**
   - Set `REPAIRGPT_SECRET_KEY` environment variable
   - Ensure it's at least 32 characters

2. **"Invalid OpenAI API key format"**
   - OpenAI keys should start with `sk-`
   - Check for typos or extra spaces

3. **"SQLite not recommended for production"**
   - Use PostgreSQL for production
   - Update `REPAIRGPT_DATABASE_URL`

4. **"Wildcard hosts not allowed in production"**
   - Replace `*` with actual domain names
   - Set `REPAIRGPT_ALLOWED_HOSTS=yourdomain.com`

## Related Files

- `/src/config/settings.py` - Main settings implementation
- `/.env.example` - Environment variable template
- `/src/api/main.py` - Settings usage in API
- `/docs/configuration-management.md` - This documentation

## References

- [Pydantic Settings Documentation](https://docs.pydantic.dev/latest/usage/pydantic_settings/)
- [12-Factor App Config](https://12factor.net/config)
- [OWASP Configuration Guide](https://owasp.org/www-project-secure-headers/)
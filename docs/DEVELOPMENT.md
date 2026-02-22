# Development Guide

## Setup Development Environment

1. **Clone and setup:**
   ```bash
   git clone https://github.com/yourusername/ctfd-scraper.git
   cd ctfd-scraper
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -e ".[dev]"
   ```

2. **Install dependencies:**
   ```bash
   pip install -e ".[dev]"
   ```

## Project Structure

```
ctfd-scraper/
├── src/
│   └── ctfd_scraper/
│       ├── __init__.py
│       ├── cli.py            # CLI & main entry point
│       ├── config.py         # Configuration constants
│       ├── logger.py         # Logging utilities
│       ├── api_client.py     # CTFd API client
│       ├── challenges.py     # Challenge backup
│       ├── teams.py          # Team backup
│       ├── users.py          # User backup
│       └── scoreboard.py     # Scoreboard backup
├── tests/
│   ├── __init__.py
│   └── test_*.py            # Test files
├── docs/
│   ├── USAGE.md             # User guide
│   ├── API.md               # API documentation
│   └── DEVELOPMENT.md       # This file
├── pyproject.toml           # Project configuration
├── README.md                # Project overview
└── LICENSE                  # MIT License
```

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/ctfd_scraper --cov-report=html

# Run specific test file
pytest tests/test_api_client.py

# Run with verbose output
pytest -v
```

## Code Style

We use Black for code formatting:

```bash
# Format all code
black src/ tests/

# Check formatting without changes
black --check src/ tests/
```

Lint with flake8:

```bash
flake8 src/ tests/
```

Type checking with mypy:

```bash
mypy src/
```

## Adding New Features

1. **Create a new module** in `src/ctfd_scraper/`
2. **Add tests** in `tests/test_<module>.py`
3. **Update documentation** in `docs/`
4. **Add log messages** using the unified logger
5. **Update README.md** if needed

### Example: Adding a new backup type

```python
# src/ctfd_scraper/new_feature.py
from .logger import log

def backup_new_feature(client, backup_dir):
    """Backup new feature data."""
    log('new_feature', '*', "Starting backup...")
    
    try:
        # Implementation
        log('new_feature', '+', "Backup completed")
    except Exception as e:
        log('new_feature', '-', f"Error: {e}")
```

## Testing Guidelines

1. **Write tests for new features**
2. **Use mocking for API calls**
3. **Test error cases**
4. **Maintain >80% coverage**

Example test:

```python
# tests/test_new_feature.py
import pytest
from unittest.mock import Mock
from src.ctfd_scraper.new_feature import backup_new_feature

def test_backup_new_feature():
    client = Mock()
    backup_dir = "/tmp/test"
    
    # Test implementation
    backup_new_feature(client, backup_dir)
    
    # Assertions
    assert something
```

## Logging Standards

Always use the unified logger:

```python
from .logger import log

# Success
log('module', '+', "Operation successful")

# Error
log('module', '-', "Critical error occurred")

# Warning
log('module', '!', "Non-critical issue")

# Info
log('module', '*', "Status update")
```

## Performance Optimization

1. **Use ThreadPoolExecutor** for I/O-bound operations
2. **Adjust MAX_WORKERS** in config.py
3. **Use streaming downloads** for large files
4. **Batch API requests** when possible

## Release Process

1. Update version in `pyproject.toml`
2. Update CHANGELOG.md
3. Run all tests
4. Build package: `python -m build`
5. Tag release: `git tag v1.0.0`
6. Push: `git push --tags`

## Troubleshooting

### Import Errors

If you see `ModuleNotFoundError`:
```bash
pip install -e .
```

### Test Failures

Check that you're in the project root and have activated the venv.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## Code Review Checklist

- [ ] Tests pass
- [ ] Code is formatted (black)
- [ ] No linting errors (flake8)
- [ ] Documentation updated
- [ ] Logging follows standards
- [ ] No hardcoded credentials

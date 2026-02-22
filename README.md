<div align="center">

# CTFd Scraper

**High-performance backup tool for CTFd competitions with parallel processing**

[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Fast, reliable, and comprehensive backup solution for CTFd platforms with multi-threaded downloads and intelligent logging.

[Installation](#quickstart) • [Documentation](docs/USAGE.md) • [Contributing](#contributing)

</div>

---

## Quickstart

### Installation

```bash
# From PyPI (recommended)
pip install ctfd-scraper

# From source
git clone https://github.com/yourusername/ctfd-scraper.git
cd ctfd-scraper
pip install -e .
```

### Basic Usage

```bash
# Backup everything
ctfdscraper -u https://ctf.example.com -s your-session-cookie

# Challenges only
ctfdscraper -u https://ctf.example.com -s cookie --only-chal

# Custom output directory
ctfdscraper -u https://ctf.example.com -s cookie -o ./backups
```

### Getting Your Session Cookie

1. Open browser DevTools (F12)
2. Navigate to **Application → Cookies**
3. Copy the `session` cookie value

### CLI Options

```bash
ctfdscraper -u <URL> -s <SESSION> [OPTIONS]

Required:
  -u, --url           CTFd instance URL
  -s, --session       Session cookie value

Optional:
  -n, --name          Custom CTF name
  -o, --output        Output directory (default: .)
  
Backup Control:
  --only-chal         Backup challenges only
  --no-chal           Skip challenges
  --no-team           Skip teams
  --no-user           Skip users
  --no-scoreboard     Skip scoreboard

Performance:
  --max-workers-chal  Challenge concurrency (1-50, default: 10)
  --max-workers-team  Team/user concurrency (1-50, default: 20)
  --max-workers-file  File downloads per challenge (1-20, default: 5)
  --api-timeout       API timeout in seconds (default: 15)
  --file-timeout      File download timeout (default: 60)
```

### Output Structure

```
CTF_2024_backup/
├── Challenges/
│   ├── README.md              # Challenge overview by category
│   ├── Web/
│   │   └── SQL_Injection/
│   │       ├── description.md
│   │       └── source.zip
│   └── Crypto/
│       └── RSA_Challenge/
│           └── description.md
├── Teams/
│   └── TeamName_123/
│       └── team_info.json     # Members, solves, awards
├── Users/
│   └── Username_456/
│       └── user_info.json     # Team, solves
└── Scoreboard/
    ├── full_scoreboard.json   # Team rankings
    └── all_members_scoreboard.json  # Individual rankings
```

### Programmatic Usage

```python
from ctfd_scraper.cli import run_backup

config = {
    'url': 'https://ctf.example.com',
    'session': 'your-session-cookie',
    'backup_challenges': True,
    'backup_teams': True,
    'backup_users': False,  # Skip users
    'max_workers_challenges': 15,
}

run_backup(config)
```

---

## Architecture

### Core Components

```
ctfd-scraper/
├── src/ctfd_scraper/
│   ├── cli.py            # CLI & main entry point
│   ├── api_client.py     # CTFd REST API client with session pooling
│   ├── challenges.py     # Parallel challenge backup (10 workers × 5 files)
│   ├── teams.py          # Team backup with member details
│   ├── users.py          # User profile backup
│   ├── scoreboard.py     # Rankings backup (team + individual)
│   ├── logger.py         # Color-coded tagged logging system
│   └── config.py         # Performance constants
├── tests/                # Pytest test suite
└── docs/                 # User guides and API documentation
```

### Key Features

**🚀 High Performance**
- ThreadPoolExecutor-based parallelism
- Connection pooling with session reuse
- Streaming downloads for large files
- Configurable concurrency levels

**📊 Comprehensive Backup**
- Challenges with descriptions and files
- Teams with members and solve records
- Users with team affiliation
- Complete scoreboard rankings
- Auto-detects CTF name from HTML title

**🎨 Intelligent Logging**
- Color-coded output (`[+]` success, `[-]` error, `[!]` warning, `[*]` info)
- Tagged by module (`[chal]`, `[team]`, `[api]`, etc.)
- Progress tracking for large operations

**⚙️ Flexible Configuration**
- CLI-first design (no config files needed)
- Selective backup with exclusion flags
- Performance tuning via command-line args
- Timeout controls for unstable networks

### Performance

Benchmark: 40 challenges, 120 files, 100Mbps network

| Mode | Concurrency | Time | Notes |
|------|-------------|------|-------|
| Sequential | 1 worker | ~8 min | Single-threaded |
| Default | 10×5 workers | ~2 min | Recommended |
| High-speed | 20×10 workers | ~1 min | Fast networks |

### Technology Stack

- **Python 3.9+**: Modern async-ready codebase
- **Requests**: HTTP client with session pooling
- **BeautifulSoup4**: HTML parsing for CTF name detection
- **ThreadPoolExecutor**: Concurrent I/O operations
- **Pytest**: Test framework with coverage reporting

---

## License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2024 CTFd Scraper Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction...
```

---

## Contributing

We welcome contributions! Please follow these guidelines:

### Getting Started

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```

3. **Set up development environment**
   ```bash
   pip install -e ".[dev]"
   ```

4. **Make your changes**
   - Follow [PEP 8](https://peps.python.org/pep-0008/) style guide
   - Add tests for new features
   - Update documentation as needed

5. **Run quality checks**
   ```bash
   # Format code
   black ctfd_scraper/ tests/
   
   # Lint
   flake8 ctfd_scraper/ tests/
   
   # Type check
   mypy ctfd_scraper/
   
   # Run tests
   pytest --cov=ctfd_scraper
   ```

6. **Commit and push**
   ```bash
   git commit -m "feat: add amazing feature"
   git push origin feature/amazing-feature
   ```

7. **Open a Pull Request**

### Contribution Guidelines

- **Code Quality**: Maintain >80% test coverage
- **Documentation**: Update docs for user-facing changes
- **Commit Messages**: Use [Conventional Commits](https://www.conventionalcommits.org/)
- **Issues First**: For major changes, open an issue for discussion

### Development Commands

```bash
# Run tests with coverage
pytest --cov=ctfd_scraper --cov-report=html

# Format code
black ctfd_scraper/ tests/

# Lint
flake8 ctfd_scraper/ tests/

# Type check
mypy ctfd_scraper/

# Build package
python -m build
```

### Reporting Issues

- Use the [issue tracker](https://github.com/yourusername/ctfd-scraper/issues)
- Include Python version, OS, and CTFd version
- Provide minimal reproduction steps
- Check for existing issues first

---

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=yourusername/ctfd-scraper&type=Date)](https://star-history.com/#yourusername/ctfd-scraper&Date)

---

<div align="center">

**[Documentation](docs/USAGE.md)** • **[API Reference](docs/API.md)** • **[Development Guide](docs/DEVELOPMENT.md)**

Made with ❤️ for the CTF community

</div>

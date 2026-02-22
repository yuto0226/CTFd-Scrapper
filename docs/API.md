# API Documentation

## CTFdClient

Main client for interacting with CTFd API.

### Initialization

```python
from ctfd_scraper.api_client import CTFdClient

client = CTFdClient()
```

### Methods

#### `get_ctf_name()`

Retrieves CTF name from website title.

**Returns:** `str` - CTF name or "ctf" if not found

**Example:**
```python
name = client.get_ctf_name()
print(f"Backing up: {name}")
```

#### `fetch_api(endpoint, debug=False)`

Make a GET request to the CTFd API.

**Parameters:**
- `endpoint` (str): API endpoint path (e.g., "/api/v1/teams")
- `debug` (bool): Enable debug logging

**Returns:** `dict | None` - API response data or None on error

**Example:**
```python
teams = client.fetch_api("/api/v1/teams")
```

#### `fetch_all_pages(endpoint)`

Fetch all paginated results from an endpoint.

**Parameters:**
- `endpoint` (str): API endpoint path

**Returns:** `list` - Combined results from all pages

**Example:**
```python
all_users = client.fetch_all_pages("/api/v1/users")
```

## Challenge Functions

### `backup_challenges(client, backup_dir)`

Backup all challenges with parallel processing.

**Parameters:**
- `client` (CTFdClient): Initialized API client
- `backup_dir` (str): Base backup directory path

**Returns:** `list` - List of successfully backed up challenges

### `download_file(client, f_url, f_name, save_path)`

Download a single file with progress tracking.

**Parameters:**
- `client` (CTFdClient): Initialized API client
- `f_url` (str): File URL
- `f_name` (str): File name
- `save_path` (str): Directory to save file

**Returns:** `bool` - Success status

## Team/User Functions

### `backup_teams(client, backup_dir)`

Backup all team information.

**Parameters:**
- `client` (CTFdClient): Initialized API client
- `backup_dir` (str): Base backup directory path

### `backup_users(client, backup_dir)`

Backup all user information.

**Parameters:**
- `client` (CTFdClient): Initialized API client
- `backup_dir` (str): Base backup directory path

## Scoreboard Functions

### `backup_scoreboard(client, backup_dir)`

Backup complete scoreboard data.

**Parameters:**
- `client` (CTFdClient): Initialized API client
- `backup_dir` (str): Base backup directory path

## Logging

### `log(tag, level, message)`

Unified logging function with color coding.

**Parameters:**
- `tag` (str): Category tag (team, user, chal, file, scoreboard, main)
- `level` (str): Log level (+, -, !, *)
- `message` (str): Log message

**Example:**
```python
from ctfd_scraper.logger import log

log('main', '*', "Starting backup...")
log('chal', '+', "Challenge downloaded successfully")
log('team', '!', "Team has no solves, skipping")
log('api', '-', "Connection failed")
```

## Configuration

All configuration options are in `src/ctfd_scraper/config.py`:

```python
# CTFd instance
URL = "https://ctf.example.com"
SESSION_COOKIE = "your-session-cookie"

# Performance
MAX_WORKERS_CHALLENGES = 10
MAX_WORKERS_TEAMS = 20
MAX_WORKERS_FILES = 5

# Timeouts
API_TIMEOUT = 15
FILE_TIMEOUT = 60
```

## Data Structures

### Challenge Info

```python
{
    'name': str,
    'category': str,
    'value': int,
    'solves': int,
    'author': str
}
```

### Team Info

```python
{
    'id': int,
    'name': str,
    'rank': int,
    'score': int,
    'members': [
        {
            'name': str,
            'id': int,
            'score': int
        }
    ],
    'solves': [...],
    'awards': [...]
}
```

### User Info

```python
{
    'id': int,
    'name': str,
    'rank': int,
    'score': int,
    'team_id': int,
    'team_name': str,
    'solves': [...],
    'awards': [...]
}
```

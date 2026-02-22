"""Configuration module for CTFd Scraper."""

import os

# CTFd instance configuration
URL = os.getenv("CTFD_URL", "https://ctf.bitskrieg.in")
SESSION_COOKIE = os.getenv("CTFD_SESSION", "5cc1cb22-c036-49a7-9476-87defb7a353e.BtWhYP_t_40nUV0btrgR5t36cD8")

# Backup configuration
BACKUP_DIR = "./backup"
MAX_WORKERS_CHALLENGES = 10  # Concurrent challenges
MAX_WORKERS_TEAMS = 20       # Concurrent teams/users
MAX_WORKERS_FILES = 5        # Concurrent files per challenge

# Request timeouts
API_TIMEOUT = 15
FILE_TIMEOUT = 60

# File download settings
CHUNK_SIZE = 8192
PROGRESS_THRESHOLD_MB = 5  # Show progress every N MB

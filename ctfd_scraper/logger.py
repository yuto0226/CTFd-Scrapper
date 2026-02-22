"""Logging utilities for CTFd Scraper."""

import threading

# Thread-safe print lock
print_lock = threading.Lock()

# ANSI color codes
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

def log(tag, level, message):
    """統一日誌輸出
    
    Args:
        tag: 標籤，如 'team', 'user', 'chal', 'file', 'scoreboard', 'main'
        level: '+' (success), '-' (error), '!' (warn), '*' (info)
        message: 日誌訊息
    """
    colors = {
        '+': Colors.GREEN,
        '-': Colors.RED,
        '!': Colors.YELLOW,
        '*': Colors.BLUE
    }
    color = colors.get(level, Colors.RESET)
    with print_lock:
        print(f"{color}[{level}]{Colors.RESET} [{tag}] {message}")

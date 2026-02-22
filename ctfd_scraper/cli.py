"""Command-line interface for CTFd Scraper."""

import argparse
import os
import sys

from .api_client import CTFdClient
from .challenges import backup_challenges
from .teams import backup_teams
from .users import backup_users
from .scoreboard import backup_scoreboard
from .logger import log


def run_backup(config):
    """執行備份流程
    
    Args:
        config: 配置字典，包含：
            - url: CTFd URL
            - session: Session cookie
            - ctf_name: CTF 名稱 (可選)
            - output_dir: 輸出目錄
            - backup_challenges, backup_teams, backup_users, backup_scoreboard: 布林值
            - max_workers_*: 並行數量
            - *_timeout: 超時設定
    """
    log('main', '*', "CTFd Scraper v1.0.0")
    print("-" * 40)
    
    # 初始化客戶端
    client = CTFdClient(
        url=config['url'],
        session_cookie=config['session'],
        api_timeout=config.get('api_timeout', 15),
        file_timeout=config.get('file_timeout', 60)
    )
    
    # 取得或設定 CTF 名稱
    if config.get('ctf_name'):
        ctf_name = config['ctf_name']
        log('main', '*', f"使用指定名稱: {ctf_name}")
    else:
        ctf_name = client.get_ctf_name()
    
    # 設定備份目錄
    output_dir = config.get('output_dir', '.')
    backup_dir = os.path.join(output_dir, f"{ctf_name}_backup")
    
    log('main', '*', f"備份目錄: {backup_dir}")
    os.makedirs(backup_dir, exist_ok=True)
    
    # 更新配置到模組
    from . import challenges, teams, users
    challenges.MAX_WORKERS_CHALLENGES = config.get('max_workers_challenges', 10)
    challenges.MAX_WORKERS_FILES = config.get('max_workers_files', 5)
    teams.MAX_WORKERS_TEAMS = config.get('max_workers_teams', 20)
    users.MAX_WORKERS_TEAMS = config.get('max_workers_teams', 20)
    
    # 依序備份各項資料
    if config.get('backup_scoreboard', True):
        backup_scoreboard(client, backup_dir)
    
    if config.get('backup_challenges', True):
        backup_challenges(client, backup_dir)
    
    if config.get('backup_teams', True):
        backup_teams(client, backup_dir)
    
    if config.get('backup_users', True):
        backup_users(client, backup_dir)
    
    print("-" * 40)
    log('main', '+', "所有備份作業完成")


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        prog='ctfdscraper',
        description='High-performance CTFd competition backup tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage with URL and session cookie
  ctfdscraper -u https://ctf.example.com -s your-session-cookie
  
  # Custom CTF name and output directory
  ctfdscraper -u https://ctf.example.com -s cookie -n "MyCtf2026" -o ./backup
  
  # Only backup challenges
  ctfdscraper -u https://ctf.example.com -s cookie --only-chal
  
  # Backup everything except users
  ctfdscraper -u https://ctf.example.com -s cookie --no-user
  
  # Specify max workers for parallel processing
  ctfdscraper -u https://ctf.example.com -s cookie --max-workers-chal 15
        """
    )
    
    # Required arguments
    parser.add_argument(
        '-u', '--url',
        required=True,
        help='CTFd instance URL (e.g., https://ctf.example.com)'
    )
    
    parser.add_argument(
        '-s', '--session',
        required=True,
        help='Session cookie value for authentication'
    )
    
    # Optional arguments
    parser.add_argument(
        '-n', '--name',
        help='CTF name (auto-detected from website if not specified)'
    )
    
    parser.add_argument(
        '-o', '--output',
        default='.',
        help='Output directory for backup (default: current directory)'
    )
    
    # Selective backup options
    backup_group = parser.add_argument_group('backup selection')
    backup_group.add_argument(
        '--no-chal',
        action='store_true',
        help='Skip challenges backup'
    )
    
    backup_group.add_argument(
        '--no-team',
        action='store_true',
        help='Skip teams backup'
    )
    
    backup_group.add_argument(
        '--no-user',
        action='store_true',
        help='Skip users backup'
    )
    
    backup_group.add_argument(
        '--no-scoreboard',
        action='store_true',
        help='Skip scoreboard backup'
    )
    
    backup_group.add_argument(
        '--only-chal',
        action='store_true',
        help='Only backup challenges (skip teams, users, scoreboard)'
    )
    
    # Performance tuning
    perf_group = parser.add_argument_group('performance tuning')
    perf_group.add_argument(
        '--max-workers-chal',
        type=int,
        default=10,
        help='Maximum concurrent challenges (default: 10)'
    )
    
    perf_group.add_argument(
        '--max-workers-team',
        type=int,
        default=20,
        help='Maximum concurrent teams/users (default: 20)'
    )
    
    perf_group.add_argument(
        '--max-workers-file',
        type=int,
        default=5,
        help='Maximum concurrent files per challenge (default: 5)'
    )
    
    # Timeout settings
    timeout_group = parser.add_argument_group('timeout settings')
    timeout_group.add_argument(
        '--api-timeout',
        type=int,
        default=15,
        help='API request timeout in seconds (default: 15)'
    )
    
    timeout_group.add_argument(
        '--file-timeout',
        type=int,
        default=60,
        help='File download timeout in seconds (default: 60)'
    )
    
    # Version
    parser.add_argument(
        '-v', '--version',
        action='version',
        version='%(prog)s 1.0.0'
    )
    
    args = parser.parse_args()
    
    # Process --only-chal flag
    if args.only_chal:
        args.no_team = True
        args.no_user = True
        args.no_scoreboard = True
    
    # Validate arguments
    if args.max_workers_chal < 1 or args.max_workers_chal > 50:
        log('cli', '-', "max-workers-chal must be between 1 and 50")
        sys.exit(1)
    
    if args.max_workers_team < 1 or args.max_workers_team > 50:
        log('cli', '-', "max-workers-team must be between 1 and 50")
        sys.exit(1)
    
    if args.max_workers_file < 1 or args.max_workers_file > 20:
        log('cli', '-', "max-workers-file must be between 1 and 20")
        sys.exit(1)
    
    # Build configuration
    config = {
        'url': args.url,
        'session': args.session,
        'ctf_name': args.name,
        'output_dir': args.output,
        'backup_challenges': not args.no_chal,
        'backup_teams': not args.no_team,
        'backup_users': not args.no_user,
        'backup_scoreboard': not args.no_scoreboard,
        'max_workers_challenges': args.max_workers_chal,
        'max_workers_teams': args.max_workers_team,
        'max_workers_files': args.max_workers_file,
        'api_timeout': args.api_timeout,
        'file_timeout': args.file_timeout,
    }
    
    try:
        run_backup(config)
    except KeyboardInterrupt:
        log('cli', '!', "Backup interrupted by user")
        sys.exit(130)
    except Exception as e:
        log('cli', '-', f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

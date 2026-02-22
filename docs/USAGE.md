# Usage Guide

## Quick Start

### 命令列工具 (推薦)

```bash
# 基本用法：備份所有資料
ctfdscraper -u https://ctf.example.com -s your-session-cookie

# 自訂 CTF 名稱
ctfdscraper -u https://ctf.example.com -s cookie -n "MyCtf2026"

# 自訂輸出目錄
ctfdscraper -u https://ctf.example.com -s cookie -o ./backups

# 只備份 Challenge
ctfdscraper -u https://ctf.example.com -s cookie --only-chal

# 備份除了使用者以外的所有資料
ctfdscraper -u https://ctf.example.com -s cookie --no-user

# 查看所有選項
ctfdscraper --help
```

### 直接執行 (無需安裝)

```bash
python3 ctfdscraper.py -u https://ctf.example.com -s your-cookie
```

## 命令列選項

### 必填參數

- `-u, --url`: CTFd 實例 URL (例如：`https://ctf.example.com`)
- `-s, --session`: Session cookie 值用於身份驗證

### 可選參數

- `-n, --name`: CTF 名稱 (不指定則從網站 HTML title 自動檢測)
- `-o, --output`: 輸出目錄 (預設：當前目錄)
- `-v, --version`: 顯示版本資訊

### 備份選擇

- `--only-chal`: 只備份 Challenge (自動排除 teams/users/scoreboard)
- `--no-chal`: 跳過 Challenge 備份
- `--no-team`: 跳過 Team 備份
- `--no-user`: 跳過 User 備份
- `--no-scoreboard`: 跳過 Scoreboard 備份

### 效能調校

- `--max-workers-chal N`: 並行處理 Challenge 的數量 (預設：10，範圍：1-50)
- `--max-workers-team N`: 並行處理 Team/User 的數量 (預設：20，範圍：1-50)
- `--max-workers-file N`: 每個 Challenge 並行下載檔案數 (預設：5，範圍：1-20)

### 逾時設定

- `--api-timeout N`: API 請求逾時秒數 (預設：15)
- `--file-timeout N`: 檔案下載逾時秒數 (預設：60)

## 取得 Session Cookie

### 方法 1：Chrome/Edge 開發者工具

1. 登入 CTFd 網站
2. 按 `F12` 開啟開發者工具
3. 切換到 **Application** 分頁
4. 左側選單：**Storage → Cookies → (你的網站)**
5. 找到名為 `session` 的 cookie，複製其 **Value**

### 方法 2：Firefox 開發者工具

1. 登入 CTFd 網站
2. 按 `F12` 開啟開發者工具
3. 切換到 **Storage** 分頁
4. 左側選單：**Cookies → (你的網站)**
5. 找到 `session`，複製值

### 方法 3：使用 curl 指令

```bash
curl -c cookies.txt https://ctf.example.com/login -d "name=your_username&password=your_password"
grep session cookies.txt | awk '{print $7}'
```

## 使用範例

### 情境 1：快速備份比賽所有資料

```bash
# 一鍵備份完整資料
ctfdscraper -u https://ctf.bitskrieg.in -s "5cc1cb22-c036-49a7..."

# 輸出目錄：./bitsctf2026_backup/
```

### 情境 2：只要 Challenge 題目和檔案

```bash
# 不需要隊伍、使用者、排行榜
ctfdscraper -u https://ctf.bitskrieg.in -s "5cc1cb22..." --only-chal
```

### 情境 3：網速慢的環境

```bash
# 降低並行數、增加逾時
ctfdscraper -u https://ctf.example.com -s cookie \
  --max-workers-chal 5 \
  --max-workers-file 2 \
  --api-timeout 30 \
  --file-timeout 120
```

### 情境 4：高速網路環境

```bash
# 提升並行數量來加快備份
ctfdscraper -u https://ctf.example.com -s cookie \
  --max-workers-chal 20 \
  --max-workers-file 10 \
  --max-workers-team 30
```

### 情境 5：排除使用者資料 (User 通常很多)

```bash
# 只要 challenges + teams + scoreboard
ctfdscraper -u https://ctf.example.com -s cookie --no-user
```

### 情境 6：批次備份多個 CTF

```bash
#!/bin/bash
# batch_backup.sh

declare -A CTFS=(
  ["CTF2024_Quals"]="https://quals.ctf.com|cookie1"
  ["CTF2024_Finals"]="https://finals.ctf.com|cookie2"
  ["Practice_CTF"]="https://practice.ctf.com|cookie3"
)

for name in "${!CTFS[@]}"; do
  IFS='|' read -r url cookie <<< "${CTFS[$name]}"
  echo "🔄 Backing up $name..."
  ctfdscraper -u "$url" -s "$cookie" -n "$name" -o ./all_backups
  echo "✅ $name complete!"
done
```

## 程式化使用 (Python API)

```python
from ctfd_scraper.cli import run_backup

# 完整配置
config = {
    'url': 'https://ctf.example.com',
    'session': 'your-session-cookie',
    'ctf_name': 'MyCtf2026',  # 可選
    'output_dir': './backups',
    'backup_challenges': True,
    'backup_teams': True,
    'backup_users': False,  # 跳過 user
    'backup_scoreboard': True,
    'max_workers_challenges': 15,
    'max_workers_teams': 25,
    'max_workers_files': 8,
    'api_timeout': 20,
    'file_timeout': 90,
}

run_backup(config)
```

## 輸出結構

```
<CTF_Name>_backup/
├── Challenges/
│   ├── README.md                    # 所有題目總覽 (依分類分組)
│   ├── Crypto/
│   │   ├── RSA Challenge/
│   │   │   ├── description.md       # 題目描述、解題隊伍
│   │   │   ├── challenge.py         # 下載的檔案
│   │   │   └── output.txt
│   │   └── AES Problem/
│   │       └── description.md
│   ├── Web/
│   │   ├── SQL Injection/
│   │   │   ├── description.md
│   │   │   └── source.zip
│   │   └── XSS Challenge/
│   └── Pwn/
│       └── Buffer Overflow/
├── Scoreboard/
│   ├── full_scoreboard.json         # 隊伍排行 (JSON)
│   ├── full_scoreboard.md           # 隊伍排行 (Markdown)
│   ├── all_members_scoreboard.json  # 個人排行 (JSON)
│   └── all_members_scoreboard.md    # 個人排行 (Markdown)
├── Teams/
│   ├── README.md                    # 隊伍總覽
│   ├── TeamA/
│   │   └── team_info.json           # 包含隊員、解題記錄
│   └── TeamB/
│       └── team_info.json
└── Users/
    ├── README.md                    # 使用者總覽
    ├── user_123/
    │   └── user_info.json           # 包含隊伍、解題記錄
    └── user_456/
        └── user_info.json
```

## 疑難排解

### 連線問題

**症狀：** `[-] [api] API 請求失敗`

**解決方法：**
- 檢查網路連線
- 確認 URL 正確（需包含 `https://`）
- 確認 session cookie 仍然有效（未過期）
- 嘗試增加 `--api-timeout`

### 身份驗證失敗

**症狀：** 返回 HTML 而非 JSON，或 403/401 錯誤

**解決方法：**
- 重新登入網站取得新的 session cookie
- 檢查 cookie 值是否完整複製（沒有多餘空格）
- 確認帳號有權限存取相關 API

### 下載速度慢

**症狀：** 大檔案下載卡住或很慢

**解決方法：**
```bash
# 降低並行數量
ctfdscraper -u URL -s COOKIE --max-workers-chal 3 --max-workers-file 1

# 增加檔案下載逾時
ctfdscraper -u URL -s COOKIE --file-timeout 180
```

### 記憶體不足

**症狀：** 程式崩潰或系統變慢

**解決方法：**
```bash
# 分批備份
ctfdscraper -u URL -s COOKIE --only-chal               # 先備份 Challenge
ctfdscraper -u URL -s COOKIE --no-chal --no-user      # 再備份 Team + Scoreboard
ctfdscraper -u URL -s COOKIE --no-chal --no-team --no-scoreboard  # 最後備份 User
```

## 日誌訊息

- **[+]** 成功 - 操作成功完成 (綠色)
- **[-]** 錯誤 - 嚴重失敗 (紅色)
- **[!]** 警告 - 非致命問題，例如跳過無解題記錄的隊伍 (黃色)
- **[*]** 資訊 - 狀態更新 (藍色)

## 實用技巧

1. **定期備份：** 比賽期間每小時執行一次，避免遺失資料
2. **版本控制：** 將備份目錄加入 git 追蹤變更
3. **壓縮檔案：** 備份完成後可壓縮：`tar -czf backup.tar.gz ctf_backup/`
4. **CI/CD 自動化：** 參考下方 GitHub Actions 範例

## GitHub Actions 自動備份

在 `.github/workflows/ctf-backup.yml`：

```yaml
name: CTF Auto Backup

on:
  schedule:
    - cron: '0 */3 * * *'  # 每 3 小時執行一次
  workflow_dispatch:       # 允許手動觸發

jobs:
  backup:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python 3.9
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      
      - name: Install CTFd Scraper
        run: |
          pip install requests beautifulsoup4
          pip install -e .
      
      - name: Run Backup
        env:
          CTFD_SESSION: ${{ secrets.CTFD_SESSION }}
        run: |
          ctfdscraper -u https://ctf.example.com -s "$CTFD_SESSION" -o ./backups
      
      - name: Commit Changes
        run: |
          git config user.name "GitHub Actions"
          git config user.email "actions@github.com"
          git add backups/
          git diff-index --quiet HEAD || git commit -m "Auto backup $(date +'%Y-%m-%d %H:%M')"
          git push
      
      - name: Upload Artifacts
        uses: actions/upload-artifact@v3
        with:
          name: ctf-backup-${{ github.run_number }}
          path: ./backups
          retention-days: 30
```

**設定 Secret：**
1. GitHub Repo → Settings → Secrets and variables → Actions
2. New repository secret
3. Name: `CTFD_SESSION`
4. Value: 你的 session cookie
5. Add secret

## 常見問題

**Q: 可以同時備份多個 CTF 嗎？**  
A: 可以，使用不同的 `-n` 指定名稱，或寫 shell script 迴圈執行。

**Q: 需要管理員權限嗎？**  
A: 不需要，只要能登入並存取題目即可。部分隱藏題目可能需要特殊權限。

**Q: 會被 CTFd 偵測為攻擊嗎？**  
A: 工具使用正常 API 且有合理的 User-Agent，但請控制並行數量避免造成伺服器負擔。

**Q: 支援 CTFd 哪些版本？**  
A: 測試於 CTFd 3.x，理論上支援所有使用 `/api/v1/` 的版本。

**Q: 可以備份私有比賽嗎？**  
A: 可以，只要你的帳號有權限存取該比賽。

1. **Run during off-peak hours** to avoid rate limiting
2. **Use a stable connection** for large file downloads
3. **Check disk space** before backing up large competitions
4. **Save your session cookie** securely

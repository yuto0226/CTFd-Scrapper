# CLI Tool Examples

## 基本用法

```bash
# 完整備份
./ctfdscraper.py -u https://ctf.bitskrieg.in -s "YOUR_COOKIE_HERE"

# 只備份 Challenge
./ctfdscraper.py -u https://ctf.bitskrieg.in -s "YOUR_COOKIE_HERE" --only-chal

# 排除 User 資料
./ctfdscraper.py -u https://ctf.bitskrieg.in -s "YOUR_COOKIE_HERE" --no-user

# 自訂名稱和輸出目錄
./ctfdscraper.py -u https://ctf.bitskrieg.in -s "YOUR_COOKIE_HERE" \
  -n "BITSCTF2026" \
  -o ./my_backups

# 調整效能參數
./ctfdscraper.py -u https://ctf.bitskrieg.in -s "YOUR_COOKIE_HERE" \
  --max-workers-chal 15 \
  --max-workers-file 8 \
  --max-workers-team 30
```

## 安裝後使用

```bash
# 安裝到系統
pip install -e .

# 然後直接使用 ctfdscraper 命令
ctfdscraper -u https://ctf.bitskrieg.in -s "YOUR_COOKIE_HERE"

# 所有參數都一樣
ctfdscraper -u URL -s COOKIE --only-chal
ctfdscraper -u URL -s COOKIE --no-user --max-workers-chal 15
```

## 進階範例

```bash
# 批次備份腳本
for url in https://ctf1.com https://ctf2.com; do
  ctfdscraper -u "$url" -s "$COOKIE" -o ./all_backups
done

# 結合 cron 自動備份
# 每小時備份一次
0 * * * * /usr/bin/ctfdscraper -u https://ctf.example.com -s "$SESSION" >> /var/log/ctf-backup.log 2>&1
```


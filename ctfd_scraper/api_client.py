"""API client for CTFd."""

import requests
from bs4 import BeautifulSoup

from .logger import log


class CTFdClient:
    """CTFd API client with session management."""

    def __init__(self, url=None, session_cookie=None, api_timeout=15, file_timeout=60):
        """初始化 CTFd 客戶端

        Args:
            url: CTFd 實例 URL
            session_cookie: Session cookie 值
            api_timeout: API 請求超時（秒）
            file_timeout: 檔案下載超時（秒）
        """
        self.base_url = url or "https://ctf.bitskrieg.in"
        self.api_timeout = api_timeout
        self.file_timeout = file_timeout
        self.session = requests.Session()

        if session_cookie:
            self.session.cookies.update({"session": session_cookie})

        self.session.headers.update({"User-Agent": "Mozilla/5.0"})
        self.ctf_name = None

    def get_ctf_name(self):
        """從首頁 HTML title 取得 CTF 名稱"""
        if self.ctf_name:
            return self.ctf_name

        try:
            log("api", "*", "正在獲取 CTF 名稱...")
            response = self.session.get(self.base_url, timeout=self.api_timeout)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                title = soup.find("title")
                if title and title.string:
                    # 移除常見的後綴
                    name = title.string.strip()
                    name = name.replace(" - CTFd", "").strip()
                    # 清理檔案名稱不合法字元
                    for char in ["/", "\\", ":", "*", "?", '"', "<", ">", "|"]:
                        name = name.replace(char, "_")
                    self.ctf_name = name or "ctf"
                    log("api", "+", f"CTF 名稱: {self.ctf_name}")
                    return self.ctf_name
        except Exception as e:
            log("api", "!", f"無法獲取 CTF 名稱: {e}")

        self.ctf_name = "ctf"
        log("api", "*", f"使用預設名稱: {self.ctf_name}")
        return self.ctf_name

    def fetch_api(self, endpoint, debug=False):
        """通用 API 請求函數"""
        try:
            r = self.session.get(f"{self.base_url}{endpoint}", timeout=self.api_timeout)
            content_type = r.headers.get("Content-Type", "")

            if r.status_code == 200:
                if "application/json" in content_type:
                    return r.json().get("data", None)
            return None
        except Exception as e:
            if debug:
                log("api", "!", f"API 請求錯誤 ({endpoint}): {e}")
            return None

    def fetch_all_pages(self, endpoint):
        """獲取所有分頁資料"""
        all_data = []
        page = 1

        while True:
            data = self.fetch_api(f"{endpoint}?page={page}")
            if not data:
                break

            all_data.extend(data)

            if len(data) < 50:
                break

            page += 1

        return all_data

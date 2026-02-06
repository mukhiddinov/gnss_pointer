import json
import time
import urllib.request

from config import REFRESH_SAFETY_WINDOW_SEC

class TokenManager:
    def __init__(self, api_base: str, username: str, password: str, logger):
        self.api_base = api_base.rstrip("/")
        self.username = username
        self.password = password
        self.log = logger

        self.access_token: str | None = None
        self.refresh_token: str | None = None
        self.expires_at_ms: int = 0  # epoch ms

    def _request_json(self, method: str, path: str, payload=None, access_token=None, timeout=8.0):
        url = f"{self.api_base}{path}"
        headers = {"Content-Type": "application/json"}
        if access_token:
            headers["Authorization"] = f"Bearer {access_token}"

        data = None if payload is None else json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url=url, data=data, method=method, headers=headers)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8", errors="ignore")
            return resp.status, body

    def login(self):
        status, body = self._request_json(
            "POST",
            "/api/v1/auth/login",
            payload={"username": self.username, "password": self.password},
            timeout=10.0,
        )
        if status < 200 or status >= 300:
            raise RuntimeError(f"login failed: status={status} body={body}")

        obj = json.loads(body)
        self.access_token = obj["accessToken"]
        self.refresh_token = obj.get("refreshToken")
        self.expires_at_ms = int(obj.get("expiresAt", 0))
        self.log.info("AUTH: login ok")

    def refresh(self):
        if not self.access_token or not self.refresh_token:
            raise RuntimeError("refresh: missing access/refresh token")

        status, body = self._request_json(
            "POST",
            "/api/v1/auth/refresh",
            payload={"refreshToken": self.refresh_token},
            access_token=self.access_token,
            timeout=10.0,
        )
        if status < 200 or status >= 300:
            raise RuntimeError(f"refresh failed: status={status} body={body}")

        obj = json.loads(body)
        self.access_token = obj["accessToken"]
        self.refresh_token = obj.get("refreshToken", self.refresh_token)
        self.expires_at_ms = int(obj.get("expiresAt", 0))
        self.log.info("AUTH: refresh ok")

    def ensure_valid(self):
        now_ms = int(time.time() * 1000)

        if not self.access_token:
            self.login()
            return

        # expiresAt bo'lmasa, xavfsiz yo'l: login
        if self.expires_at_ms <= 0:
            self.login()
            return

        # tugashiga oz qolsa refresh
        if now_ms >= (self.expires_at_ms - REFRESH_SAFETY_WINDOW_SEC * 1000):
            try:
                self.refresh()
            except Exception as e:
                self.log.warning("AUTH: refresh failed -> relogin (%s)", e)
                self.login()

import json
import urllib.request

class ApiClient:
    def __init__(self, api_base: str, token_manager, logger):
        self.api_base = api_base.rstrip("/")
        self.auth = token_manager
        self.log = logger

    def _request(self, method: str, path: str, payload=None, timeout=6.0):
        self.auth.ensure_valid()
        url = f"{self.api_base}{path}"

        headers = {
            "Authorization": f"Bearer {self.auth.access_token}",
            "Content-Type": "application/json",
        }
        data = None if payload is None else json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url=url, data=data, method=method, headers=headers)

        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8", errors="ignore")
            return resp.status, body

    def post_point(self, autodrome_id: int, lon: float, lat: float):
        payload = {
            "autodromeId": autodrome_id,
            "point": {"longitude": lon, "latitude": lat},
            "angle": None,
        }
        return self._request("POST", "/api/v1/geo/point", payload=payload)

    def delete_geo(self):
        return self._request("DELETE", "/api/v1/geo", payload=None)

import os

def _get_int(name: str, default: int) -> int:
    v = os.getenv(name)
    return default if v is None else int(v)

def _get_float(name: str, default: float) -> float:
    v = os.getenv(name)
    return default if v is None else float(v)

def _get_str(name: str, default: str = "") -> str:
    v = os.getenv(name)
    return default if v is None else v

API_BASE = _get_str("API_BASE", "https://smart.devpro.uz").rstrip("/")
API_USERNAME = _get_str("API_USERNAME", "pointer1")
API_PASSWORD = _get_str("API_PASSWORD", "Password123#")

AUTODROME_ID = _get_int("AUTODROME_ID", 1)

SERIAL_PORT = _get_str("SERIAL_PORT", "/dev/ttyS0")
BAUDRATE = _get_int("BAUDRATE", 115200)

POINTER_BUTTON = _get_int("POINTER_BUTTON", 4)
CANCEL_BUTTON = _get_int("CANCEL_BUTTON", 17)

REFRESH_SAFETY_WINDOW_SEC = _get_int("REFRESH_SAFETY_WINDOW_SEC", 60)
KSXT_READ_TIMEOUT_SEC = _get_float("KSXT_READ_TIMEOUT_SEC", 2.0)

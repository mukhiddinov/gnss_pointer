import time
import logging
import serial
import urllib.error

from config import (
    API_BASE, API_USERNAME, API_PASSWORD, AUTODROME_ID,
    SERIAL_PORT, BAUDRATE,
    POINTER_BUTTON, CANCEL_BUTTON,
    KSXT_READ_TIMEOUT_SEC
)
from auth import TokenManager
from api_client import ApiClient
from gnss import read_next_valid_ksxt
from gpio_buttons import ButtonPins

def setup_logger():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )
    return logging.getLogger("pointer-client")

def main():
    log = setup_logger()

    # Serial
    ser = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=1)

    # Auth + API
    auth = TokenManager(API_BASE, API_USERNAME, API_PASSWORD, log)
    api = ApiClient(API_BASE, auth, log)

    # GPIO
    buttons = ButtonPins(POINTER_BUTTON, CANCEL_BUTTON, log)
    buttons.setup()

    # Initial login (fail bo'lsa ham keyin ensure_valid qiladi)
    try:
        auth.login()
    except Exception as e:
        log.warning("AUTH: initial login failed (%s) - will retry on demand", e)

    log.info("Started. pointer=%d cancel=%d serial=%s", POINTER_BUTTON, CANCEL_BUTTON, SERIAL_PORT)

    try:
        while True:
            evt = buttons.poll()
            if evt == "pointer":
                ksxt = read_next_valid_ksxt(ser, timeout_sec=KSXT_READ_TIMEOUT_SEC)
                if not ksxt:
                    log.warning("POINTER: KSXT not received within %.1fs", KSXT_READ_TIMEOUT_SEC)
                    continue

                # Console log: lat lon alt satl rtk_fix_status
                log.info(
                    "KSXT lat=%.9f lon=%.9f alt=%.4f satl=%s rtk_fix_status=%s(%s)",
                    ksxt["lat"], ksxt["lon"], ksxt["alt"],
                    str(ksxt["satl"]), str(ksxt["rtk_fix"]), ksxt["rtk_name"]
                )

                # POST payload values log (exact)
                log.info(
                    "POST values autodromeId=%d longitude=%.8f latitude=%.8f angle=null",
                    AUTODROME_ID, ksxt["lon"], ksxt["lat"]
                )

                try:
                    status, _ = api.post_point(AUTODROME_ID, ksxt["lon"], ksxt["lat"])
                    log.info("POST /geo/point -> %s", status)
                except urllib.error.HTTPError as e:
                    body = e.read().decode("utf-8", errors="ignore")
                    log.error("POST HTTPError %s %s", e.code, body)
                except Exception as e:
                    log.error("POST failed: %s", e)

            elif evt == "cancel":
                try:
                    status, _ = api.delete_geo()
                    log.info("DELETE /geo -> %s", status)
                except urllib.error.HTTPError as e:
                    body = e.read().decode("utf-8", errors="ignore")
                    log.error("DELETE HTTPError %s %s", e.code, body)
                except Exception as e:
                    log.error("DELETE failed: %s", e)

            time.sleep(0.02)

    finally:
        buttons.cleanup()

if __name__ == "__main__":
    main()

import time

# KSXT indekslar (siz yuborgan satrga mos)
LON_IDX = 2
LAT_IDX = 3
ALT_IDX = 4
RTK_FIX_IDX = 10     # 0..3 (Position quality)
SATL_IDX = 12        # sizdagi satrda 15

RTK_MAP = {
    0: "INVALID",
    1: "SINGLE",
    2: "RTK_FLOAT",
    3: "RTK_FIXED",
}

def parse_ksxt(line: str):
    if not line.startswith("$KSXT"):
        return None

    p = line.split(",")
    try:
        lon = float(p[LON_IDX])
        lat = float(p[LAT_IDX])
        alt = float(p[ALT_IDX])

        rtk_fix = int(p[RTK_FIX_IDX]) if p[RTK_FIX_IDX] else None
        satl = int(p[SATL_IDX]) if SATL_IDX < len(p) and p[SATL_IDX] else None

        # Minimal sanity-check (UZ). Xohlasangiz olib tashlang.
        if not (40 < lat < 42 and 68 < lon < 70):
            return None

        return {
            "lat": lat,
            "lon": lon,
            "alt": alt,
            "satl": satl,
            "rtk_fix": rtk_fix,
            "rtk_name": RTK_MAP.get(rtk_fix, "UNKNOWN"),
            "raw": line,
        }
    except Exception:
        return None

def read_next_valid_ksxt(ser, timeout_sec: float):
    deadline = time.time() + timeout_sec
    while time.time() < deadline:
        line = ser.readline().decode("ascii", errors="ignore").strip()
        data = parse_ksxt(line)
        if data:
            return data
    return None

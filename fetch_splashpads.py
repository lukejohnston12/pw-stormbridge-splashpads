#!/usr/bin/env python
"""
State‑by‑state splash‑pad scraper (overpy 0.7‑compatible, no threads).

Output: clean_splashpads_<timestamp>.csv
"""

import json, os, sys, time
from pathlib import Path

import overpy, pandas as pd
from dotenv import load_dotenv
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from tenacity import retry, wait_fixed, stop_after_attempt, retry_if_exception_type

# ───────────────────────── 1.  Config ─────────────────────────
OVERPASS_URL        = "https://overpass.kumi.systems/api/interpreter"
PER_STATE_TIMEOUT   = 240        # seconds per state query
PAUSE_BETWEEN_CALLS = 1.0        # polite delay between states

load_dotenv()
CORE_UA = os.getenv("USER_AGENT", "pw-splashpads-bot/0.1")
CONTACT = os.getenv("GEOCODER_EMAIL", "ljohnston@perryweather.com")
GEO_UA  = f"{CORE_UA} ({CONTACT})"            # Nominatim UA string

# admin_level 4 relations → contiguous 48 + DC  (HI & AK removed)
STATE_REL = {
    "AL": 161950, "AZ": 162018, "AR": 161646, "CA": 165475,
    "CO": 161961, "CT": 165794, "DE": 162110, "FL": 162050, "GA": 161957,
    "ID": 162116, "IL": 122586, "IN": 161816, "IA": 161650, "KS": 161644,
    "KY": 161655, "LA": 224922, "ME":  63512, "MD": 162112, "MA":  61315,
    "MI": 165789, "MN": 165471, "MS": 161943, "MO": 161638, "MT": 162115,
    "NE": 161648, "NV": 165473, "NH":  67213, "NJ": 224951, "NM": 162014,
    "NY":  61320, "NC": 224045, "ND": 161653, "OH": 162061, "OK": 161645,
    "OR": 165476, "PA": 162109, "RI": 392915, "SC": 224040, "SD": 161652,
    "TN": 161838, "TX": 114690, "UT": 161993, "VT":  60759, "VA": 224042,
    "WA": 165479, "WV": 162068, "WI": 165466, "WY": 161991, "DC": 162069,
}

QUERY_TEMPLATE = """
[out:json][timeout:{timeout}];
area({area_id})->.a;
(
  nwr["playground"="splash_pad"](area.a);
  nwr["playground:splash_pad"="yes"](area.a);
  nwr["fountain"="splash_pad"](area.a);
  nwr["water_feature"="splash_pad"](area.a);
  nwr["leisure"="water_park"](area.a);
  nwr["amenity"="water_park"](area.a);
  nwr["name"~"splash\\s*pad|spray\\s*ground|sprayground",i](area.a);
);
out center;
"""

# ─────────────────────── 2.  Helpers ────────────────────────
@retry(wait=wait_fixed(8), stop=stop_after_attempt(4),
       retry=retry_if_exception_type(overpy.exception.OverpassTooManyRequests))
def overpass_query(query: str) -> overpy.Result:
    return overpy.Overpass(url=OVERPASS_URL, max_retry_count=0).query(query)

def flatten(el):
    lat = getattr(el, "lat", None) or el.center_lat
    lon = getattr(el, "lon", None) or el.center_lon
    return {
        "osm_id": f"{el.__class__.__name__[0]}{el.id}",
        "name": el.tags.get("name", ""),
        "lat": lat,
        "lon": lon,
        "tags": json.dumps(el.tags, ensure_ascii=False),
    }

def classify(row):
    if '"water_park"' in row["tags"]:   return "commercial_water_park"
    if "HOA" in row["name"].upper():    return "hoa"
    if "school" in row["name"].lower(): return "school"
    return "municipal_park"

# ───────────────────────── 3.  Main ─────────────────────────
def main():
    all_elems = []

    for abbr, rel in STATE_REL.items():
        area_id = 3_600_000_000 + rel
        q       = QUERY_TEMPLATE.format(area_id=area_id, timeout=PER_STATE_TIMEOUT)
        try:
            res = overpass_query(q)
            cnt = len(res.nodes) + len(res.ways) + len(res.relations)
            print(f"{abbr:>2}  {cnt:4} objects")
            all_elems.extend(res.nodes + res.ways + res.relations)
        except Exception as exc:
            print(f"{abbr:>2}  ERROR → {exc}", file=sys.stderr)
        time.sleep(PAUSE_BETWEEN_CALLS)

    if not all_elems:
        sys.exit("No data returned – check Overpass status and retry.")

    df = pd.DataFrame(flatten(e) for e in all_elems)
    df["key"] = df["lat"].round(5).astype(str) + df["lon"].round(5).astype(str) + df["name"]
    df = df.drop_duplicates("key").drop(columns="key")

    print("→ reverse‑geocoding …")
    geocoder = Nominatim(user_agent=GEO_UA, timeout=3)
    rev      = RateLimiter(geocoder.reverse, min_delay_seconds=1)

    cities, states, zips = [], [], []
    for r in df.itertuples():
        try:
            a = rev((r.lat, r.lon), addressdetails=True).raw["address"]
            cities.append(a.get("city") or a.get("town") or a.get("village"))
            states.append(a.get("state")); zips.append(a.get("postcode"))
        except Exception:
            cities.append(None); states.append(None); zips.append(None)

    df[["city", "state", "zip"]] = list(zip(cities, states, zips))
    df["site_type"] = df.apply(classify, axis=1)

    out = Path(f"clean_splashpads_{int(time.time())}.csv")
    df.to_csv(out, index=False)
    print(f"\n✅  Saved {len(df):,} rows → {out}")

if __name__ == "__main__":
    main()
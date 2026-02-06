# usgs_service.py - USGS Earthquake service
import requests
import pandas as pd
from datetime import datetime, timedelta, timezone
from .config import USGS_API_BASE_URL, CURRENT_YEAR

def _iso(dt: datetime) -> str:
    """Format datetime object to ISO 8601 string needed by USGS API."""
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")

def fetch_global_last24h_text(min_mag: float = 5.0, limit: int = 10) -> str:
    """Fetch global significant earthquakes from USGS in the past 24 hours."""
    now_utc = datetime.now(timezone.utc)
    since = now_utc - timedelta(hours=24)
    params = {
        "format": "geojson",
        "starttime": _iso(since),
        "endtime": _iso(now_utc),
        "minmagnitude": float(min_mag),
        "limit": int(limit),
        "orderby": "time",
    }
    try:
        r = requests.get(USGS_API_BASE_URL, params=params, timeout=15)
        r.raise_for_status()
        features = r.json().get("features", [])
        if not features:
            return f"✅ No significant earthquakes (M≥{min_mag}) globally in the past 24 hours."
        
        lines = [f"🚨 Recent 24h Global Significant Earthquakes (M≥{min_mag}):", "-" * 20]
        for f in features:
            p = f["properties"]
            t_utc = datetime.fromtimestamp(p["time"] / 1000, tz=timezone.utc)
            
            lines.append(
                f"Magnitude: {p['mag']:.1f} | Date/Time: {t_utc.strftime('%Y-%m-%d %H:%M')} (UTC)\n"
                f"Location: {p.get('place', 'N/A')}\n"
                f"Report Link: {p.get('url', 'None')}"
            )
        return "\n\n".join(lines)
    except Exception as e:
        return f"❌ Query failed: {e}"

def fetch_taiwan_df_this_year(min_mag: float = 5.0) -> pd.DataFrame | str:
    """Fetch significant earthquakes in Taiwan region from USGS this year."""
    now_utc = datetime.now(timezone.utc)
    start_of_year_utc = datetime(now_utc.year, 1, 1, tzinfo=timezone.utc)
    params = {
        "format": "geojson", "starttime": _iso(start_of_year_utc), "endtime": _iso(now_utc),
        "minmagnitude": float(min_mag),
        "minlatitude": 21, "maxlatitude": 26,
        "minlongitude": 119, "maxlongitude": 123,
        "limit": 250,
        "orderby": "time",
    }
    try:
        r = requests.get(USGS_API_BASE_URL, params=params, timeout=20)
        r.raise_for_status()
        features = r.json().get("features", [])
        if not features:
            return f"✅ No significant earthquakes (M≥{min_mag:.1f}) in Taiwan region this year ({CURRENT_YEAR})."
        
        rows = []
        for f in features:
            p = f["properties"]
            lon, lat, *_ = f["geometry"]["coordinates"]
            rows.append({
                "latitude": lat, 
                "longitude": lon, 
                "magnitude": p["mag"],
                "place": p.get("place", ""), 
                "time_utc": datetime.fromtimestamp(p["time"]/1000, tz=timezone.utc),
                "url": p.get("url", "")
            })
        return pd.DataFrame(rows)
    except Exception as e:
        return f"❌ Query failed: {e}"

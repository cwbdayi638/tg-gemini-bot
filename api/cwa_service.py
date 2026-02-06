# cwa_service.py - Taiwan Central Weather Administration earthquake service
import requests
import re
import pandas as pd
from datetime import datetime, timedelta, timezone
from .config import CWA_API_KEY, CWA_ALARM_API, CWA_SIGNIFICANT_API

TAIPEI_TZ = timezone(timedelta(hours=8))

def _escape_braces(s: str) -> str:
    """Escape curly braces for string formatting."""
    return str(s).replace('{', '{{').replace('}', '}}')

def _to_float(x):
    """Safely convert a value to float."""
    if x is None: return None
    s = str(x).strip()
    m = re.search(r"[-+]?\d+(?:\.\d+)?", s)
    return float(m.group()) if m else None

def _parse_cwa_time(s: str) -> tuple[str, str]:
    """Parse CWA time format and return Taiwan and UTC time strings."""
    if not s: return ("Unknown", "Unknown")
    dt_utc = None
    try:
        dt_utc = datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError:
        try:
            dt_local = datetime.strptime(s, "%Y-%m-%d %H:%M:%S")
            dt_local = dt_local.replace(tzinfo=TAIPEI_TZ)
            dt_utc = dt_local.astimezone(timezone.utc)
        except Exception:
            return (s, "Unknown")
    if dt_utc:
        tw_str = dt_utc.astimezone(TAIPEI_TZ).strftime("%Y-%m-%d %H:%M")
        utc_str = dt_utc.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M")
        return (tw_str, utc_str)
    return (s, "Unknown")

def fetch_cwa_alarm_list(limit: int = 5) -> str:
    """Fetch earthquake early warnings from CWA API."""
    try:
        r = requests.get(CWA_ALARM_API, timeout=10)
        r.raise_for_status()
        payload = r.json()
    except Exception as e:
        return f"❌ Earthquake warning query failed: {e}"
    items = payload.get("data", [])
    if not items: return "✅ No earthquake warnings at this time."
    def _key(it):
        try: return datetime.fromisoformat(it.get("originTime", "").replace("Z", "+00:00"))
        except: return datetime.min.replace(tzinfo=timezone.utc)
    items = sorted(items, key=_key, reverse=True)
    lines = ["🚨 Earthquake Early Warnings (Latest):", "-" * 20]
    for it in items[:limit]:
        mag = _to_float(it.get("magnitudeValue"))
        depth = _to_float(it.get("depth"))
        tw_str, _ = _parse_cwa_time(it.get("originTime", ""))
        identifier = _escape_braces(it.get('identifier', '—'))
        msg_type = _escape_braces(it.get('msgType', '—'))
        msg_no = _escape_braces(it.get('msgNo', '—'))
        location_desc_list = it.get('locationDesc')
        areas_str = ", ".join(str(area) for area in location_desc_list) if isinstance(location_desc_list, list) and location_desc_list else "—"
        areas = _escape_braces(areas_str)
        mag_str = f"{mag:.1f}" if mag is not None else "—"
        depth_str = f"{depth:.0f}" if depth is not None else "—"
        lines.append(
            f"Event: {identifier} | Type: {msg_type}#{msg_no}\n"
            f"Magnitude/Depth: M{mag_str} / {depth_str} km\n"
            f"Time: {tw_str} (Taiwan Time)\n"
            f"Location: {areas}"
        )
    return "\n\n".join(lines).strip()

def _parse_significant_earthquakes(obj: dict) -> pd.DataFrame:
    """Parse significant earthquake data from CWA API response."""
    records = obj.get("records", {})
    quakes = records.get("Earthquake", [])
    rows = []
    for q in quakes:
        ei = q.get("EarthquakeInfo", {})
        
        # Use robust way to get all data, checking all known case variations
        epic = ei.get("Epicenter") or ei.get("epicenter") or {}
        mag_info = ei.get("Magnitude") or ei.get("magnitude") or ei.get("EarthquakeMagnitude") or {}
        depth_raw = ei.get("FocalDepth") or ei.get("depth") or ei.get("Depth")
        mag_raw = mag_info.get("MagnitudeValue") or mag_info.get("magnitudeValue") or mag_info.get("Value") or mag_info.get("value")
        
        rows.append({
            "ID": q.get("EarthquakeNo"), "Time": ei.get("OriginTime"),
            "Lat": _to_float(epic.get("EpicenterLatitude") or epic.get("epicenterLatitude")),
            "Lon": _to_float(epic.get("EpicenterLongitude") or epic.get("epicenterLongitude")),
            "Depth": _to_float(depth_raw), 
            "Magnitude": _to_float(mag_raw),
            "Location": epic.get("Location") or epic.get("location"), 
            "URL": q.get("Web") or q.get("ReportURL"),
        })
        
    df = pd.DataFrame(rows)
    if not df.empty and "Time" in df.columns:
        df["Time"] = pd.to_datetime(df["Time"], errors="coerce").dt.tz_localize(TAIPEI_TZ)
    return df

def fetch_significant_earthquakes(days: int = 7, limit: int = 5) -> str:
    """Fetch significant earthquakes from CWA API."""
    if not CWA_API_KEY: return "❌ Significant earthquake query failed: Administrator has not set CWA_API_KEY."
    now = datetime.now(timezone.utc)
    time_from = (now - timedelta(days=days)).strftime("%Y-%m-%d")
    params = {"Authorization": CWA_API_KEY, "format": "JSON", "timeFrom": time_from}
    try:
        r = requests.get(CWA_SIGNIFICANT_API, params=params, timeout=15)
        r.raise_for_status()
        data = r.json()
        df = _parse_significant_earthquakes(data)
        if df.empty: return f"✅ No significant earthquakes reported in the past {days} days."
        df = df.sort_values(by="Time", ascending=False).head(limit)
        lines = [f"🚨 CWA Latest Significant Earthquakes (past {days} days):", "-" * 20]
        for _, row in df.iterrows():
            mag_str = f"{row['Magnitude']:.1f}" if pd.notna(row['Magnitude']) else "—"
            depth_str = f"{row['Depth']:.0f}" if pd.notna(row['Depth']) else "—"
            lines.append(
                f"Time: {row['Time'].strftime('%Y-%m-%d %H:%M') if pd.notna(row['Time']) else '—'}\n"
                f"Location: {row['Location'] or '—'}\n"
                f"Magnitude: M{mag_str} | Depth: {depth_str} km\n"
                f"Report: {row['URL'] or 'None'}"
            )
        return "\n\n".join(lines)
    except Exception as e:
        return f"❌ Significant earthquake query failed: {e}"

def fetch_latest_significant_earthquake() -> dict | None:
    """Fetch the latest significant earthquake from CWA API."""
    try:
        if not CWA_API_KEY: raise ValueError("Error: CWA_API_KEY Secret not set.")
        params = {"Authorization": CWA_API_KEY, "format": "JSON", "limit": 1, "orderby": "OriginTime desc"}
        r = requests.get(CWA_SIGNIFICANT_API, params=params, timeout=15)
        r.raise_for_status()
        data = r.json()
        df = _parse_significant_earthquakes(data)
        if df.empty: return None

        latest_eq_data = df.iloc[0].to_dict()
        
        quakes = data.get("records", {}).get("Earthquake", [])
        if quakes:
            latest_eq_data["ImageURL"] = quakes[0].get("ReportImageURI")

        if pd.notna(latest_eq_data.get("Time")):
            latest_eq_data["TimeStr"] = latest_eq_data["Time"].strftime('%Y-%m-%d %H:%M')

        return latest_eq_data
    except Exception as e:
        raise e

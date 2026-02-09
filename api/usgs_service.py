# usgs_service.py - USGS Earthquake service
import requests
import pandas as pd
from datetime import datetime, timedelta, timezone
from .config import USGS_API_BASE_URL, CURRENT_YEAR

# Global earthquake query API endpoint
GLOBAL_EARTHQUAKE_API = "https://cwadayi-python-app.hf.space/earthquakes"

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

def fetch_global_earthquakes_by_date(start_date: str, end_date: str, min_magnitude: float = 5.0) -> str:
    """
    Fetch global earthquake data from external API based on date range and minimum magnitude.
    
    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        min_magnitude: Minimum earthquake magnitude (default 5.0)
    
    Returns:
        Formatted string with earthquake results
    """
    try:
        # Validate date format and range
        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            return "❌ 日期格式錯誤！請使用 YYYY-MM-DD 格式（例如：2024-07-01）"
        
        if start_dt > end_dt:
            return "❌ 日期範圍錯誤！起始日期不能晚於結束日期"
        
        # Validate magnitude
        try:
            min_mag = float(min_magnitude)
            if min_mag < 0 or min_mag > 10:
                return "❌ 規模參數錯誤！請輸入 0-10 之間的數值"
        except ValueError:
            return "❌ 規模參數格式錯誤！請輸入數字（例如：5.0）"
        
        params = {
            "start_date": start_date,
            "end_date": end_date,
            "min_magnitude": min_mag
        }
        
        r = requests.get(GLOBAL_EARTHQUAKE_API, params=params, timeout=30)
        r.raise_for_status()
        data = r.json()
        
        # Handle error response from API
        if "error" in data:
            return f"❌ API 錯誤：{data['error']}"
        
        earthquakes = data.get("earthquakes", [])
        total_count = data.get("count", len(earthquakes))
        
        if not earthquakes:
            return f"✅ 在 {start_date} 至 {end_date} 期間，沒有規模 ≥{min_mag} 的地震記錄。"
        
        lines = [
            f"🌍 全球地震查詢結果",
            f"📅 期間：{start_date} 至 {end_date}",
            f"📊 規模：M≥{min_mag}",
            f"📈 共 {total_count} 筆記錄",
            "-" * 30
        ]
        
        # Display up to 15 earthquakes
        display_count = min(15, len(earthquakes))
        for i, eq in enumerate(earthquakes[:display_count], 1):
            mag = eq.get("magnitude", "—")
            mag_str = f"{mag:.1f}" if isinstance(mag, (int, float)) else str(mag)
            
            time_str = eq.get("time", "—")
            place = eq.get("place", "未知地點")
            depth = eq.get("depth", "—")
            depth_str = f"{depth:.1f}" if isinstance(depth, (int, float)) else str(depth)
            
            lines.append(
                f"{i}. 規模：M{mag_str} | 深度：{depth_str} km\n"
                f"   時間：{time_str}\n"
                f"   位置：{place}"
            )
        
        if total_count > display_count:
            lines.append(f"\n...（另有 {total_count - display_count} 筆記錄）")
        
        return "\n\n".join(lines)
        
    except requests.exceptions.Timeout:
        return "❌ 查詢超時，請稍後再試。"
    except requests.exceptions.RequestException as e:
        return f"❌ 網路請求失敗：{e}"
    except Exception as e:
        return f"❌ 查詢失敗：{e}"

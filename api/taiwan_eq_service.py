# taiwan_eq_service.py - Fetch Taiwan earthquake data from SQLite API
import requests
import pandas as pd

TAIWAN_EQ_API = "https://cwadayi-sqlite-api.hf.space/items/"


def fetch_taiwan_eq_data() -> pd.DataFrame:
    """Fetch all Taiwan earthquake records from the remote SQLite API.

    Returns a DataFrame with columns:
        id, date, time, lat, lon, depth, ML, nstn, dmin, gap,
        trms, ERH, ERZ, fixed, nph, quality
    Raises RuntimeError on network / API errors.
    """
    try:
        r = requests.get(TAIWAN_EQ_API, timeout=30)
        r.raise_for_status()
        data = r.json()
    except requests.exceptions.Timeout:
        raise RuntimeError("查詢超時，請稍後再試。")
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"網路請求失敗：{e}")

    items = data.get("items", [])
    if not items:
        raise RuntimeError("API 回傳資料為空。")

    df = pd.DataFrame(items)
    # Ensure numeric types
    for col in ("lat", "lon", "depth", "ML", "dmin", "trms", "ERH", "ERZ"):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    for col in ("nstn", "gap", "nph"):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")
    return df


def filter_taiwan_eq(
    df: pd.DataFrame,
    start_date: str | None = None,
    end_date: str | None = None,
    min_ml: float | None = None,
    max_ml: float | None = None,
    min_depth: float | None = None,
    max_depth: float | None = None,
) -> pd.DataFrame:
    """Apply user-specified filters to the earthquake DataFrame.

    Parameters
    ----------
    df : DataFrame from ``fetch_taiwan_eq_data``
    start_date, end_date : YYYY-MM-DD strings (inclusive)
    min_ml, max_ml : magnitude (ML) range
    min_depth, max_depth : depth range in km
    """
    filtered = df.copy()
    if start_date:
        filtered = filtered[filtered["date"] >= start_date]
    if end_date:
        filtered = filtered[filtered["date"] <= end_date]
    if min_ml is not None:
        filtered = filtered[filtered["ML"] >= min_ml]
    if max_ml is not None:
        filtered = filtered[filtered["ML"] <= max_ml]
    if min_depth is not None:
        filtered = filtered[filtered["depth"] >= min_depth]
    if max_depth is not None:
        filtered = filtered[filtered["depth"] <= max_depth]
    return filtered.reset_index(drop=True)


def format_taiwan_eq_text(df: pd.DataFrame, filters_desc: str = "") -> str:
    """Return a fancy formatted text summary of the filtered earthquake data.

    Parameters
    ----------
    df : filtered DataFrame
    filters_desc : human-readable description of applied filters
    """
    count = len(df)
    if count == 0:
        return "✅ 沒有符合條件的地震記錄。"

    lines = [
        "🇹🇼 台灣地震查詢結果",
        f"📊 共 {count} 筆記錄",
    ]
    if filters_desc:
        lines.insert(1, f"🔍 篩選條件：{filters_desc}")
    lines.append("─" * 28)

    display = min(20, count)
    for i, (_, row) in enumerate(df.head(display).iterrows(), 1):
        ml_str = f"{row['ML']:.2f}" if pd.notna(row["ML"]) else "—"
        depth_str = f"{row['depth']:.1f}" if pd.notna(row["depth"]) else "—"
        lat_str = f"{row['lat']:.4f}" if pd.notna(row["lat"]) else "—"
        lon_str = f"{row['lon']:.4f}" if pd.notna(row["lon"]) else "—"
        quality = row.get("quality", "—")
        lines.append(
            f"{i}. 📅 {row['date']}  ⏰ {row['time']}\n"
            f"   規模：ML {ml_str} | 深度：{depth_str} km\n"
            f"   位置：({lat_str}, {lon_str}) | 品質：{quality}"
        )

    if count > display:
        lines.append(f"\n...（另有 {count - display} 筆記錄未顯示）")

    # Summary statistics
    lines.append("─" * 28)
    lines.append("📈 統計摘要")
    lines.append(f"   最大規模：ML {df['ML'].max():.2f}")
    lines.append(f"   最小規模：ML {df['ML'].min():.2f}")
    lines.append(f"   平均深度：{df['depth'].mean():.1f} km")
    lines.append(f"   日期範圍：{df['date'].min()} ~ {df['date'].max()}")

    return "\n\n".join(lines)

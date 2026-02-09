# plotting_service.py - Earthquake map visualization service
import os
import uuid
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # Use non-interactive backend
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
import matplotlib.cm as cm
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from .config import STATIC_DIR, CURRENT_YEAR

def create_and_save_map(df: pd.DataFrame) -> str:
    """Create an earthquake map, save the image, and return the filename."""
    fig, ax = plt.subplots(figsize=(9, 6), dpi=150, subplot_kw={"projection": ccrs.PlateCarree()})
    ax.set_extent([118.5, 123.5, 20.5, 26.8], crs=ccrs.PlateCarree())
    ax.add_feature(cfeature.LAND, facecolor="lightgray")
    ax.add_feature(cfeature.OCEAN, facecolor="lightblue")
    ax.add_feature(cfeature.COASTLINE, linewidth=0.5)
    ax.add_feature(cfeature.BORDERS, linestyle="--", linewidth=0.5)
    ax.set_title(f"Significant Earthquakes (M≥5.0) in Taiwan Area This Year ({CURRENT_YEAR}) — UTC")
    gl = ax.gridlines(draw_labels=True, linestyle="--", linewidth=0.5, alpha=0.4)
    gl.top_labels = False
    gl.right_labels = False

    mags = df["magnitude"].astype(float).clip(lower=0)
    norm = Normalize(vmin=max(4.5, mags.min()), vmax=max(6.5, mags.max()))
    cmap = cm.get_cmap("YlOrRd")
    colors = cmap(norm(mags.values))
    sizes = 15 + (mags - mags.min()) * 25

    ax.scatter(df["longitude"].values, df["latitude"].values,
               s=sizes, c=colors, edgecolor="k", linewidths=0.4, alpha=0.9,
               transform=ccrs.PlateCarree())

    fig.colorbar(cm.ScalarMappable(norm=norm, cmap=cmap), ax=ax, pad=0.02).set_label("Magnitude")

    filename = f"map_{uuid.uuid4().hex}.png"
    filepath = os.path.join(STATIC_DIR, filename)
    fig.tight_layout()
    fig.savefig(filepath)
    plt.close(fig)
    return filename


def create_global_earthquake_map(earthquakes: list, start_date: str, end_date: str, min_mag: float = 5.0) -> str | None:
    """Create a global earthquake epicenter map from a list of earthquake dicts and return the file path.
    
    Each dict should have 'latitude', 'longitude', and 'magnitude' keys.
    Returns the full file path of the saved PNG, or None if no valid data.
    """
    rows = []
    for eq in earthquakes:
        lat = eq.get("latitude")
        lon = eq.get("longitude")
        mag = eq.get("magnitude")
        if isinstance(lat, (int, float)) and isinstance(lon, (int, float)) and isinstance(mag, (int, float)):
            rows.append({"latitude": lat, "longitude": lon, "magnitude": mag})
    
    if not rows:
        return None
    
    df = pd.DataFrame(rows)
    
    fig, ax = plt.subplots(figsize=(12, 6), dpi=150, subplot_kw={"projection": ccrs.PlateCarree()})
    ax.set_global()
    ax.add_feature(cfeature.LAND, facecolor="lightgray")
    ax.add_feature(cfeature.OCEAN, facecolor="lightblue")
    ax.add_feature(cfeature.COASTLINE, linewidth=0.5)
    ax.add_feature(cfeature.BORDERS, linestyle="--", linewidth=0.5)
    ax.set_title(f"Global Earthquakes (M≥{min_mag}) — {start_date} to {end_date}")
    gl = ax.gridlines(draw_labels=True, linestyle="--", linewidth=0.5, alpha=0.4)
    gl.top_labels = False
    gl.right_labels = False
    
    mags = df["magnitude"].astype(float).clip(lower=0)
    norm = Normalize(vmin=max(4.5, mags.min()), vmax=max(9.0, mags.max()))
    cmap = cm.get_cmap("YlOrRd")
    colors = cmap(norm(mags.values))
    sizes = 20 + (mags - mags.min()) * 30
    
    ax.scatter(df["longitude"].values, df["latitude"].values,
               s=sizes, c=colors, edgecolor="k", linewidths=0.4, alpha=0.9,
               transform=ccrs.PlateCarree())
    
    fig.colorbar(cm.ScalarMappable(norm=norm, cmap=cmap), ax=ax, pad=0.02).set_label("Magnitude")
    
    filename = f"global_map_{uuid.uuid4().hex}.png"
    filepath = os.path.join(STATIC_DIR, filename)
    fig.tight_layout()
    fig.savefig(filepath)
    plt.close(fig)
    return filepath

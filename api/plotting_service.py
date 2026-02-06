# plotting_service.py - Earthquake map visualization service
import os
import uuid
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # Use non-interactive backend
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
import matplotlib.cm as cm
from .config import STATIC_DIR, CURRENT_YEAR

def create_and_save_map(df: pd.DataFrame) -> str:
    """Create an earthquake map, save the image, and return the filename."""
    fig, ax = plt.subplots(figsize=(9, 6), dpi=150)
    ax.set_xlim(118.5, 123.5)
    ax.set_ylim(20.5, 26.8)
    ax.set_xlabel("Longitude (°E)")
    ax.set_ylabel("Latitude (°N)")
    ax.set_title(f"Significant Earthquakes (M≥5.0) in Taiwan Area This Year ({CURRENT_YEAR}) — UTC")
    ax.grid(True, linestyle="--", linewidth=0.5, alpha=0.4)

    mags = df["magnitude"].astype(float).clip(lower=0)
    norm = Normalize(vmin=max(4.5, mags.min()), vmax=max(6.5, mags.max()))
    cmap = cm.get_cmap("YlOrRd")
    colors = cmap(norm(mags.values))
    sizes = 15 + (mags - mags.min()) * 25

    ax.scatter(df["longitude"].values, df["latitude"].values,
               s=sizes, c=colors, edgecolor="k", linewidths=0.4, alpha=0.9)

    fig.colorbar(cm.ScalarMappable(norm=norm, cmap=cmap), ax=ax, pad=0.02).set_label("Magnitude")

    filename = f"map_{uuid.uuid4().hex}.png"
    filepath = os.path.join(STATIC_DIR, filename)
    fig.tight_layout()
    fig.savefig(filepath)
    plt.close(fig)
    return filename

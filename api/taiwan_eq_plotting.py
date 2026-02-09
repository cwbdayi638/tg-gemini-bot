# taiwan_eq_plotting.py - Plot Taiwan earthquake maps using Plotly
import os
import uuid
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from .config import STATIC_DIR


def create_taiwan_eq_map(df: pd.DataFrame, title: str = "台灣地震分布圖") -> str | None:
    """Create an earthquake scatter-geo map saved as a PNG image.

    Uses ``plotly.express`` for the colour-coded scatter layer and
    ``plotly.graph_objects`` for a secondary depth layer.

    Parameters
    ----------
    df : DataFrame with columns ``lat``, ``lon``, ``ML``, ``depth``, ``date``, ``time``.
    title : map title string.

    Returns
    -------
    Full file path of the saved PNG image, or ``None`` if no valid data.
    """
    if df.empty:
        return None

    work = df.copy()
    work = work.dropna(subset=["lat", "lon", "ML"])
    if work.empty:
        return None

    # Build hover text
    work["label"] = work.apply(
        lambda r: (
            f"日期: {r['date']}<br>"
            f"時間: {r['time']}<br>"
            f"規模: ML {r['ML']:.2f}<br>"
            f"深度: {r['depth']:.1f} km<br>"
            f"位置: ({r['lat']:.4f}, {r['lon']:.4f})"
        ),
        axis=1,
    )

    # Marker sizes proportional to magnitude
    work["marker_size"] = (work["ML"] - work["ML"].min() + 1) * 6

    # ----- plotly.express scatter_geo (magnitude colour) -----
    fig = px.scatter_geo(
        work,
        lat="lat",
        lon="lon",
        color="ML",
        size="marker_size",
        hover_name="label",
        color_continuous_scale="YlOrRd",
        size_max=22,
        title=title,
    )

    # ----- plotly.graph_objects trace (depth overlay) -----
    fig.add_trace(
        go.Scattergeo(
            lat=work["lat"],
            lon=work["lon"],
            mode="markers",
            marker=dict(
                size=work["marker_size"],
                color=work["depth"],
                colorscale="Blues",
                showscale=True,
                colorbar=dict(
                    title="深度 (km)",
                    x=1.08,
                    len=0.5,
                    yanchor="bottom",
                    y=0,
                ),
                opacity=0.4,
            ),
            text=work["label"],
            hoverinfo="text",
            name="深度",
        )
    )

    fig.update_geos(
        resolution=50,
        showcountries=True,
        showland=True,
        landcolor="rgb(243,243,243)",
        showocean=True,
        oceancolor="rgb(204,229,255)",
        showcoastlines=True,
        coastlinecolor="rgb(80,80,80)",
        lonaxis_range=[119, 124],
        lataxis_range=[21, 26.5],
        projection_type="mercator",
    )

    fig.update_layout(
        margin=dict(l=0, r=0, t=50, b=0),
        title_font_size=16,
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
        coloraxis_colorbar=dict(title="規模 (ML)"),
        width=900,
        height=700,
    )

    filename = f"tw_eq_{uuid.uuid4().hex}.png"
    filepath = os.path.join(STATIC_DIR, filename)
    fig.write_image(filepath, scale=2)
    return filepath

# taiwan_eq_plotting.py - Plot Taiwan earthquake maps using Plotly and Folium
import os
import uuid
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from .config import STATIC_DIR

# Try to import folium for interactive maps
try:
    import folium
    from folium.plugins import MarkerCluster
    FOLIUM_AVAILABLE = True
except ImportError:
    FOLIUM_AVAILABLE = False
    print("Warning: folium not available, using Plotly for maps")


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


def create_taiwan_eq_folium_map(df: pd.DataFrame, title: str = "台灣地震分布圖") -> str | None:
    """Create an interactive earthquake map using Folium.

    Parameters
    ----------
    df : DataFrame with columns ``lat``, ``lon``, ``ML``, ``depth``, ``date``, ``time``.
    title : map title string.

    Returns
    -------
    Full file path of the saved HTML file, or ``None`` if no valid data or folium not available.
    """
    if not FOLIUM_AVAILABLE:
        # Fallback to Plotly if Folium is not available
        return create_taiwan_eq_map(df, title)
    
    if df.empty:
        return None

    work = df.copy()
    work = work.dropna(subset=["lat", "lon", "ML"])
    if work.empty:
        return None

    # Create Folium map centered on Taiwan with OpenStreetMap for better coastline detail
    m = folium.Map(
        location=[23.5, 121], 
        zoom_start=7, 
        tiles="OpenStreetMap",
        control_scale=True
    )
    
    # Add alternative tile layers for better visualization
    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr='Esri',
        name='Satellite',
        overlay=False,
        control=True
    ).add_to(m)
    
    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}',
        attr='Esri',
        name='Terrain',
        overlay=False,
        control=True
    ).add_to(m)

    # Create a MarkerCluster for better performance with many markers
    marker_cluster = MarkerCluster(name="地震事件").add_to(m)

    # Define color scale based on magnitude
    def get_color_by_magnitude(ml):
        if ml < 3.0:
            return "green"
        elif ml < 4.0:
            return "blue"
        elif ml < 5.0:
            return "yellow"
        elif ml < 6.0:
            return "orange"
        else:
            return "red"

    # Iterate through earthquake events and add to map
    for idx, row in work.iterrows():
        try:
            lat = row["lat"]
            lon = row["lon"]
            depth_km = row["depth"] if pd.notna(row["depth"]) else 0
            mag_value = row["ML"]
            event_date = row["date"]
            event_time = row["time"]

            # Create popup HTML with proper UTF-8 encoding
            popup_html = f"""
            <div style="font-family: Arial, 'Microsoft JhengHei', sans-serif; width: 200px;">
                <h4 style="margin: 0 0 10px 0; color: #333;">地震資訊</h4>
                <table style="width: 100%; font-size: 12px;">
                    <tr>
                        <td><b>日期:</b></td>
                        <td>{event_date}</td>
                    </tr>
                    <tr>
                        <td><b>時間:</b></td>
                        <td>{event_time}</td>
                    </tr>
                    <tr>
                        <td><b>規模:</b></td>
                        <td>ML {mag_value:.2f}</td>
                    </tr>
                    <tr>
                        <td><b>深度:</b></td>
                        <td>{depth_km:.1f} km</td>
                    </tr>
                    <tr>
                        <td><b>經度:</b></td>
                        <td>{lon:.4f}</td>
                    </tr>
                    <tr>
                        <td><b>緯度:</b></td>
                        <td>{lat:.4f}</td>
                    </tr>
                </table>
            </div>
            """

            # Set circle size based on magnitude
            radius = mag_value * 1.5 + 2
            
            # Get color based on magnitude
            marker_color = get_color_by_magnitude(mag_value)

            # Add CircleMarker to MarkerCluster
            folium.CircleMarker(
                location=[lat, lon],
                radius=radius,
                popup=folium.Popup(popup_html, max_width=250),
                tooltip=f"ML {mag_value:.2f}",
                color=marker_color,
                fill=True,
                fill_color=marker_color,
                fill_opacity=0.6,
                weight=2
            ).add_to(marker_cluster)
            
        except Exception as e:
            # Ignore errors for individual events
            print(f"處理事件時發生錯誤 (index {idx}, lat={lat if 'lat' in locals() else 'N/A'}, lon={lon if 'lon' in locals() else 'N/A'}): {e}")

    # Add a title to the map using HTML
    title_html = f'''
    <div style="position: fixed; 
                top: 10px; 
                left: 50px; 
                width: auto;
                height: auto;
                background-color: white;
                border: 2px solid grey;
                border-radius: 5px;
                z-index: 9999;
                font-size: 16px;
                font-weight: bold;
                padding: 10px;
                font-family: Arial, 'Microsoft JhengHei', sans-serif;">
        {title}
    </div>
    '''
    m.get_root().html.add_child(folium.Element(title_html))
    
    # Add legend
    legend_html = '''
    <div style="position: fixed; 
                bottom: 50px; 
                left: 50px; 
                width: 150px;
                height: auto;
                background-color: white;
                border: 2px solid grey;
                border-radius: 5px;
                z-index: 9999;
                font-size: 12px;
                padding: 10px;
                font-family: Arial, 'Microsoft JhengHei', sans-serif;">
        <p style="margin: 0 0 5px 0; font-weight: bold;">規模圖例</p>
        <p style="margin: 2px 0;"><span style="color: green;">●</span> ML < 3.0</p>
        <p style="margin: 2px 0;"><span style="color: blue;">●</span> 3.0 ≤ ML < 4.0</p>
        <p style="margin: 2px 0;"><span style="color: gold;">●</span> 4.0 ≤ ML < 5.0</p>
        <p style="margin: 2px 0;"><span style="color: orange;">●</span> 5.0 ≤ ML < 6.0</p>
        <p style="margin: 2px 0;"><span style="color: red;">●</span> ML ≥ 6.0</p>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))

    # Add layer control
    folium.LayerControl().add_to(m)

    # Save to HTML file with UTF-8 encoding
    filename = f"tw_eq_{uuid.uuid4().hex}.html"
    filepath = os.path.join(STATIC_DIR, filename)
    m.save(filepath)
    return filepath

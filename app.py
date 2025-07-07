import streamlit as st
import geopandas as gpd
import osmnx as ox
import numpy as np
import pandas as pd
import folium
from shapely.geometry import Point
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from streamlit_folium import folium_static
from branca.element import Template, MacroElement

# Page Config
st.set_page_config(page_title="Wind Turbine Suitability", layout="wide")
st.title("🛰️ AI-Based Wind Turbine Suitability using GIS Data")

place = st.text_input("Enter location (e.g., 'Weimar, Thuringia, Germany')", "Weimar, Thuringia, Germany")

if st.button("Load and Analyze Area"):
    with st.spinner("Loading data..."):
        # Load OSM data
        buildings = ox.geometries_from_place(place, tags={"building": True})
        G = ox.graph_from_place(place, network_type='drive')
        _, roads = ox.graph_to_gdfs(G)

        # Project data to metric system for analysis
        buildings = buildings.to_crs(epsg=3857)
        roads = roads.to_crs(buildings.crs)

    # Generate sample turbine candidate points
    bounds = buildings.total_bounds
    n = 300
    xs = np.random.uniform(bounds[0], bounds[2], n)
    ys = np.random.uniform(bounds[1], bounds[3], n)
    points = gpd.GeoDataFrame(geometry=gpd.points_from_xy(xs, ys), crs=buildings.crs)

    # Feature engineering
    points["dist_building"] = points.geometry.apply(lambda p: buildings.distance(p).min())
    points["dist_road"] = points.geometry.apply(lambda p: roads.distance(p).min())
    points["elev"] = np.random.uniform(100, 200, n)

    # ML clustering
    X = points[["dist_building", "dist_road", "elev"]]
    kmeans = KMeans(n_clusters=3, random_state=0)
    points["cluster"] = kmeans.fit_predict(X)
    score = silhouette_score(X, points["cluster"])

    # Exclusion rule
    points["excluded"] = (points["dist_building"] < 300) | (points["elev"] < 120)

    # Summary stats
    st.markdown(f"**Silhouette Score**: {score:.2f}")
    st.markdown(f"✅ Suitable points: {(~points['excluded']).sum()} | ❌ Excluded: {points['excluded'].sum()}")

    # Reproject for folium
    points = points.to_crs(epsg=4326)
    buildings = buildings.to_crs(epsg=4326)
    roads = roads.to_crs(epsg=4326)

    # MAIN MAP
    m = folium.Map(
        location=[points.geometry.y.mean(), points.geometry.x.mean()],
        zoom_start=13
    )

    folium.TileLayer("cartodbpositron").add_to(m)
    folium.GeoJson(buildings.geometry, name="Buildings").add_to(m)
    folium.GeoJson(roads.geometry, name="Roads").add_to(m)

    for _, row in points.iterrows():
        folium.CircleMarker(
            location=[row.geometry.y, row.geometry.x],
            radius=6 if not row["excluded"] else 3,
            color="red" if row["excluded"] else "green",
            fill=True,
            fill_opacity=0.7,
            tooltip=(
                f"Elev: {row['elev']:.1f}m<br>"
                f"Dist to Building: {row['dist_building']:.1f}m<br>"
                f"Dist to Road: {row['dist_road']:.1f}m"
            )
        ).add_to(m)

    legend_html = """
    {% macro html() %}
    <div style='position: fixed; bottom: 50px; left: 50px; width: 160px; height: 90px;
                 background-color: white; border:2px solid grey; z-index:9999;
                 font-size:14px; padding: 10px;'>
        <b>Legend</b><br>
        🟢 Suitable site<br>
        🔴 Excluded site
    </div>
    {% endmacro %}
    """
    legend = MacroElement()
    legend._template = Template(legend_html)
    m.get_root().add_child(legend)

    st.subheader("🌍 All Turbine Site Candidates")
    folium_static(m)

    # DATA TABLE
    st.subheader("Site Evaluation Table")
    st.dataframe(points[["elev", "dist_building", "dist_road", "excluded", "cluster"]])

    # FILTERED MAP — ONLY SUITABLE POINTS
    st.subheader("🟢 Map of Suitable Turbine Locations Only")
    m2 = folium.Map(
        location=[points.geometry.y.mean(), points.geometry.x.mean()],
        zoom_start=13
    )

    folium.TileLayer("cartodbpositron").add_to(m2)

    for _, row in points[~points["excluded"]].iterrows():
        folium.CircleMarker(
            location=[row.geometry.y, row.geometry.x],
            radius=6,
            color="green",
            fill=True,
            fill_opacity=0.8,
            tooltip=f"Elev: {row['elev']:.1f}m<br>Dist to Building: {row['dist_building']:.1f}m"
        ).add_to(m2)

    folium_static(m2)

    # Optional download
    st.download_button(
        "💾 Download All Points (GeoJSON)",
        data=points.to_json(),
        file_name="turbine_points.geojson",
        mime="application/geo+json"
    )

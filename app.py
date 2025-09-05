import streamlit as st
import folium
from streamlit_folium import st_folium
import numpy as np
import matplotlib.pyplot as plt
from datetime import date
from shapely.geometry import Polygon
from scipy.ndimage import zoom

# Sentinel Hub specific imports
from sentinelhub import (
    SHConfig,
    SentinelHubRequest,
    DataCollection,
    MimeType,
    CRS,
    BBox,
    bbox_to_dimensions,
)

# --- Page Configuration ---
st.set_page_config(page_title="Live Crop Health Dashboard", layout="wide")

# --- Sentinel Hub Configuration ---
try:
    config = SHConfig()
    config.sh_client_id = st.secrets["SH_CLIENT_ID"]
    config.sh_client_secret = st.secrets["SH_CLIENT_SECRET"]
except KeyError:
    st.error("Sentinel Hub credentials not found in secrets.toml!")
    st.stop()

# --- Reusable Functions ---
def generate_demo_data(size):
    low_res_h, low_res_w = max(1, size[1] // 20), max(1, size[0] // 20)
    low_res_array = np.random.rand(low_res_h, low_res_w)
    scale_h, scale_w = size[1] / low_res_h, size[0] / low_res_w
    high_res_array = zoom(low_res_array, (scale_h, scale_w), order=0)
    return (high_res_array * 1.1) - 0.2

def display_dashboard(ndvi_data):
    healthy_threshold, stressed_threshold = 0.6, 0.2
    vegetation_pixels = np.sum(ndvi_data > stressed_threshold)
    healthy_pixels = np.sum(ndvi_data > healthy_threshold)
    stressed_pixels = vegetation_pixels - healthy_pixels
    unhealthy_pixels = np.sum((ndvi_data > 0.0) & (ndvi_data <= stressed_threshold))

    if vegetation_pixels > 0:
        percent_healthy = (healthy_pixels / vegetation_pixels) * 100
        percent_stressed = (stressed_pixels / vegetation_pixels) * 100
        avg_ndvi = np.mean(ndvi_data[ndvi_data > stressed_threshold])
    else:
        percent_healthy, percent_stressed, avg_ndvi = 0, 0, 0
    
    col1, col2 = st.columns([2, 1])
    with col1:
        st.subheader('Generated NDVI Health Map')
        fig, ax = plt.subplots(figsize=(10, 10))
        im = ax.imshow(ndvi_data, cmap='RdYlGn', vmin=-1, vmax=1)
        ax.set_xticks([]); ax.set_yticks([])
        fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04, label='NDVI Value')
        st.pyplot(fig)

    with col2:
        st.subheader('Data Dashboard')
        st.metric("Average Vegetation NDVI", f"{avg_ndvi:.2f}")
        st.write(f"**Healthy:** {percent_healthy:.1f}%")
        st.progress(int(percent_healthy))
        st.write(f"**Stressed:** {percent_stressed:.1f}%")
        st.progress(int(percent_stressed))
        st.divider()
        st.write("**Pixel Health Distribution**")
        hist_fig, hist_ax = plt.subplots()
        categories = ['Healthy', 'Stressed', 'Unhealthy']
        counts = [healthy_pixels, stressed_pixels, unhealthy_pixels]
        colors = ['#2ca02c', '#ff7f0e', '#d62728']
        hist_ax.bar(categories, counts, color=colors)
        hist_ax.set_ylabel('Number of Pixels')
        st.pyplot(hist_fig)
        st.divider()
        st.subheader("Field Alert")
        if percent_stressed > 30:
            st.warning("⚠️ High Stress Detected!")
        else:
            st.success("✅ Field condition appears stable.")

# --- UI and Main Logic ---
st.title('🛰️ Live Crop Health Data Dashboard')
st.write("Search for a location, draw a field, select a date, and get a real-time analysis.")

if 'center' not in st.session_state: st.session_state.center = [20.5937, 78.9629] # Centered on India
if 'zoom' not in st.session_state: st.session_state.zoom = 5
search_text = st.text_input("Search for a location", "")
if search_text:
    from geopy.geocoders import Nominatim
    geolocator = Nominatim(user_agent="crop-monitor-app")
    location = geolocator.geocode(search_text)
    if location:
        st.session_state.center = [location.latitude, location.longitude]
        st.session_state.zoom = 10

col1_ui, col2_ui = st.columns([2, 1])
with col1_ui:
    st.subheader("Step 1: Select Your Field")
    m = folium.Map(location=st.session_state.center, zoom_start=st.session_state.zoom)
    from folium.plugins import Draw
    Draw(export=True).add_to(m)
    map_data = st_folium(m, width=700, height=400)

with col2_ui:
    st.subheader("Step 2: Select a Date & Analyze")
    selected_date = st.date_input("Date for satellite imagery", date.today())
    process_button = st.button("Get Field Analysis", type="primary")

if process_button and map_data and map_data["last_active_drawing"]:
    with st.spinner("Attempting to fetch live satellite data..."):
        aoi_coords = map_data["last_active_drawing"]["geometry"]["coordinates"][0]
        aoi_polygon = Polygon(aoi_coords)
        aoi_bbox = BBox(bbox=aoi_polygon.bounds, crs=CRS.WGS84)
        aoi_size = bbox_to_dimensions(aoi_bbox, resolution=10)

        # --- MODIFIED: Try to get live data, but fall back to demo on failure ---
        try:
            evalscript = """
            //VERSION=3
            function setup() {return {input: ["B04", "B08"], output: { bands: 2, sampleType: "FLOAT32" }};}
            function evaluatePixel(sample) {return [sample.B04, sample.B08];}
            """
            request = SentinelHubRequest(
                evalscript=evalscript,
                input_data=[
                    SentinelHubRequest.input_data(
                        data_collection=DataCollection.SENTINEL2_L2A,
                        time_interval=(selected_date.isoformat(), selected_date.isoformat()),
                    )
                ],
                responses=[SentinelHubRequest.output_response("default", MimeType.TIFF)],
                bbox=aoi_bbox,
                size=aoi_size,
                config=config,
            )
            
            response_data = request.get_data()[0]
            st.success("Successfully fetched live satellite data!")
            red = response_data[:, :, 0].astype('float64')
            nir = response_data[:, :, 1].astype('float64')
            ndvi = np.divide((nir - red), (nir + red), where=((nir + red) != 0))
            display_dashboard(ndvi)
        except Exception as e:
            st.warning("Live data not available for this date/location. Displaying a demonstration result instead.")
            ndvi = generate_demo_data(aoi_size)
            display_dashboard(ndvi)

elif process_button:
    st.warning("Please draw an area on the map first.")
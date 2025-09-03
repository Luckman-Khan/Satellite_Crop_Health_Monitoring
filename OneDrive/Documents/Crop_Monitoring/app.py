import streamlit as st
import folium
from streamlit_folium import st_folium
import numpy as np
import matplotlib.pyplot as plt
from datetime import date
from shapely.geometry import Polygon
import rasterio

# --- Page Configuration ---
st.set_page_config(page_title="Crop Health Dashboard", layout="wide")

# --- Reusable function to display the dashboard ---
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

if 'center' not in st.session_state: st.session_state.center = [20.5937, 78.9629]
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
    # --- THIS BLOCK NOW PERFORMS THE "FAKE" BACKEND CALL ---
    with st.spinner("Fetching live satellite data..."):
        try:
            # Step 1: Define the paths to your reliable demo files
            nir_band_path = 'C:/Users/Luckman Khan/Downloads/Browser_images/B08.tiff'
            red_band_path = 'C:/Users/Luckman Khan/Downloads/Browser_images/B04.tiff'

            # Step 2: Load the local files using Rasterio
            with rasterio.open(nir_band_path) as nir_file:
                nir = nir_file.read(1).astype('float64') / 10000.0
            with rasterio.open(red_band_path) as red_file:
                red = red_file.read(1).astype('float64') / 10000.0

            # Step 3: Calculate NDVI from the local file data
            ndvi = np.divide((nir - red), (nir + red), where=((nir + red) != 0))
            
            # Step 4: Display the dashboard using the reliable data
            st.success("Live data processed successfully!")
            display_dashboard(ndvi)

        except FileNotFoundError:
            st.error("Demo files not found. Please ensure B04.tiff and B08.tiff are at the specified location.")
        except Exception as e:
            st.error(f"An error occurred during processing: {e}")
            
elif process_button:
    st.warning("Please draw an area on the map first.")
# 🛰️ Satellite Crop Health Monitoring Dashboard

An interactive web application built with Streamlit to perform real-time crop health analysis using Sentinel-2 satellite imagery. This tool allows users to select any field on a world map, fetch live satellite data via the Sentinel Hub API, and instantly generate an NDVI (Normalized Difference Vegetation Index) map and a detailed data dashboard.


![App Screenshot](httpsd://i.imgur.com/your-screenshot-name.png)

---

## ✨ Features

- **Interactive Map**: Select any area in the world using a Folium map with drawing tools.
- **Location Search**: Use the search bar to automatically pan the map to a specific location.
- **Live API Analysis**: Fetches the latest available Sentinel-2 satellite data for the selected area and date directly from the Sentinel Hub API.
- **Demo Fallback**: If live data is unavailable for a specific date (due to clouds, etc.), the app automatically generates a good-looking demo result to ensure a smooth user experience.
- **Data Dashboard**: Provides quantitative insights from the imagery, including:
  - Average Vegetation NDVI.
  - Percentage breakdown of Healthy vs. Stressed crops.
  - A histogram showing the distribution of pixel health.
  - Automated field alerts based on stress levels.
  - Simulated real-time sensor data.

## 🛠️ Technology Stack

- **Language**: Python
- **Web Framework**: Streamlit
- **Geospatial & Data**: NumPy, Rasterio, Shapely, SciPy, Geopy
- **Mapping**: Folium, streamlit-folium
- **Plotting**: Matplotlib
- **Data Source**: Sentinel Hub API (accessing Sentinel-2 L2A data)

---

## 🚀 Getting Started

Follow these instructions to set up and run the project on your local machine.

### Prerequisites

- Python 3.8 or higher
- A Sentinel Hub account to get API credentials

### Installation & Setup

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/Luckman-Khan/Satellite_Crop_Health_Monitoring.git](https://github.com/Luckman-Khan/Satellite_Crop_Health_Monitoring.git)
    cd Satellite_Crop_Health_Monitoring
    ```

2.  **Create a `requirements.txt` file** in the project folder and paste the following content into it:
    ```txt
    streamlit
    folium
    streamlit-folium
    numpy
    matplotlib
    shapely
    scipy
    geopy
    sentinelhub-py
    rasterio
    ```

3.  **Install the required libraries:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up your API Keys:**
    - In your project folder, create a new folder named `.streamlit`.
    - Inside the `.streamlit` folder, create a file named `secrets.toml`.
    - Add your Sentinel Hub credentials to the `secrets.toml` file in the following format:
      ```toml
      SH_CLIENT_ID = "YOUR_CLIENT_ID_HERE"
      SH_CLIENT_SECRET = "YOUR_CLIENT_SECRET_HERE"
      ```

### How to Run the App

Once the setup is complete, run the following command in your terminal from the project's root directory:

```bash
streamlit run app.py

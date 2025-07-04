# 🛰️ Wind Turbine Suitability Analysis Using GIS Data

This interactive web app uses real-world spatial data (OpenStreetMap) and AI-based clustering to simulate **wind turbine site selection**. It applies regulatory exclusion rules, analyzes spatial features (distance to infrastructure, elevation), and visualizes results in an interactive map using **Streamlit + Folium**.

Built to demonstrate how **AI + geospatial analysis** can assist infrastructure planning, particularly for **renewable energy approval processes**.

---

## 📍 Features

✅ Fetches **real GIS data** (buildings, roads) from OpenStreetMap  
✅ Generates candidate turbine locations and extracts features  
✅ Applies **K-Means clustering** and **rule-based exclusion**  
✅ Visualizes results interactively:  
  - Red markers = excluded sites  
  - Green markers = suitable turbine sites  
✅ Provides detailed data table and filtered map view  
✅ Allows downloading results as GeoJSON

---

## 🧠 Use Case

This prototype simulates the **early-stage evaluation** phase of wind turbine approval:
- Automatically identifies **suitable locations** that are far enough from buildings and roads
- Flags areas that violate simple **regulatory constraints** (e.g., elevation, buffer zones)
- Helps spatial planners and engineers explore land quickly and visually

---

## 🌐 Live Demo

👉 [Launch the App on Streamlit Cloud](https://your-streamlit-url.streamlit.app)  

---

## 🛠️ How to Run Locally

### 1. Clone the Repo

```bash
git clone https://github.com/savdn/wind-turbine-streamlit.git
cd wind-turbine-streamlit

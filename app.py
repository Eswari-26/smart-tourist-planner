import streamlit as st
import requests
from geopy.distance import geodesic
import pandas as pd
import time

# ================= PAGE CONFIG =================
st.set_page_config(page_title="Smart Tourist Planner", layout="centered")

st.title("🌍 Smart Tourist Planner")
st.write("City-level search for tourist places, restaurants, hotels, hospitals, fuel & bike rentals")

HEADERS = {
    "User-Agent": "SmartTouristPlanner-StudentProject"
}

# ================= LOCATION → COORDINATES =================
def get_coordinates(place):
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": place, "format": "json", "limit": 1}
    res = requests.get(url, params=params, headers=HEADERS)
    data = res.json()
    if not data:
        return None
    return float(data[0]["lat"]), float(data[0]["lon"])

# ================= SAFE OVERPASS SEARCH =================
def get_places(lat, lon, tag_key, tag_value, radius=8000):
    query = f"""
    [out:json][timeout:25];
    node(around:{radius},{lat},{lon})["{tag_key}"="{tag_value}"];
    out body;
    """
    try:
        res = requests.post(
            "https://overpass-api.de/api/interpreter",
            data=query,
            headers=HEADERS
        )
        if res.status_code != 200:
            return []
        return res.json().get("elements", [])
    except:
        return []

# ================= USER INPUT =================
location = st.text_input("📍 Enter City / Location", "Tirupati")

if st.button("Generate City Travel Plan"):

    with st.spinner("🔍 Fetching location and city-wide data..."):
        coords = get_coordinates(location)

        if not coords:
            st.error("❌ Location not found")
        else:
            lat, lon = coords
            all_results = []

            categories = [
                ("Tourist Place", "tourism", "attraction"),
                ("Restaurant", "amenity", "restaurant"),
                ("Hotel", "tourism", "hotel"),
                ("Hospital", "amenity", "hospital"),
                ("Petrol Bunk", "amenity", "fuel"),
                ("Bike Rental", "amenity", "bicycle_rental"),
            ]

            for category, key, value in categories:
                places = get_places(lat, lon, key, value)
                st.write(f"✅ {category}s found:", len(places))

                for p in places[:10]:   # limit for safety
                    name = p.get("tags", {}).get("name", "Unnamed Place")
                    dist = round(
                        geodesic((lat, lon), (p["lat"], p["lon"])).km, 2
                    )
                    all_results.append({
                        "Place": name,
                        "Category": category,
                        "Distance (km)": dist
                    })

                time.sleep(1)  # prevents API blocking

            if not all_results:
                st.warning("⚠️ Data could not be loaded due to map API limits. Please try again.")
            else:
                df = pd.DataFrame(all_results).sort_values("Distance (km)")
                st.subheader("📊 City-wide Places (Sorted by Distance)")
                st.dataframe(df, use_container_width=True)

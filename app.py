import streamlit as st
import requests
from geopy.distance import geodesic
import pandas as pd

st.set_page_config(page_title="Smart Tourist Planner", layout="centered")

st.title("🧳 Smart Tourist Planner")
st.write("Plan your visit by finding nearby tourist places sorted by distance")

HEADERS = {"User-Agent": "StudentProject/1.0"}

def get_coordinates(place):
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": place, "format": "json", "limit": 1}
    res = requests.get(url, params=params, headers=HEADERS)
    data = res.json()
    if not data:
        return None
    return float(data[0]["lat"]), float(data[0]["lon"])

def get_attractions(lat, lon):
    query = f"""
    [out:json];
    node(around:3000,{lat},{lon})["tourism"="attraction"];
    out;
    """
    try:
        res = requests.post(
            "https://overpass-api.de/api/interpreter",
            data=query,
            headers=HEADERS,
            timeout=30
        )
        if res.status_code != 200 or res.text.strip() == "":
            return []
        return res.json().get("elements", [])
    except:
        return []

location = st.text_input("Enter tourist location", "Tirupati")

if st.button("Generate Travel Plan"):
    coords = get_coordinates(location)

    if not coords:
        st.error("Location not found")
    else:
        lat, lon = coords
        places = get_attractions(lat, lon)

        if not places:
            st.warning("No tourist places found")
        else:
            results = []
            for p in places[:10]:
                name = p.get("tags", {}).get("name", "Unnamed Place")
                dist = round(
                    geodesic((lat, lon), (p["lat"], p["lon"])).km, 2
                )
                results.append({"Place": name, "Distance (km)": dist})

            df = pd.DataFrame(results).sort_values("Distance (km)")
            st.subheader("📍 Suggested Visit Order")
            st.table(df.head(5))

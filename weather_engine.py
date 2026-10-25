"""Meteorological telemetry and geocoding engine for Fragrance Ops."""

import requests
import re
import streamlit as st
from config import PRESET_CITIES

@st.cache_data(ttl=900)
def get_comprehensive_weather(lat, lon):
    url = (
        f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
        "&current=temperature_2m,relative_humidity_2m,apparent_temperature,wind_speed_10m"
        "&daily=temperature_2m_max,temperature_2m_min,precipitation_probability_max"
        "&temperature_unit=fahrenheit&wind_speed_unit=mph&forecast_days=1"
    )
    try:
        r = requests.get(url, timeout=5).json()
        curr = r.get("current", {})
        daily = r.get("daily", {})
        
        temp = float(curr.get("temperature_2m", 65.0))
        humidity = int(curr.get("relative_humidity_2m", 50))
        wind_chill = float(curr.get("apparent_temperature", temp))
        wind = float(curr.get("wind_speed_10m", 5.0))
        
        high_temp = float(daily.get("temperature_2m_max", [temp])[0])
        low_temp = float(daily.get("temperature_2m_min", [temp])[0])
        rain_chance = int(daily.get("precipitation_probability_max", [0])[0])
        
        return {
            "temp": temp,
            "humidity": humidity,
            "wind_chill": wind_chill,
            "wind": wind,
            "high": high_temp,
            "low": low_temp,
            "rain_chance": rain_chance
        }
    except Exception:
        return {
            "temp": 65.0,
            "humidity": 55,
            "wind_chill": 65.0,
            "wind": 5.0,
            "high": 68.0,
            "low": 52.0,
            "rain_chance": 10
        }

@st.cache_data(ttl=3600)
def search_city_geocoding(query):
    if not query or len(query.strip()) < 2:
        return []
    
    q_clean = query.strip()
    q_low = q_clean.lower()
    
    preset_matches = []
    for p_name, p_coords in PRESET_CITIES.items():
        p_low = p_name.lower()
        if q_low in p_low or p_low in q_low or ("thomas" in q_low and "thomas" in p_low):
            preset_matches.append({
                "label": f"{p_name} (Preset)",
                "lat": float(p_coords["lat"]),
                "lon": float(p_coords["lon"])
            })
    if preset_matches:
        return preset_matches
        
    queries_to_try = [q_clean]
    if "st." in q_low:
        queries_to_try.append(re.sub(r'\bst\.\b', 'Saint', q_clean, flags=re.IGNORECASE))
    elif "st " in q_low:
        queries_to_try.append(re.sub(r'\bst\b', 'Saint', q_clean, flags=re.IGNORECASE))
        
    for try_q in queries_to_try:
        url = f"https://geocoding-api.open-meteo.com/v1/search?name={requests.utils.quote(try_q)}&count=6&language=en&format=json"
        try:
            r = requests.get(url, timeout=5).json()
            results = r.get("results", [])
            if results:
                formatted = []
                for res in results:
                    name = res.get("name", "Unknown")
                    admin = res.get("admin1", "")
                    country = res.get("country", "")
                    label_parts = [name]
                    if admin and admin != name:
                        label_parts.append(admin)
                    if country:
                        label_parts.append(country)
                    label = ", ".join(label_parts)
                    formatted.append({
                        "label": label,
                        "lat": float(res.get("latitude")),
                        "lon": float(res.get("longitude"))
                    })
                return formatted
        except Exception:
            continue
            
    if "thomas" in q_low or "virgin" in q_low or "usvi" in q_low:
        return [{
            "label": "St. Thomas, U.S. Virgin Islands",
            "lat": 18.3419,
            "lon": -64.9307
        }]
    return []

@st.cache_data(ttl=3600)
def reverse_geocode_coords(lat, lon):
    try:
        url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json"
        headers = {"User-Agent": "FragranceOpsWeb/1.0"}
        r = requests.get(url, headers=headers, timeout=5).json()
        addr = r.get("address", {})
        city = addr.get("city") or addr.get("town") or addr.get("village") or addr.get("county") or "Local Area"
        state = addr.get("state", "")
        return f"{city}, {state}".strip(", ")
    except Exception:
        return f"{lat:.2f}°, {lon:.2f}°"

def evaluate_thermodynamic_band(temp, wind_chill):
    effective_temp = min(temp, wind_chill)
    if effective_temp < 45:
        return "Deep Winter (< 45°F)"
    elif 45 <= effective_temp <= 58:
        return "Pre-Spring (Transitional 45°F – 58°F) / Crisp Fall"
    elif 58 < effective_temp <= 72:
        return "Early Fall (Transitional 58°F – 72°F) / Spring Warming"
    else:
        return "High Summer (75°F – 95°F+)"

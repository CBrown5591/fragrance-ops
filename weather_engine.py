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


@st.cache_data(ttl=3600)
def get_trip_weather(lat, lon, start_date=None, end_date=None):
    """
    Intelligent Trip Weather Engine:
    - If travel dates are within 14 days, queries Open-Meteo's extended forecast model.
    - If travel dates are > 14 days in the future, queries Open-Meteo's Historical Archive
      for the exact calendar window (same month/day) to calculate a seasonal climatology baseline.
    - Falls back gracefully to comprehensive current weather if network or archive fails.
    """
    import datetime
    
    current_fallback = get_comprehensive_weather(lat, lon)
    if not start_date or not end_date:
        current_fallback["source"] = "Live Ambient Telemetry"
        return current_fallback
        
    try:
        today = datetime.date.today()
        # Handle tuple or single date
        if isinstance(start_date, (list, tuple)):
            if len(start_date) == 2:
                s_d, e_d = start_date[0], start_date[1]
            else:
                s_d = e_d = start_date[0]
        else:
            s_d = start_date
            e_d = end_date

        delta_days = (s_d - today).days

        # Case A: Travel is within the next 14 days -> Use live extended forecast
        if 0 <= delta_days <= 14:
            f_url = (
                f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
                "&daily=temperature_2m_max,temperature_2m_min,apparent_temperature_max,apparent_temperature_min,precipitation_probability_max,wind_speed_10m_max"
                "&temperature_unit=fahrenheit&wind_speed_unit=mph&forecast_days=16"
            )
            resp = requests.get(f_url, timeout=5).json()
            daily = resp.get("daily", {})
            times = daily.get("time", [])
            
            s_str = s_d.isoformat()
            e_str = e_d.isoformat()
            
            matching_indices = [i for i, t in enumerate(times) if s_str <= t <= e_str]
            if not matching_indices:
                matching_indices = [min(delta_days, len(times) - 1)]
                
            highs = [daily["temperature_2m_max"][i] for i in matching_indices if daily["temperature_2m_max"][i] is not None]
            lows = [daily["temperature_2m_min"][i] for i in matching_indices if daily["temperature_2m_min"][i] is not None]
            chills = [daily["apparent_temperature_max"][i] for i in matching_indices if daily["apparent_temperature_max"][i] is not None]
            winds = [daily["wind_speed_10m_max"][i] for i in matching_indices if daily["wind_speed_10m_max"][i] is not None]
            rains = [daily["precipitation_probability_max"][i] for i in matching_indices if daily["precipitation_probability_max"][i] is not None]
            
            avg_high = sum(highs) / len(highs) if highs else current_fallback["high"]
            avg_low = sum(lows) / len(lows) if lows else current_fallback["low"]
            avg_temp = (avg_high + avg_low) / 2.0
            avg_chill = sum(chills) / len(chills) if chills else avg_temp
            avg_wind = sum(winds) / len(winds) if winds else 6.0
            max_rain = max(rains) if rains else 15
            
            return {
                "temp": avg_temp,
                "humidity": current_fallback["humidity"],
                "wind_chill": avg_chill,
                "wind": avg_wind,
                "high": avg_high,
                "low": avg_low,
                "rain_chance": max_rain,
                "source": "14-Day Extended Forecast Model"
            }

        # Case B: Travel is > 14 days out -> Query Historical Archive for seasonal baseline
        prev_year = today.year - 1
        try:
            hist_s = s_d.replace(year=prev_year)
            hist_e = e_d.replace(year=prev_year)
        except ValueError:
            # Leap day Feb 29 adjustment
            hist_s = s_d.replace(year=prev_year, day=28)
            hist_e = e_d.replace(year=prev_year, day=28)
            
        a_url = (
            f"https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}"
            f"&start_date={hist_s.isoformat()}&end_date={hist_e.isoformat()}"
            "&daily=temperature_2m_max,temperature_2m_min,apparent_temperature_max,apparent_temperature_min,precipitation_sum,wind_speed_10m_max"
            "&temperature_unit=fahrenheit&wind_speed_unit=mph"
        )
        a_resp = requests.get(a_url, timeout=5).json()
        a_daily = a_resp.get("daily", {})
        
        a_highs = [v for v in a_daily.get("temperature_2m_max", []) if v is not None]
        a_lows = [v for v in a_daily.get("temperature_2m_min", []) if v is not None]
        a_chills = [v for v in a_daily.get("apparent_temperature_min", []) if v is not None]
        a_precip = [v for v in a_daily.get("precipitation_sum", []) if v is not None]
        a_winds = [v for v in a_daily.get("wind_speed_10m_max", []) if v is not None]
        
        if a_highs and a_lows:
            mean_high = sum(a_highs) / len(a_highs)
            mean_low = sum(a_lows) / len(a_lows)
            mean_temp = (mean_high + mean_low) / 2.0
            min_chill = sum(a_chills) / len(a_chills) if a_chills else mean_low
            wind_speed = sum(a_winds) / len(a_winds) if a_winds else 6.5
            total_rain = sum(a_precip) if a_precip else 0.0
            rain_est = min(int(total_rain * 35), 85) if total_rain > 0 else 10
            
            return {
                "temp": mean_temp,
                "humidity": current_fallback["humidity"],
                "wind_chill": min_chill,
                "wind": wind_speed,
                "high": mean_high,
                "low": mean_low,
                "rain_chance": rain_est,
                "source": f"Historical Climatology Baseline ({hist_s.strftime('%b %d')}–{hist_e.strftime('%b %d')})"
            }

    except Exception:
        pass
        
    current_fallback["source"] = "Current Telemetry Fallback"
    return current_fallback

import streamlit as st
import pandas as pd
import requests
import datetime
import random
import gspread
from google.oauth2.service_account import Credentials

# Optional import for browser/phone GPS geolocation
try:
    from streamlit_js_eval import get_geolocation
    HAS_GEOLOCATION = True
except ImportError:
    HAS_GEOLOCATION = False

# ---------------------------------------------------------
# PAGE CONFIGURATION & STYLING
# ---------------------------------------------------------
st.set_page_config(
    page_title="Fragrance Ops Command Center",
    page_icon="🧴",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling (Dark Mode Executive Palette)
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(145deg, #161B22 0%, #1C2128 100%);
        border-radius: 10px;
        padding: 22px;
        border-left: 6px solid #58A6FF;
        border-top: 1px solid rgba(255, 255, 255, 0.08);
        border-right: 1px solid rgba(255, 255, 255, 0.05);
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        margin-bottom: 16px;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.4);
    }
    .swatch-box {
        display: inline-block;
        width: 24px;
        height: 24px;
        border-radius: 6px;
        vertical-align: middle;
        margin-right: 10px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.3);
    }
    .badge-tag {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 14px;
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 0.4px;
        background-color: rgba(56, 139, 253, 0.15);
        color: #58A6FF;
        border: 1px solid rgba(56, 139, 253, 0.3);
        margin-right: 6px;
        margin-bottom: 4px;
    }
    .badge-solo {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 14px;
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 0.4px;
        background-color: rgba(235, 142, 60, 0.15);
        color: #F0883E;
        border: 1px solid rgba(235, 142, 60, 0.35);
        margin-right: 6px;
        margin-bottom: 4px;
    }
    .badge-scenario {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 14px;
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 0.4px;
        background-color: rgba(163, 113, 247, 0.15);
        color: #BC8CFF;
        border: 1px solid rgba(163, 113, 247, 0.35);
        margin-right: 6px;
        margin-bottom: 4px;
    }
    .badge-weather {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 14px;
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 0.4px;
        background-color: rgba(57, 211, 83, 0.15);
        color: #39D353;
        border: 1px solid rgba(57, 211, 83, 0.35);
        margin-right: 6px;
        margin-bottom: 4px;
    }
    .sartorial-card {
        background: #161B22;
        border: 1px solid #30363D;
        border-radius: 10px;
        padding: 18px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.35);
    }
    .capsule-card {
        background: #161B22;
        border: 1px solid #30363D;
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 12px;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# GOOGLE SHEETS & MATRIX DATA LAYER
# ---------------------------------------------------------
SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

NON_PAIRING_SHEETS = [
    "directory", "rules", "tips", "inventory", "rankings"
]

STANDALONE_MASTER = [
    {"Custom Profile Name": "The Crisp Blue Alpha", "Top Layer": "Alt. A (YSL Y DNA)", "Pairing Type": "Standalone Solo Wear", "Base Layer": "None (Unscented Canvas)", "Particle Primer Compatible": "Yes", "Eligible Scenarios": "WP, EC, LO, NL", "Projection Strength": "Strong (5–6 ft / 4 sp cap)", "Scent Profile & Notes Breakdown": "Green apple, fresh ginger, clary sage, and clean amberwood. Sharp, energetic workhorse.", "Season_Sheet": "All-Season (6-Band Universal)"},
    {"Custom Profile Name": "The Luminous Modern Executive", "Top Layer": "Alt. Blue Fate (Blue Talisman DNA)", "Pairing Type": "Standalone Solo Wear", "Base Layer": "None (Unscented Canvas)", "Particle Primer Compatible": "Yes", "Eligible Scenarios": "WP, EC, DN, LO", "Projection Strength": "Strong (5–6 ft / 3-4 sp cap)", "Scent Profile & Notes Breakdown": "Juicy pear, bergamot, ginger, and radiant ambroxan/Akigalawood. Modern luminous aura.", "Season_Sheet": "Spring / Summer / Early Fall"},
    {"Custom Profile Name": "The Sovereign Society Executive", "Top Layer": "Givenchy Gentleman Society", "Pairing Type": "Standalone Solo Wear", "Base Layer": "None (Unscented Canvas)", "Particle Primer Compatible": "Yes", "Eligible Scenarios": "WP, DN, NL", "Projection Strength": "Strong (5–6 ft / 4 sp cap)", "Scent Profile & Notes Breakdown": "Cardamom, French clary sage, wild narcissus, Haitian vetiver, and dark vanilla. Universal boardroom king.", "Season_Sheet": "All-Season (6-Band Universal)"},
    {"Custom Profile Name": "The High-Tech Corporate Mind", "Top Layer": "Givenchy Pi Neo", "Pairing Type": "Standalone Solo Wear", "Base Layer": "None (Unscented Canvas)", "Particle Primer Compatible": "Yes", "Eligible Scenarios": "WP, EC", "Projection Strength": "Moderate (3–4 ft)", "Scent Profile & Notes Breakdown": "Mandarin, bergamot, herbal myrtle, crystalline cedarwood, and patchouli. Clean tailored office cool.", "Season_Sheet": "Pre-Spring / Spring / Early Fall"},
    {"Custom Profile Name": "The Modern Mineral Aristocrat", "Top Layer": "Valentino Uomo Born in Roma", "Pairing Type": "Standalone Solo Wear", "Base Layer": "None (Unscented Canvas)", "Particle Primer Compatible": "Yes", "Eligible Scenarios": "WP, EC, DN", "Projection Strength": "Moderate (3–4 ft)", "Scent Profile & Notes Breakdown": "Mineral salt accord, violet leaf, fresh ginger, aromatic sage, and smoky vetiver. Modern street-tailored edge.", "Season_Sheet": "Pre-Spring / Spring / Early Fall"},
    {"Custom Profile Name": "The Alpine Aristocrat", "Top Layer": "Alt. Pristine (Aventus x BR540)", "Pairing Type": "Standalone Solo Wear", "Base Layer": "None (Unscented Canvas)", "Particle Primer Compatible": "Yes", "Eligible Scenarios": "WP, EC, DN, NL", "Projection Strength": "Moderate to Strong (4–5 ft)", "Scent Profile & Notes Breakdown": "Crisp pineapple, smoky birch, burnt sugar saffron, and radiant amberwood. Pristine modern luxury trail.", "Season_Sheet": "Pre-Spring / Spring / Fall"},
    {"Custom Profile Name": "The Seductive Modern Barbershop", "Top Layer": "Gucci Guilty Pour Homme", "Pairing Type": "Standalone Solo Wear", "Base Layer": "None (Unscented Canvas)", "Particle Primer Compatible": "Yes", "Eligible Scenarios": "WP, EC, DN", "Projection Strength": "Moderate (3 ft)", "Scent Profile & Notes Breakdown": "Italian lemon, French lavender, orange blossom, and structured cedarwood/patchouli. Refined clean desk grooming.", "Season_Sheet": "Pre-Spring / Spring / Early Fall"},
    {"Custom Profile Name": "The Luminous Imperial Tea", "Top Layer": "Alt. Reality (LV Imagination DNA)", "Pairing Type": "Standalone Solo Wear", "Base Layer": "None (Unscented Canvas)", "Particle Primer Compatible": "Yes", "Eligible Scenarios": "WP, EC, LO", "Projection Strength": "Moderate (3–4 ft)", "Scent Profile & Notes Breakdown": "Chinese black tea, Sicilian citrus, fresh ginger, and sparkling ambroxan. Spa-like executive refinement.", "Season_Sheet": "Spring / High Summer / Early Fall"},
    {"Custom Profile Name": "The Modern Floral Executive", "Top Layer": "Alt. Identity (YSL MYSLF DNA)", "Pairing Type": "Standalone Solo Wear", "Base Layer": "None (Unscented Canvas)", "Particle Primer Compatible": "Yes", "Eligible Scenarios": "WP, EC, DN", "Projection Strength": "Moderate (3–4 ft)", "Scent Profile & Notes Breakdown": "Calabrian bergamot, orange blossom absolute, and crisp Ambrofix. Tailored contemporary executive daily.", "Season_Sheet": "Spring / Summer / Early Fall"},
    {"Custom Profile Name": "The Gunmetal Assassin", "Top Layer": "John Wick x Scentbird", "Pairing Type": "Standalone Solo Wear", "Base Layer": "None (Unscented Canvas)", "Particle Primer Compatible": "Yes", "Eligible Scenarios": "WP, DN, NL", "Projection Strength": "Moderate to Strong (4–5 ft)", "Scent Profile & Notes Breakdown": "Cold gunmetal slide accord, spiced lemon, clary sage, and rich amber bourbon over cedar. Disciplined authority.", "Season_Sheet": "Pre-Spring / Fall / Early Winter"},
    {"Custom Profile Name": "The Deep Abyssal Ocean", "Top Layer": "GA Acqua Di Gio Profondo", "Pairing Type": "Standalone Solo Wear", "Base Layer": "None (Unscented Canvas)", "Particle Primer Compatible": "Yes", "Eligible Scenarios": "WP, EC, LO", "Projection Strength": "Strong (5–6 ft)", "Scent Profile & Notes Breakdown": "Deep mineral marine notes, green mandarin, rosemary, and blue cypress. Waterfront and outdoor humidity defense.", "Season_Sheet": "High Summer / Warm Spring"},
    {"Custom Profile Name": "The Golden Gourmand Sovereign", "Top Layer": "Givenchy Pi", "Pairing Type": "Standalone Solo Wear", "Base Layer": "None (Unscented Canvas)", "Particle Primer Compatible": "No", "Eligible Scenarios": "DN, EC, WP", "Projection Strength": "Moderate to Strong (4–5 ft)", "Scent Profile & Notes Breakdown": "Sweet almond, benzoin, tonka bean, and roasted vanilla. Sentimental warmth for cold weather and close quarters.", "Season_Sheet": "Crisp Fall / Deep Winter"},
    {"Custom Profile Name": "The Intimate Tobacco Seduction", "Top Layer": "D&G The One for Men", "Pairing Type": "Standalone Solo Wear", "Base Layer": "None (Unscented Canvas)", "Particle Primer Compatible": "Yes", "Eligible Scenarios": "DN, WP", "Projection Strength": "Intimate to Moderate (2–3 ft)", "Scent Profile & Notes Breakdown": "Warm cardamom, fresh ginger, cured tobacco, and cozy amber. Close-proximity evening & date night benchmark.", "Season_Sheet": "Early Fall / Crisp Fall / Deep Winter"},
    {"Custom Profile Name": "The Authentic Caribbean King", "Top Layer": "Creed Virgin Island Water", "Pairing Type": "Standalone Solo Wear", "Base Layer": "None (Unscented Canvas)", "Particle Primer Compatible": "Yes", "Eligible Scenarios": "LO, EC", "Projection Strength": "Moderate (3–4 ft)", "Scent Profile & Notes Breakdown": "Crisp Jamaican lime zest, coconut water, white rum, and sugar cane. High-heat resort and waterfront staple.", "Season_Sheet": "High Summer / Vacation"},
    {"Custom Profile Name": "The Desert Oud Monarch", "Top Layer": "House of Kelam (HOK) Nomade Ember", "Pairing Type": "Standalone Solo Wear", "Base Layer": "None (Unscented Canvas)", "Particle Primer Compatible": "No", "Eligible Scenarios": "NL, DN", "Projection Strength": "Nuclear / Beast Mode (8+ ft / 2 sp cap)", "Scent Profile & Notes Breakdown": "Smoked agarwood, incense tears, sweet tart raspberry, and raw leather. Cold-weather formal evening galas.", "Season_Sheet": "Deep Winter / Late Fall"},
    {"Custom Profile Name": "The Sovereign Agarwood Suite", "Top Layer": "House of Kelam (HOK) Oud Noir", "Pairing Type": "Standalone Solo Wear", "Base Layer": "None (Unscented Canvas)", "Particle Primer Compatible": "Yes", "Eligible Scenarios": "WP, DN, NL", "Projection Strength": "Strong (5–6 ft)", "Scent Profile & Notes Breakdown": "Precious agarwood, rosewood, cardamom, Sichuan pepper, and smoky amber. Authority and evening depth.", "Season_Sheet": "Deep Winter / Pre-Spring / Crisp Fall"},
    {"Custom Profile Name": "The Tactical Ambroxan Alpha", "Top Layer": "Dior Sauvage (EDT/EDP)", "Pairing Type": "Standalone Solo Wear", "Base Layer": "None (Unscented Canvas)", "Particle Primer Compatible": "Yes", "Eligible Scenarios": "WP, EC, NL, LO", "Projection Strength": "Strong (5–6 ft / 3 sp cap)", "Scent Profile & Notes Breakdown": "Calabrian bergamot, Sichuan pepper, geranium, and clean metallic ambroxan. Powerful projection engine.", "Season_Sheet": "All-Season (6-Band Universal)"},
    {"Custom Profile Name": "The Mediterranean Blue Powerhouse", "Top Layer": "Versace Dylan Blue", "Pairing Type": "Standalone Solo Wear", "Base Layer": "None (Unscented Canvas)", "Particle Primer Compatible": "No", "Eligible Scenarios": "WP, EC, NL, LO", "Projection Strength": "Strong (5–6 ft)", "Scent Profile & Notes Breakdown": "Aquatic citrus, violet leaf, black pepper, ambroxan, and incense. Clean modern power daily.", "Season_Sheet": "Spring / Summer / Early Fall"},
    {"Custom Profile Name": "The Boozy Oak Aristocrat", "Top Layer": "B&BW Whiskey Reserve (Cologne)", "Pairing Type": "Standalone Solo Wear", "Base Layer": "None (Unscented Canvas)", "Particle Primer Compatible": "Yes", "Eligible Scenarios": "WP, EC, DN, LO", "Projection Strength": "Moderate to Strong (4–5 ft)", "Scent Profile & Notes Breakdown": "Crisp red apple, single malt whiskey, and aged white oak barrel staves. Autumn stadium & lounge refinement.", "Season_Sheet": "Early Fall / Crisp Fall"}
]

@st.cache_data(ttl=300, show_spinner="Syncing with Fragrance Matrix in Google Drive...")
def fetch_matrix_from_drive():
    solo_df = pd.DataFrame(STANDALONE_MASTER)
    
    if "gcp_service_account" not in st.secrets:
        return pd.concat([get_fallback_dataframe(), solo_df], ignore_index=True)
    
    try:
        creds = Credentials.from_service_account_info(
            st.secrets["gcp_service_account"], scopes=SCOPE
        )
        client = gspread.authorize(creds)
        sheet_name = st.secrets.get("spreadsheet_name", "Fragrance Matrix")
        spreadsheet = client.open(sheet_name)
        
        all_dfs = []
        for ws in spreadsheet.worksheets():
            ws_title_lower = ws.title.strip().lower()
            if any(term in ws_title_lower for term in NON_PAIRING_SHEETS):
                continue

            records = ws.get_all_records()
            if records:
                w_df = pd.DataFrame(records)
                w_df["Season_Sheet"] = ws.title
                w_df = clean_matrix_columns(w_df)
                all_dfs.append(w_df)
        
        if all_dfs:
            master = pd.concat(all_dfs, ignore_index=True)
            master = master[
                master["Base Layer"].notna() & 
                (master["Base Layer"].astype(str).str.strip() != "") &
                (master["Base Layer"].astype(str).str.strip().str.lower() != "nan")
            ]
            master.fillna("", inplace=True)
            combined = pd.concat([master, solo_df], ignore_index=True)
            return combined
            
        return pd.concat([get_fallback_dataframe(), solo_df], ignore_index=True)
    except Exception as e:
        st.sidebar.error(f"Google Drive Sync Notice: {e}")
        return pd.concat([get_fallback_dataframe(), solo_df], ignore_index=True)

def clean_matrix_columns(df):
    col_map = {
        'Pairing Type': 'Pairing Type',
        'Base Layer': 'Base Layer',
        'Top Layer': 'Top Layer',
        'Custom Profile Name': 'Custom Profile Name',
        'Eligible Scenarios': 'Eligible Scenarios',
        'Projection Strength': 'Projection Strength',
        'Scent Profile & Notes Breakdown': 'Scent Profile & Notes Breakdown',
        'Particle Primer Compatible': 'Particle Primer Compatible'
    }
    for orig in df.columns:
        clean_orig = str(orig).strip()
        for standard in col_map:
            if clean_orig.lower() == standard.lower() or standard.lower() in clean_orig.lower():
                df.rename(columns={orig: standard}, inplace=True)
                break
    return df

def get_fallback_dataframe():
    data = [
        {"Season_Sheet": "Early Fall (Transitional 58°F – 72°F)", "Pairing Type": "Body Cream Layer", "Base Layer": "Graphite Cream", "Particle Primer Compatible": "Yes", "Top Layer": "Givenchy Gentleman Society", "Custom Profile Name": "The Modern Herbal Executive", "Eligible Scenarios": "WP, DN", "Projection Strength": "Strong (5–6 ft / 4 sp cap)", "Scent Profile & Notes Breakdown": "French sage mirrors Society sage; leatherwood grounds vetiver and cedarwood."},
        {"Season_Sheet": "Early Fall (Transitional 58°F – 72°F)", "Pairing Type": "Body Cream Layer", "Base Layer": "Mahogany Teakwood", "Particle Primer Compatible": "Yes", "Top Layer": "Alt. Blue Fate", "Custom Profile Name": "The Radiant Executive Timber", "Eligible Scenarios": "WP, DN, LO, NL", "Projection Strength": "Strong (5–6 ft)", "Scent Profile & Notes Breakdown": "Juicy pear, fresh ginger, and orange blossom over rich mahogany and oak. Magnetic waterfront evening presence."},
        {"Season_Sheet": "Early Fall (Transitional 58°F – 72°F)", "Pairing Type": "Body Cream Layer", "Base Layer": "Graphite Cream", "Particle Primer Compatible": "Yes", "Top Layer": "Gucci Guilty Pour Homme", "Custom Profile Name": "The High-Style Executive", "Eligible Scenarios": "WP, DN, EC", "Projection Strength": "Moderate (3 ft)", "Scent Profile & Notes Breakdown": "French lavender and lemon slice through thawing chill over structured leatherwood."},
        {"Season_Sheet": "Early Fall (Transitional 58°F – 72°F)", "Pairing Type": "Body Cream Layer", "Base Layer": "Mahogany Teakwood", "Particle Primer Compatible": "Yes", "Top Layer": "GA Acqua Di Gio Profondo", "Custom Profile Name": "The Oceanic Executive", "Eligible Scenarios": "WP, EC, LO", "Projection Strength": "Moderate to Strong (4–5 ft)", "Scent Profile & Notes Breakdown": "Crisp mineral deep sea notes cut through rich timbers and frosted lavender. Waterfront & open air ready."},
        {"Season_Sheet": "Crisp Fall (45°F – 60°F)", "Pairing Type": "Body Cream Layer", "Base Layer": "Whiskey Reserve", "Particle Primer Compatible": "Yes", "Top Layer": "John Wick x Scentbird", "Custom Profile Name": "The Premium Lounge", "Eligible Scenarios": "DN, WP, NL, LO", "Projection Strength": "Moderate to Strong (4–5 ft)", "Scent Profile & Notes Breakdown": "Amber bourbon and cedarwood lock directly onto whiskey and oak. Warm stadium & chilly evening benchmark."},
        {"Season_Sheet": "Spring (Warming 55°F – 70°F)", "Pairing Type": "Cologne Mixology", "Base Layer": "Alt. Splish (D&G Light Blue)", "Particle Primer Compatible": "Yes", "Top Layer": "Alt. Reality (LV Imagination)", "Custom Profile Name": "The Sicilian Citrus Tea", "Eligible Scenarios": "EC, WP, LO", "Projection Strength": "Moderate (3–4 ft)", "Scent Profile & Notes Breakdown": "Mandarin and grapefruit peel blend into black tea, ginger, and ambroxan."},
        {"Season_Sheet": "High Summer (75°F – 95°F+)", "Pairing Type": "Body Cream Layer", "Base Layer": "Ocean Cream", "Particle Primer Compatible": "Yes", "Top Layer": "Alt. Blue Fate (Blue Talisman)", "Custom Profile Name": "The Luminous Azure Sea", "Eligible Scenarios": "EC, WP, LO", "Projection Strength": "Moderate to Strong (4–5 ft)", "Scent Profile & Notes Breakdown": "Juicy pear and Akigalawood float over coastal air and blue cypress."}
    ]
    return pd.DataFrame(data)

# ---------------------------------------------------------
# EXPANDED METEOROLOGICAL TELEMETRY ENGINE
# ---------------------------------------------------------
PRESET_CITIES = {
    "Washington, D.C.": {"lat": 38.9072, "lon": -77.0369},
    "National Harbor, MD": {"lat": 38.7848, "lon": -77.0169},
    "New York, NY": {"lat": 40.7128, "lon": -74.0060},
    "Miami, FL": {"lat": 25.7617, "lon": -80.1918},
    "Orlando, FL": {"lat": 28.5383, "lon": -81.3792},
    "Atlanta, GA": {"lat": 33.7490, "lon": -84.3880},
    "Chicago, IL": {"lat": 41.8781, "lon": -87.6298},
    "Los Angeles, CA": {"lat": 34.0522, "lon": -118.2437},
    "St. Thomas, VI": {"lat": 18.3354, "lon": -64.9534}
}

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
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={query.strip()}&count=6&language=en&format=json"
    try:
        r = requests.get(url, timeout=5).json()
        results = r.get("results", [])
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

# ---------------------------------------------------------
# SARTORIAL COLOR MATCHING REGISTRY
# ---------------------------------------------------------
SARTORIAL_MAP = {
    "The Crisp Blue Alpha": {"name": "Deep Navy & Crisp Gunmetal", "primary": "#0D2A6B", "accent": "#5A6570", "styling": "Crisp blue aromatic lift over modern tailored suiting or clean dark denim."},
    "The Luminous Modern Executive": {"name": "Slate Charcoal & Soft Lavender", "primary": "#2B303A", "accent": "#9E97A9", "styling": "Modern ambroxan and orange blossom over tailored slate."},
    "The Sovereign Society Executive": {"name": "Midnight Navy & Cardamom Bronze", "primary": "#1A2238", "accent": "#A3704C", "styling": "Rich narcissus and dark vanilla over deep executive navy with warm leather accents."},
    "The High-Tech Corporate Mind": {"name": "Slate Olive & Sunlit Amber", "primary": "#3B443B", "accent": "#D9822B", "styling": "Herbal myrtle and cedar balanced by energetic mandarin."},
    "The Modern Mineral Aristocrat": {"name": "Mineral Slate & Smoked Sage", "primary": "#3C4A57", "accent": "#8A9A86", "styling": "Mineral salt and clary sage over muted herbal earth."},
    "The Alpine Aristocrat": {"name": "Deep Teak Brown & Alpine Silver", "primary": "#2E1F18", "accent": "#D6DBDF", "styling": "Polished dark timber balancing frosty green tea air."},
    "The Seductive Modern Barbershop": {"name": "Charcoal Wool & French Lilac", "primary": "#33383B", "accent": "#92849E", "styling": "Clean orange blossom and French lavender over dark suiting."},
    "The Luminous Imperial Tea": {"name": "Black Tea Amber & Cool Slate", "primary": "#8C4A28", "accent": "#4A5868", "styling": "Chinese black tea and ginger grounded in tailored slate chinos."},
    "The Modern Floral Executive": {"name": "Slate Charcoal & Soft Lilac", "primary": "#2C3038", "accent": "#A394AA", "styling": "Clean orange blossom and Ambrofix over dark structured slate."},
    "The Gunmetal Assassin": {"name": "Gunmetal Steel & Bourbon Ochre", "primary": "#3A3E45", "accent": "#B5732A", "styling": "Cold metallic slide and amber bourbon over tactical wool or leather."},
    "The Deep Abyssal Ocean": {"name": "Deep Nautical Navy & Mineral Sea Grey", "primary": "#122038", "accent": "#8898A6", "styling": "Salty marine accords and green mandarin over abyssal navy."},
    "The Oceanic Executive": {"name": "Deep Marine Navy & Frosted Steel", "primary": "#0D2A6B", "accent": "#8A9EA7", "styling": "Tailored dark navy overshirt with frosted steel trousers; built for waterfront breezes."},
    "The Radiant Executive Timber": {"name": "Deep Teak Brown & Washed Mineral Blue", "primary": "#2E1F18", "accent": "#4F6B85", "styling": "Tailored selvedge denim or dark timber trousers with washed mineral blue layer."},
    "The Golden Gourmand Sovereign": {"name": "Dark Espresso & Warm Honey Tan", "primary": "#281D17", "accent": "#C48D47", "styling": "Sweet almond and benzoin resting on dark roasted espresso."},
    "The Intimate Tobacco Seduction": {"name": "Espresso & Spiced Cognac", "primary": "#2A1D15", "accent": "#9E5A2A", "styling": "Cozy tobacco and ginger over rich brown knitwear for close dining."},
    "The Authentic Caribbean King": {"name": "Palm Green & Coconut Shell Tan", "primary": "#324A38", "accent": "#9C7A58", "styling": "Lime zest, sugar cane, and white rum in island earth tones."},
    "The Desert Oud Monarch": {"name": "Midnight Black & Desert Crimson", "primary": "#1A1A1A", "accent": "#801B2B", "styling": "Smoky oud and sweet raspberry over sleek nocturnal darks."},
    "The Sovereign Agarwood Suite": {"name": "Smoked Charcoal & Rosewood Bronze", "primary": "#2B2D33", "accent": "#8C4F47", "styling": "Agarwood, rosewood, and cardamom in a sovereign corporate or gala cut."},
    "The Tactical Ambroxan Alpha": {"name": "Tactical Gunmetal & Electric Bergamot Blue", "primary": "#2A2C2E", "accent": "#3A6B88", "styling": "Fiery Sichuan pepper and ambroxan over dark technical gear."},
    "The Mediterranean Blue Powerhouse": {"name": "Midnight Blue & Smoked Incense Grey", "primary": "#121F38", "accent": "#525B66", "styling": "Aquatic citrus, violet leaf, and incense in sharp contrast."},
    "The Boozy Oak Aristocrat": {"name": "Rich Cognac & Dark Oak Charcoal", "primary": "#8C4820", "accent": "#2A2E33", "styling": "Crisp apple and single malt whiskey over structured dark wool or stadium jacket."},
    "The Premium Lounge": {"name": "Gunmetal Steel & Bourbon Ochre", "primary": "#3A3E45", "accent": "#B5732A", "styling": "Amber bourbon and dark cedarwood over heavy wool or leather jacket."},
    "The Modern Herbal Executive": {"name": "Executive Navy & Cardamom Bronze", "primary": "#1A2238", "accent": "#A3704C", "styling": "Suited navy trouser with bronze/gunmetal hardware."},
    "The High-Style Executive": {"name": "Charcoal Wool & French Lilac", "primary": "#2B3038", "accent": "#9E92A8", "styling": "Charcoal relaxed trousers with soft heather lilac knit."},
    "The Tailored Contemporary Alpha": {"name": "Charcoal Slate & Ice Blue", "primary": "#3E444C", "accent": "#A5C9EB", "styling": "Slate tailored trousers with crisp ice-blue dress shirt."},
    "The Power Blue Executive": {"name": "Deep French Blue & Crisp White", "primary": "#0D2A6B", "accent": "#FFFFFF", "styling": "Dark structured blazer and crisp collared poplin."},
    "The Sicilian Citrus Tea": {"name": "Earthy Olive & Sunlit Ochre", "primary": "#4A5240", "accent": "#D4A373", "styling": "Smart casual linen/knit with warm ochre wrist watch strap."},
    "The Alpine Tea Stream": {"name": "Black Tea Amber & Cool Slate", "primary": "#8C4A28", "accent": "#4A5868", "styling": "Grounded warm-amber tones over tailored slate chinos."}
}

DEFAULT_PALETTE = {"name": "Classic Executive Slate & White", "primary": "#2F3E46", "accent": "#F8F9FA", "styling": "Clean tailored neutral wardrobe with subtle brushed steel accent."}

# ---------------------------------------------------------
# SIDEBAR CONTROLS & EXPANDED WEATHER TELEMETRY
# ---------------------------------------------------------
with st.sidebar:
    st.image("https://images.unsplash.com/photo-1592945403244-b3fbafd7f539?w=500&auto=format&fit=crop&q=60", use_container_width=True)
    st.title("Fragrance Ops")
    st.caption("Live Google Drive Matrix • Climate Engine")
    st.markdown("---")
    
    st.subheader("⚙️ Deployment Mode")
    rotation_mode = st.radio(
        "Wardrobe Deployment",
        ["🔄 Full Wardrobe (Mixology + Solo)", "🎯 Standalone Solo Only", "🧪 Layering & Mixology Only"],
        index=0
    )
    
    st.markdown("---")
    st.subheader("📍 Location Mode")
    loc_mode = st.radio(
        "Select Mode",
        ["📱 Phone GPS (Live)", "🔍 Search Any City", "🏙️ Quick Presets"],
        index=0 if HAS_GEOLOCATION else 2
    )
    
    active_location_label = "Washington, D.C."
    current_lat = PRESET_CITIES["Washington, D.C."]["lat"]
    current_lon = PRESET_CITIES["Washington, D.C."]["lon"]
    
    if loc_mode == "📱 Phone GPS (Live)":
        if HAS_GEOLOCATION:
            device_loc = get_geolocation()
            if device_loc and "coords" in device_loc:
                current_lat = device_loc["coords"]["latitude"]
                current_lon = device_loc["coords"]["longitude"]
                resolved_name = reverse_geocode_coords(current_lat, current_lon)
                active_location_label = f"📱 {resolved_name}"
                st.success(f"Locked to device GPS: **{resolved_name}**")
            else:
                st.info("Tap **Allow** on your phone to lock GPS. Baseline: D.C.")
                active_location_label = "Washington, D.C. (Default)"
        else:
            st.warning("Install `streamlit-js-eval` for phone GPS.")
            active_location_label = "Washington, D.C. (Default)"
            
    elif loc_mode == "🔍 Search Any City":
        search_input = st.text_input("Enter City, State or Country", placeholder="e.g. Philadelphia, Austin, Paris, London...")
        if search_input:
            search_matches = search_city_geocoding(search_input)
            if search_matches:
                choice = st.selectbox(
                    "Matching Locations Found",
                    search_matches,
                    format_func=lambda x: x["label"]
                )
                current_lat = choice["lat"]
                current_lon = choice["lon"]
                active_location_label = f"🔍 {choice['label']}"
            else:
                st.warning(f"No coordinates found for '{search_input}'. Check spelling or try a broader region.")
                active_location_label = "Washington, D.C. (Default)"
        else:
            st.caption("Type any destination above to query live global weather telemetry.")
            active_location_label = "Washington, D.C. (Default)"
            
    else:  # Quick Presets
        selected_city = st.selectbox("Select Metro Preset", list(PRESET_CITIES.keys()), index=0)
        current_lat = PRESET_CITIES[selected_city]["lat"]
        current_lon = PRESET_CITIES[selected_city]["lon"]
        active_location_label = f"🏙️ {selected_city}"

    # Fetch Comprehensive Live Weather
    wx = get_comprehensive_weather(current_lat, current_lon)
    active_band = evaluate_thermodynamic_band(wx["temp"], wx["wind_chill"])
    
    st.markdown("---")
    st.subheader("🌤️ Meteorological Panel")
    
    delta_chill = wx["wind_chill"] - wx["temp"]
    delta_str = f"Feels like {wx['wind_chill']:.1f}°F" if abs(delta_chill) >= 1.0 else "Stable air"
    st.metric("Live Ambient Temp", f"{wx['temp']:.1f} °F", delta_str)
    
    w_col1, w_col2 = st.columns(2)
    with w_col1:
        st.write(f"📈 **High:** {wx['high']:.0f}°F")
        st.write(f"📉 **Low:** {wx['low']:.0f}°F")
    with w_col2:
        st.write(f"💧 **Humidity:** {wx['humidity']}%")
        st.write(f"🌧️ **Rain:** {wx['rain_chance']}%")
        
    st.caption(f"🌬️ **Wind Speed:** {wx['wind']:.1f} mph | **Active:** {active_location_label}")
    st.info(f"**Target Seasonal Band:** {active_band}")
    
    if st.button("🔄 Sync with Google Drive Now"):
        st.cache_data.clear()
        st.success("Cache refreshed from Google Drive!")

# Load Master Matrix
matrix_df = fetch_matrix_from_drive()

# ---------------------------------------------------------
# MAIN APP TABS
# ---------------------------------------------------------
tab_briefing, tab_explorer, tab_directory, tab_planner = st.tabs([
    "👔 Daily Briefing & Ops",
    "🔍 Matrix Explorer & Generator",
    "📖 Standalone Directory",
    "🧳 Trip Capsule Planner"
])

# ---------------------------------------------------------
# TAB 1: DAILY BRIEFING & OPS (ATMOSPHERICALLY WEIGHTED)
# ---------------------------------------------------------
with tab_briefing:
    st.header("Daily Operational Scent Briefing")
    st.caption(f"Atmospheric thermodynamics locked to {active_location_label} ({wx['temp']:.1f}°F, High {wx['high']:.0f}°F / Low {wx['low']:.0f}°F, {wx['humidity']}% Humidity).")
    
    SCENARIO_OPTIONS = {
        "💼 Work & Professional (Office Desk, Meetings, Leadership)": {
            "badge": "WP",
            "desc": "Enforces a controlled 3–4 ft sillage cap; polished woods, clean aromatics, tailored blues.",
            "sprays": "3–4 sprays total (1 behind each ear, 1 center chest over cream/canvas, 1 across shirt collar/lapel).",
            "cap": "Controlled Moderate (3–4 ft cap)"
        },
        "🌊 Leisure & Outdoor (Waterfront, Patios, Festivals, Stadium Games)": {
            "badge": "LO",
            "desc": "Built to cut through open air, river breezes, sunshine, and humidity without fading.",
            "sprays": "4–5 sprays total (1 behind each ear, 1 center chest over cream/canvas, 2 misted across jacket, hoodie, or overshirt).",
            "cap": "Assertive Open-Air (4–6 ft reach)"
        },
        "🍸 Date Night & Evening (Dinner, Intimate Speakeasy, Lounge)": {
            "badge": "DN",
            "desc": "Intimate 2–3 ft scent bubble; warm ambers, soft spices, cardamom, leather, and dark vanilla.",
            "sprays": "3–4 sprays total (1 to each side of collarbones/neck, 1 center chest over canvas, 1 back of neck).",
            "cap": "Intimate / Close Quarters (2–3 ft bubble)"
        },
        "🪩 Nightlife & Lounges (High Impact, Clubs, Social Lounges)": {
            "badge": "NL",
            "desc": "Maximum presence and heavy sillage; bold peppers, boozy resins, and powerful ouds.",
            "sprays": "5–6 sprays total (2 neck pulse points, 2 chest over cream, 2 external clothing/lapel).",
            "cap": "Bold Statement / Beast Mode (6–8+ ft)"
        },
        "☕ Everyday & Casual (Errands, WFH, Relaxed Daytime)": {
            "badge": "EC",
            "desc": "Clean, uplifting, and approachable; fresh musks, sparkling teas, and refreshing citrus/aquatics.",
            "sprays": "3 sprays total (1 behind each ear, 1 center chest over canvas).",
            "cap": "Approachable Moderate (2–3 ft)"
        }
    }
    
    today_w = datetime.date.today().weekday()
    if today_w in [0, 1, 2, 3]:
        default_idx = 0
    elif today_w == 4:
        default_idx = 0
    elif today_w == 5:
        default_idx = 1
    else:
        default_idx = 4
        
    selected_scenario_label = st.selectbox(
        "🎯 Select Operational Scenario Context",
        list(SCENARIO_OPTIONS.keys()),
        index=default_idx
    )
    
    scen_meta = SCENARIO_OPTIONS[selected_scenario_label]
    target_badge = scen_meta["badge"]
    
    st.caption(f"*{scen_meta['desc']}*")
    
    candidate_df = matrix_df.copy()
    if rotation_mode == "🎯 Standalone Solo Only":
        candidate_df = candidate_df[candidate_df["Pairing Type"] == "Standalone Solo Wear"]
    elif rotation_mode == "🧪 Layering & Mixology Only":
        candidate_df = candidate_df[candidate_df["Pairing Type"] != "Standalone Solo Wear"]
    
    scen_col = candidate_df.get("Eligible Scenarios", pd.Series([], dtype=str))
    scenario_filtered_df = candidate_df[scen_col.str.contains(target_badge, case=False, na=False)]
    
    if scenario_filtered_df.empty:
        scenario_filtered_df = candidate_df
        
    weather_tags = []
    
    is_damp = (wx["humidity"] >= 70 or wx["rain_chance"] >= 35)
    if is_damp:
        weather_tags.append("🌧️ Rain / High Humidity Anchor Active")
        damp_mask = scenario_filtered_df["Scent Profile & Notes Breakdown"].str.contains(
            "sage|vetiver|leatherwood|ambroxan|oak|birch|ginger|cedar|pepper", case=False, na=False
        )
        if damp_mask.any():
            scenario_filtered_df = scenario_filtered_df[damp_mask]
            
    is_chilly = (wx["wind_chill"] < 50.0)
    if is_chilly:
        weather_tags.append("❄️ Wind Chill Suppression Active")
        chill_mask = ~scenario_filtered_df["Scent Profile & Notes Breakdown"].str.contains(
            "eau fraiche|frozen grapefruit|lime zest|coconut water", case=False, na=False
        )
        if chill_mask.any():
            scenario_filtered_df = scenario_filtered_df[chill_mask]

    is_warm_spike = (wx["high"] >= 78.0)
    if is_warm_spike:
        weather_tags.append("☀️ Warm Afternoon Spike Guard")
        warm_mask = ~scenario_filtered_df["Scent Profile & Notes Breakdown"].str.contains(
            "tonka bean|roasted vanilla|smoked agarwood|sweet almond|incense tears", case=False, na=False
        )
        if warm_mask.any():
            scenario_filtered_df = scenario_filtered_df[warm_mask]

    if not scenario_filtered_df.empty:
        today_num = datetime.date.today().toordinal()
        badge_seed = sum(ord(c) for c in target_badge)
        wx_seed = int(wx["temp"] * 3 + wx["humidity"] + wx["rain_chance"] + wx["wind_chill"])
        random.seed(today_num + wx_seed + badge_seed)
        daily_idx = random.randint(0, len(scenario_filtered_df) - 1)
        daily_choice = scenario_filtered_df.iloc[daily_idx]
        
        def safe_val(val, fallback="N/A"):
            s = str(val).strip()
            return fallback if not s or s.lower() == "nan" else s

        profile_name = safe_val(daily_choice.get("Custom Profile Name"), "Custom Executive Profile")
        pairing_type = safe_val(daily_choice.get("Pairing Type"), "Standalone Solo Wear")
        base_layer = safe_val(daily_choice.get("Base Layer"), "None (Unscented Canvas)")
        top_layer = safe_val(daily_choice.get("Top Layer"), "Givenchy Gentleman Society")
        primer_compat = safe_val(daily_choice.get("Particle Primer Compatible"), "Yes")
        projection = safe_val(daily_choice.get("Projection Strength"), scen_meta["cap"])
        scent_notes = safe_val(daily_choice.get("Scent Profile & Notes Breakdown"), "Harmonious scent progression tailored to the operational scenario.")
        
        is_solo = (pairing_type == "Standalone Solo Wear" or "none" in base_layer.lower())
        use_butter = (wx["wind_chill"] < 65.0)
        canvas_base = "Unscented Body Butter" if use_butter else "Unscented Body Lotion"
        
        if is_solo:
            canvas_recommendation = f"{canvas_base} (Clean Canvas Prep)"
            canvas_reason = (
                f"Calibrated for {wx['temp']:.1f}°F air (Wind Chill: {wx['wind_chill']:.1f}°F, {wx['humidity']}% humidity). "
                f"{'Locks deep moisture against drying chill/damp air' if use_butter else 'Maintains weightless hydration under warmer highs'} "
                "without muting the single bottle's natural note pyramid."
            )
        else:
            canvas_recommendation = f"{canvas_base} Base + {base_layer}"
            if is_damp:
                canvas_reason = f"Damp Weather Defense ({wx['humidity']}% humidity, {wx['rain_chance']}% rain): Provides a resilient lipid barrier so heavy moisture vapors cannot wash out base timbers."
            elif use_butter:
                canvas_reason = f"Thermal Protection (Wind Chill {wx['wind_chill']:.1f}°F): Deep lipid bonding locks volatile aromatic notes onto skin against brisk drafts."
            else:
                canvas_reason = f"Warm Dynamic ({wx['high']:.0f}°F daytime peak): Prevents heavy oil suffocation while maintaining clean sillage."
        
        spray_strategy = scen_meta["sprays"]
        if wx["wind"] >= 10.0 or target_badge == "LO":
            spray_strategy += f" *[Wind Defense Active: 1 extra mist across jacket collar/lapel to counter {wx['wind']:.1f} mph outdoor wind shear].*"
            
        if not is_solo and base_layer and "none" not in base_layer.lower():
            wash_recommendation = f"{base_layer} Body Wash (1:1 Matching Shower Protocol)"
        else:
            wash_recommendation = "Freshwater Body Wash (Clean Slate Universal Canvas)"
            
        sartorial = SARTORIAL_MAP.get(profile_name, DEFAULT_PALETTE)
        badge_style = "badge-solo" if is_solo else "badge-tag"
        
        col1, col2 = st.columns([1.8, 1.2])
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <span class="badge-scenario">🎯 {target_badge} PROTOCOL</span>
                <span class="{badge_style}">{"🎯 SOLO WEAR" if is_solo else "🧪 LAYERING PICK"}</span>
                <span class="badge-tag">{pairing_type}</span>
                <span class="badge-tag">Primer: {primer_compat}</span>
                {' '.join([f'<span class="badge-weather">{tag}</span>' for tag in weather_tags])}
                <h2 style="color: #58A6FF; margin-top: 8px; font-weight: 700;">{profile_name}</h2>
                <p style="font-size: 15.5px; margin-bottom: 6px;">
                    <strong>{'Selected Fragrance' if is_solo else 'Top Layer'}:</strong> <span style="color: #58A6FF; font-weight: 600;">{top_layer}</span><br>
                    <strong>Base Preparation:</strong> {base_layer}
                </p>
                <p style="font-style: italic; color: #8B949E; font-size: 13.5px;">"{scent_notes}"</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.subheader("🎯 Application Strategy")
            st.write(f"- **Target Sillage Cap:** {scen_meta['cap']} *(Evaluated for {target_badge})*")
            st.write(f"- **Spray Distribution:** {spray_strategy}")
            st.write(f"- **Shower Prep:** **{wash_recommendation}**")
            st.write(f"- **Grooming Canvas:** **{canvas_recommendation}**")
            st.caption(f"*{canvas_reason}*")
            
            temp_range = wx["high"] - wx["low"]
            if temp_range >= 18.0:
                st.markdown(f"""
                <div style="background-color: rgba(235, 142, 60, 0.1); border-left: 4px solid #F0883E; padding: 10px 14px; border-radius: 6px; margin-top: 10px; font-size: 13px;">
                    <strong>Transitional Swing Notice:</strong> {temp_range:.0f}°F delta between Low ({wx['low']:.0f}°F) and High ({wx['high']:.0f}°F). 
                    The chosen formula opens with sufficient crispness for early chill while resting on an anchor that will not turn cloying once afternoon peak temperatures are reached.
                </div>
                """, unsafe_allow_html=True)

        with col2:
            st.subheader("🎨 Sartorial Color Harmony")
            st.markdown(f"""
            <div class="sartorial-card">
                <div style="font-weight: 600; font-size: 16px; margin-bottom: 8px;">{sartorial['name']}</div>
                <p style="margin: 4px 0;"><span class="swatch-box" style="background-color: {sartorial['primary']};"></span> Primary: <code>{sartorial['primary']}</code></p>
                <p style="margin: 4px 0;"><span class="swatch-box" style="background-color: {sartorial['accent']};"></span> Accent: <code>{sartorial['accent']}</code></p>
                <div style="margin-top: 10px; font-size: 13px; color: #8B949E;">{sartorial['styling']}</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            st.subheader("🔄 Alternate Roll")
            if st.button("Generate Alternative Option for this Scenario"):
                st.rerun()
    else:
        st.warning("No pairing recipes found in the active matrix sheets for this scenario. Please verify your Google Sheet tabs.")

# ---------------------------------------------------------
# TAB 2: MATRIX EXPLORER & GENERATOR
# ---------------------------------------------------------
with tab_explorer:
    st.header("Fragrance Matrix Query Engine")
    st.caption("Filter live recipes across all seasonal brackets, scenario badges, pairing types, and chemical primers.")
    
    col_f1, col_f2, col_f3, col_f4 = st.columns(4)
    
    with col_f1:
        if "Season_Sheet" in matrix_df.columns:
            seasons = ["All Sheets / Bands"] + sorted([s for s in matrix_df["Season_Sheet"].unique() if str(s).strip() != ""])
            chosen_season = st.selectbox("Seasonal Sheet", seasons)
        else:
            chosen_season = "All Sheets / Bands"
            
    with col_f2:
        modes = ["All Modes", "Standalone Solo Wear", "Body Cream Layer", "Cologne Mixology"]
        chosen_mode = st.selectbox("Pairing Mode", modes)
        
    with col_f3:
        scenarios = [
            "All Scenarios", 
            "WP (Work & Professional)", 
            "LO (Leisure & Outdoor)", 
            "DN (Date Night & Evening)", 
            "NL (Nightlife & Lounges)", 
            "EC (Everyday & Casual)"
        ]
        chosen_scen = st.selectbox("Target Scenario Badge", scenarios)
        
    with col_f4:
        primer_opt = st.selectbox("Particle Primer Compatible", ["Any", "Yes", "No"])
        
    filtered_df = matrix_df.copy()
    if chosen_season != "All Sheets / Bands" and "Season_Sheet" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["Season_Sheet"] == chosen_season]
        
    if chosen_mode != "All Modes" and "Pairing Type" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["Pairing Type"] == chosen_mode]
        
    if chosen_scen != "All Scenarios" and "Eligible Scenarios" in filtered_df.columns:
        badge = chosen_scen.split()[0]
        filtered_df = filtered_df[filtered_df["Eligible Scenarios"].str.contains(badge, case=False, na=False)]
        
    if primer_opt != "Any" and "Particle Primer Compatible" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["Particle Primer Compatible"].astype(str).str.strip().str.lower() == primer_opt.lower()]

    st.markdown("---")
    gen_col1, gen_col2 = st.columns([2, 1])
    with gen_col1:
        st.write(f"**Matching Recipes Found:** {len(filtered_df)}")
    with gen_col2:
        if st.button("🎲 Surprise Me (Random Pair from Filter)"):
            if not filtered_df.empty:
                pick = filtered_df.sample(1).iloc[0]
                is_p_solo = (pick.get("Pairing Type") == "Standalone Solo Wear")
                summary_line = f"{pick.get('Top Layer')} (Solo)" if is_p_solo else f"{pick.get('Base Layer')} + {pick.get('Top Layer')}"
                st.info(f"**Random Pick:** **{pick.get('Custom Profile Name')}** ({summary_line})\n\n*{pick.get('Scent Profile & Notes Breakdown')}*")
            else:
                st.warning("No entries match the current filter.")
                
    display_cols = [c for c in ['Custom Profile Name', 'Pairing Type', 'Base Layer', 'Top Layer', 'Eligible Scenarios', 'Projection Strength', 'Scent Profile & Notes Breakdown'] if c in filtered_df.columns]
    st.dataframe(filtered_df[display_cols], use_container_width=True, hide_index=True)
    
    # Boundary Clash Checker
    st.markdown("### ⚠️ Boundary Clash Checker")
    st.caption("Verify experimental combinations against your operational conflict rules.")
    
    check_base = st.text_input("Enter Base Layer (Cream or Cologne 1)", placeholder="e.g. Vanilla Noir Cream")
    check_top = st.text_input("Enter Top Layer (Cologne 2)", placeholder="e.g. Versace Man Eau Fraiche")
    
    if check_base and check_top:
        b_low = check_base.lower()
        t_low = check_top.lower()
        clash = False
        warning_msg = ""
        
        if ("noir" in b_low or "vanilla" in b_low) and ("eau fraiche" in t_low or "atlantic" in t_low or "skai" in t_low or "ceo" in t_low):
            clash = True
            warning_msg = "Clash Detected: Dense vanilla notes will suffocate delicate airy citrus and marine accords."
        elif ("ocean" in b_low or "freshwater" in b_low) and ("nomade" in t_low or "oud" in t_low or "the one" in t_low):
            clash = True
            warning_msg = "Clash Detected: Heavy desert oud, tobacco, and resins will overpower transparent ozone/spring water accords."
        elif ("virgin island" in t_low or "colada" in t_low) and ("mahogany" in b_low or "graphite" in b_low or "noir" in b_low):
            clash = True
            warning_msg = "Clash Detected: Raw lime and coconut become muddled when layered over heavy dry oak, leatherwood, or smoky cardamom."
            
        if clash:
            st.error(warning_msg)
        else:
            st.success("✅ Clean Synergy: No active boundary clash detected in operational rules.")

# ---------------------------------------------------------
# TAB 3: STANDALONE DIRECTORY
# ---------------------------------------------------------
with tab_directory:
    st.header("Standalone Fragrance Directory & Notes")
    st.caption("Search across all standalone colognes, mists, and inspired DNA profiles.")
    
    search_query = st.text_input("🔍 Search notes, cologne names, or DNA references", placeholder="e.g. Sage, Ambroxan, YSL Y, Aventus, Vetiver...")
    
    if search_query:
        mask = matrix_df.astype(str).apply(lambda row: row.str.contains(search_query, case=False).any(), axis=1)
        search_res = matrix_df[mask]
        st.write(f"Found **{len(search_res)}** references:")
        disp_cols = [c for c in ['Custom Profile Name', 'Base Layer', 'Top Layer', 'Scent Profile & Notes Breakdown'] if c in search_res.columns]
        st.dataframe(search_res[disp_cols], use_container_width=True, hide_index=True)
    else:
        st.info("Type a note (e.g. 'bergamot', 'leatherwood', 'pear') or fragrance name above to query matching profiles.")

# ---------------------------------------------------------
# TAB 4: 🧳 TRIP CAPSULE PLANNER
# ---------------------------------------------------------
with tab_planner:
    st.header("🧳 Trip Fragrance Capsule Planner")
    st.caption("Pack light, project right. Build a lean, high-synergy travel wardrobe of 1–2 universal base creams and 3–4 colognes that cover every scenario of your itinerary.")
    
    p_col1, p_col2 = st.columns([1.2, 1.8])
    
    with p_col1:
        st.subheader("1. Trip Parameters")
        dest_input = st.text_input("Destination(s)", value="Atlanta, GA", placeholder="e.g. Atlanta, GA / Miami / London")
        
        # Date range picker
        d_start = datetime.date.today() + datetime.timedelta(days=7)
        d_end = d_start + datetime.timedelta(days=4)
        date_range = st.date_input("Travel Dates", value=(d_start, d_end))
        
        # Scenarios to cover
        st.write("**Scenarios to Cover on Trip:**")
        scen_wp = st.checkbox("💼 Work & Professional (Meetings, Leadership)", value=True)
        scen_ec = st.checkbox("☕ Everyday & Casual (Daytime, Exploring, Transit)", value=True)
        scen_dn = st.checkbox("🍸 Date Night & Dining (Intimate, Evening Out)", value=True)
        scen_nl = st.checkbox("🪩 Nightlife & Lounges (High Impact, Club)", value=False)
        scen_lo = st.checkbox("🌊 Leisure & Outdoor (Waterfront, Patios, Stadium)", value=False)
        
        # Base Cream Allowance
        cream_choice = st.radio(
            "Base Cream Allowance",
            ["1 Universal Anchor Cream", "2 Dynamic Dual Creams"],
            index=0
        )
        
        plan_button = st.button("🚀 Generate Travel Capsule Plan", use_container_width=True)

    with p_col2:
        st.subheader("2. Curated Travel Capsule")
        
        # Collect target scenario codes
        target_badges = []
        if scen_wp: target_badges.append("WP")
        if scen_ec: target_badges.append("EC")
        if scen_dn: target_badges.append("DN")
        if scen_nl: target_badges.append("NL")
        if scen_lo: target_badges.append("LO")
        if not target_badges:
            target_badges = ["WP", "EC", "DN"]
            
        # Destination geocode & climate estimation
        trip_city_matches = search_city_geocoding(dest_input.split("/")[0].strip())
        if trip_city_matches:
            c_lat, c_lon = trip_city_matches[0]["lat"], trip_city_matches[0]["lon"]
            city_label = trip_city_matches[0]["label"]
        else:
            c_lat, c_lon = 33.7490, -84.3880
            city_label = dest_input
            
        t_wx = get_comprehensive_weather(c_lat, c_lon)
        t_band = evaluate_thermodynamic_band(t_wx["temp"], t_wx["wind_chill"])
        
        st.markdown(f"""
        <div style="background-color: #161B22; border: 1px solid #30363D; border-radius: 8px; padding: 12px; margin-bottom: 12px; font-size: 13.5px;">
            📍 <strong>Target Location:</strong> {city_label}<br>
            🌡️ <strong>Estimated Climate:</strong> ~{t_wx['temp']:.0f}°F (High {t_wx['high']:.0f}°F / Low {t_wx['low']:.0f}°F) • <strong>Band:</strong> {t_band}<br>
            🎯 <strong>Required Coverage:</strong> {', '.join(target_badges)}
        </div>
        """, unsafe_allow_html=True)
        
        # Algorithm: Determine Anchor Cream(s)
        # Warm / High Heat: Freshwater Cream (or Ocean)
        # Transitional / All-Season: Graphite Cream (Sage, Bergamot, Leatherwood)
        # Cold / Evening heavy: Mahogany Teakwood Cream (Dark oak, timbers)
        if "Summer" in t_band:
            base_1 = "Freshwater Cream"
            base_1_desc = "Universal crisp mountain spring water canvas; prevents heavy cream suffocation in high humidity."
            base_2 = "Graphite Cream" if cream_choice == "2 Dynamic Dual Creams" else None
            base_2_desc = "Grounded aromatic sage and leatherwood for air-conditioned meetings and evening dinners." if base_2 else ""
        elif "Winter" in t_band:
            base_1 = "Mahogany Teakwood Cream"
            base_1_desc = "Dense dark timber and frosted lavender foundation; binds warm resins against sub-freezing drafts."
            base_2 = "Whiskey Reserve Cream" if cream_choice == "2 Dynamic Dual Creams" else None
            base_2_desc = "Boozy single-malt and white oak for intimate evening dining and cigar lounges." if base_2 else ""
        else: # Early Fall, Fall, Spring, Pre-Spring
            base_1 = "Graphite Cream"
            base_1_desc = "The #1 Versatility carrier; aromatic sage and leatherwood effortlessly anchor boardroom blues, barbershops, and evening woods."
            base_2 = "Mahogany Teakwood Cream" if cream_choice == "2 Dynamic Dual Creams" else None
            base_2_desc = "Rich dark oak and frosted lavender; provides thermal reinforcement for outdoor breezes and night lounges." if base_2 else ""
            
        # Algorithm: Select 3-4 Colognes
        # Slot 1: The Daytime Executive Workhorse (WP / EC)
        # Slot 2: The Luminous Chameleon / Social Bridge (WP / EC / DN / LO)
        # Slot 3: The Intimate Evening & Dining Anchor (DN)
        # Slot 4: The Wildcard / Beast Mode or Outdoor Shield (NL or LO)
        if "Summer" in t_band:
            col_1 = {"name": "Alt. A (YSL Y DNA)", "role": "Daytime Workhorse (WP / EC)", "notes": "Green apple, ginger, and sage. Clean, sharp daily driver."}
            col_2 = {"name": "Alt. Reality (LV Imagination DNA)", "role": "Luminous Social Refresher (EC / LO)", "notes": "Chinese black tea, Sicilian citrus, and sparkling ambroxan."}
            col_3 = {"name": "Alt. Blue Fate (Blue Talisman DNA)", "role": "Evening Dinner / Social (DN / EC)", "notes": "Juicy pear, orange blossom, and Akigalawood."}
            col_4 = {"name": "GA Acqua Di Gio Profondo", "role": "High-Heat Outdoor Shield (LO / EC)", "notes": "Deep mineral marine accords and green mandarin."} if len(target_badges) >= 3 else None
        elif "Winter" in t_band:
            col_1 = {"name": "Givenchy Gentleman Society", "role": "Universal Boardroom King (WP / DN)", "notes": "Cardamom, French clary sage, vetiver trio, and dark vanilla."}
            col_2 = {"name": "Alt. Pristine (Aventus x BR540)", "role": "Daytime Luminous Aristocrat (WP / EC)", "notes": "Crisp pineapple, smoky birch, burnt sugar saffron, and amberwood."}
            col_3 = {"name": "D&G The One for Men", "role": "Intimate Date Night & Dinner (DN)", "notes": "Warm cardamom, fresh ginger, cured tobacco, and cozy amber."}
            col_4 = {"name": "HOK Nomade Ember", "role": "Sub-Freezing Nightlife Weapon (NL / DN)", "notes": "Smoked agarwood, incense tears, sweet raspberry, and raw leather."} if "NL" in target_badges else None
        else: # Transitional Seasons (Current DMV & Travel Baseline)
            col_1 = {"name": "Givenchy Gentleman Society", "role": "The Boardroom Anchor (WP / DN)", "notes": "Cardamom, French sage, vetiver, and dark vanilla; effortless authority."}
            col_2 = {"name": "Alt. Identity (YSL MYSLF DNA)", "role": "Modern Contemporary Daily (WP / EC)", "notes": "Calabrian bergamot, orange blossom, and clean Ambrofix."}
            col_3 = {"name": "Alt. Blue Fate (Blue Talisman DNA)", "role": "The Magnetic Social Bridge (DN / EC / LO)", "notes": "Juicy pear, fresh ginger, ambroxan, and Akigalawood."}
            if "NL" in target_badges:
                col_4 = {"name": "Alt. Farouche Elixir (Sauvage Elixir DNA)", "role": "Nightlife & Beast Mode (NL)", "notes": "Fiery Sichuan pepper, nutmeg, cinnamon, and rich lavender."}
            elif "LO" in target_badges:
                col_4 = {"name": "Alt. Reality (LV Imagination DNA)", "role": "Open-Air Waterfront / Patio (LO / EC)", "notes": "Sparkling black tea, ginger, and ambroxan."}
            else:
                col_4 = {"name": "Gucci Guilty Pour Homme", "role": "Refined Barbershop Backup (WP / EC / DN)", "notes": "French lavender, Italian lemon, and cedarwood."}

        # Render Base Anchor Box
        st.markdown(f"""
        <div class="capsule-card">
            <span class="badge-tag">FOUNDATION ANCHOR</span>
            <h3 style="color: #58A6FF; margin: 4px 0;">{base_1}</h3>
            <p style="margin: 0; font-size: 13.5px; color: #8B949E;">{base_1_desc}</p>
            {f'<hr style="border-color: #30363D; margin: 8px 0;"><h4 style="color: #BC8CFF; margin: 4px 0;">{base_2}</h4><p style="margin: 0; font-size: 13.5px; color: #8B949E;">{base_2_desc}</p>' if base_2 else ''}
        </div>
        """, unsafe_allow_html=True)
        
        # Render 3-4 Colognes
        colognes_list = [c for c in [col_1, col_2, col_3, col_4] if c is not None]
        st.write(f"**Selected {len(colognes_list)}-Bottle Travel Roster:**")
        
        for i, c in enumerate(colognes_list, 1):
            st.markdown(f"""
            <div style="background-color: #161B22; border-left: 4px solid #58A6FF; border-top: 1px solid #30363D; border-right: 1px solid #30363D; border-bottom: 1px solid #30363D; border-radius: 6px; padding: 10px 14px; margin-bottom: 8px;">
                <div style="font-size: 14.5px; font-weight: 600; color: #E6EDF3;">
                    Bottle #{i}: <span style="color: #58A6FF;">{c['name']}</span> 
                    <span style="font-size: 11px; color: #8B949E; margin-left: 8px;">({c['role']})</span>
                </div>
                <div style="font-size: 12.5px; color: #8B949E; margin-top: 2px;">{c['notes']}</div>
            </div>
            """, unsafe_allow_html=True)
            
        # Deployment Matrix on Trip
        st.markdown("---")
        st.subheader("3. Trip Scenario Deployment Playbook")
        
        playbook_data = []
        for badge in target_badges:
            if badge == "WP":
                playbook_data.append({
                    "Scenario": "💼 Work & Meetings",
                    "Deployment Recipe": f"{base_1} + {col_1['name']}",
                    "Sillage Cap": "3–4 ft (Office Safe)",
                    "Strategic Rationale": "Crisp, authoritative woody-aromatic trail; zero cloying sweetness in boardroom."
                })
            elif badge == "EC":
                playbook_data.append({
                    "Scenario": "☕ Casual Daytime & Transit",
                    "Deployment Recipe": f"Unscented Canvas + {col_2['name']} (Solo)",
                    "Sillage Cap": "2–3 ft (Clean Bubble)",
                    "Strategic Rationale": "Modern sparkling florals or tea; refreshing and inoffensive during flights or errands."
                })
            elif badge == "DN":
                playbook_data.append({
                    "Scenario": "🍸 Dinner & Date Night",
                    "Deployment Recipe": f"{base_1} + {col_3['name']}",
                    "Sillage Cap": "3–4 ft (Magnetic)",
                    "Strategic Rationale": "Luminous fruit, ginger, or warm spices that draw in close proximity across a dinner table."
                })
            elif badge == "NL" and col_4:
                playbook_data.append({
                    "Scenario": "🪩 Nightlife & Lounges",
                    "Deployment Recipe": f"{base_2 if base_2 else base_1} + {col_4['name']}",
                    "Sillage Cap": "6–8 ft (Beast Mode)",
                    "Strategic Rationale": "High-impact spices and woods that slice through crowded evening social clubs."
                })
            elif badge == "LO" and col_4:
                playbook_data.append({
                    "Scenario": "🌊 Waterfront & Outdoors",
                    "Deployment Recipe": f"{base_1} + {col_4['name']}",
                    "Sillage Cap": "4–6 ft (Open-Air)",
                    "Strategic Rationale": "Resilient mineral or tea accords that cut through river breezes without fading."
                })
                
        if playbook_data:
            st.table(pd.DataFrame(playbook_data))

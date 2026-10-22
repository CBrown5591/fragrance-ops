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
    .sartorial-card {
        background: #161B22;
        border: 1px solid #30363D;
        border-radius: 10px;
        padding: 18px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.35);
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

# Master Verified Standalone Fragrances Roster
STANDALONE_MASTER = [
    {"Custom Profile Name": "The Crisp Blue Alpha", "Top Layer": "Alt. A (YSL Y DNA)", "Pairing Type": "Standalone Solo Wear", "Base Layer": "None (Unscented Canvas)", "Particle Primer Compatible": "Yes", "Eligible Scenarios": "WP, EC, LO, NL", "Projection Strength": "Strong (5–6 ft / 4 sp cap)", "Scent Profile & Notes Breakdown": "Green apple, fresh ginger, clary sage, and clean amberwood. Sharp, energetic boardroom daily workhorse.", "Season_Sheet": "All-Season (6-Band Universal)"},
    {"Custom Profile Name": "The Luminous Modern Executive", "Top Layer": "Alt. Blue Fate (Blue Talisman DNA)", "Pairing Type": "Standalone Solo Wear", "Base Layer": "None (Unscented Canvas)", "Particle Primer Compatible": "Yes", "Eligible Scenarios": "WP, EC, DN, LO", "Projection Strength": "Strong (5–6 ft / 3-4 sp cap)", "Scent Profile & Notes Breakdown": "Juicy pear, bergamot, ginger, and radiant ambroxan/Akigalawood. Modern, luminous executive aura.", "Season_Sheet": "Spring / Summer / Early Fall"},
    {"Custom Profile Name": "The Sovereign Society Executive", "Top Layer": "Givenchy Gentleman Society", "Pairing Type": "Standalone Solo Wear", "Base Layer": "None (Unscented Canvas)", "Particle Primer Compatible": "Yes", "Eligible Scenarios": "WP, DN, NL", "Projection Strength": "Strong (5–6 ft / 4 sp cap)", "Scent Profile & Notes Breakdown": "Cardamom, French clary sage, wild narcissus, Haitian vetiver, and dark vanilla. Universal boardroom king.", "Season_Sheet": "All-Season (6-Band Universal)"},
    {"Custom Profile Name": "The High-Tech Corporate Mind", "Top Layer": "Givenchy Pi Neo", "Pairing Type": "Standalone Solo Wear", "Base Layer": "None (Unscented Canvas)", "Particle Primer Compatible": "Yes", "Eligible Scenarios": "WP, EC", "Projection Strength": "Moderate (3–4 ft)", "Scent Profile & Notes Breakdown": "Mandarin, bergamot, herbal myrtle, crystalline cedarwood, and patchouli. Clean, tailored high-tech office cool.", "Season_Sheet": "Pre-Spring / Spring / Early Fall"},
    {"Custom Profile Name": "The Modern Mineral Aristocrat", "Top Layer": "Valentino Uomo Born in Roma", "Pairing Type": "Standalone Solo Wear", "Base Layer": "None (Unscented Canvas)", "Particle Primer Compatible": "Yes", "Eligible Scenarios": "WP, EC, DN", "Projection Strength": "Moderate (3–4 ft)", "Scent Profile & Notes Breakdown": "Mineral salt accord, violet leaf, fresh ginger, aromatic sage, and smoky vetiver. Modern street-tailored edge.", "Season_Sheet": "Pre-Spring / Spring / Early Fall"},
    {"Custom Profile Name": "The Alpine Aristocrat", "Top Layer": "Alt. Pristine (Aventus x BR540)", "Pairing Type": "Standalone Solo Wear", "Base Layer": "None (Unscented Canvas)", "Particle Primer Compatible": "Yes", "Eligible Scenarios": "WP, EC, DN, NL", "Projection Strength": "Moderate to Strong (4–5 ft)", "Scent Profile & Notes Breakdown": "Crisp pineapple, smoky birch, burnt sugar saffron, and radiant amberwood. Pristine modern luxury trail.", "Season_Sheet": "Pre-Spring / Spring / Fall"},
    {"Custom Profile Name": "The Seductive Modern Barbershop", "Top Layer": "Gucci Guilty Pour Homme", "Pairing Type": "Standalone Solo Wear", "Base Layer": "None (Unscented Canvas)", "Particle Primer Compatible": "Yes", "Eligible Scenarios": "WP, EC, DN", "Projection Strength": "Moderate (3 ft)", "Scent Profile & Notes Breakdown": "Italian lemon, French lavender, orange blossom, and structured cedarwood/patchouli. Refined clean desk grooming.", "Season_Sheet": "Pre-Spring / Spring / Early Fall"},
    {"Custom Profile Name": "The Luminous Imperial Tea", "Top Layer": "Alt. Reality (LV Imagination DNA)", "Pairing Type": "Standalone Solo Wear", "Base Layer": "None (Unscented Canvas)", "Particle Primer Compatible": "Yes", "Eligible Scenarios": "WP, EC, LO", "Projection Strength": "Moderate (3–4 ft)", "Scent Profile & Notes Breakdown": "Chinese black tea, Sicilian citrus, fresh ginger, and sparkling ambroxan. Spa-like executive refinement.", "Season_Sheet": "Spring / High Summer / Early Fall"},
    {"Custom Profile Name": "The Modern Floral Executive", "Top Layer": "Alt. Identity (YSL MYSLF DNA)", "Pairing Type": "Standalone Solo Wear", "Base Layer": "None (Unscented Canvas)", "Particle Primer Compatible": "Yes", "Eligible Scenarios": "WP, EC, DN", "Projection Strength": "Moderate (3–4 ft)", "Scent Profile & Notes Breakdown": "Calabrian bergamot, orange blossom absolute, and crisp Ambrofix. Tailored contemporary executive daily.", "Season_Sheet": "Spring / Summer / Early Fall"},
    {"Custom Profile Name": "The Gunmetal Assassin", "Top Layer": "John Wick x Scentbird", "Pairing Type": "Standalone Solo Wear", "Base Layer": "None (Unscented Canvas)", "Particle Primer Compatible": "Yes", "Eligible Scenarios": "WP, DN, NL", "Projection Strength": "Moderate to Strong (4–5 ft)", "Scent Profile & Notes Breakdown": "Cold gunmetal slide accord, spiced lemon, clary sage, and rich amber bourbon over cedar. Disciplined authority.", "Season_Sheet": "Pre-Spring / Fall / Early Winter"},
    {"Custom Profile Name": "The Deep Abyssal Ocean", "Top Layer": "GA Acqua Di Gio Profondo", "Pairing Type": "Standalone Solo Wear", "Base Layer": "None (Unscented Canvas)", "Particle Primer Compatible": "Yes", "Eligible Scenarios": "WP, EC, LO", "Projection Strength": "Strong (5–6 ft)", "Scent Profile & Notes Breakdown": "Deep mineral marine notes, green mandarin, rosemary, and blue cypress. Summer heat & office humidity defense.", "Season_Sheet": "High Summer / Warm Spring"},
    {"Custom Profile Name": "The Golden Gourmand Sovereign", "Top Layer": "Givenchy Pi", "Pairing Type": "Standalone Solo Wear", "Base Layer": "None (Unscented Canvas)", "Particle Primer Compatible": "No", "Eligible Scenarios": "DN, EC, WP", "Projection Strength": "Moderate to Strong (4–5 ft)", "Scent Profile & Notes Breakdown": "Sweet almond, benzoin, tonka bean, and roasted vanilla. Sentimental warmth for cold weather and close quarters.", "Season_Sheet": "Crisp Fall / Deep Winter"},
    {"Custom Profile Name": "The Intimate Tobacco Seduction", "Top Layer": "D&G The One for Men", "Pairing Type": "Standalone Solo Wear", "Base Layer": "None (Unscented Canvas)", "Particle Primer Compatible": "Yes", "Eligible Scenarios": "DN, WP", "Projection Strength": "Intimate to Moderate (2–3 ft)", "Scent Profile & Notes Breakdown": "Warm cardamom, fresh ginger, cured tobacco, and cozy amber. Close-proximity evening & date night benchmark.", "Season_Sheet": "Early Fall / Crisp Fall / Deep Winter"},
    {"Custom Profile Name": "The Authentic Caribbean King", "Top Layer": "Creed Virgin Island Water", "Pairing Type": "Standalone Solo Wear", "Base Layer": "None (Unscented Canvas)", "Particle Primer Compatible": "Yes", "Eligible Scenarios": "LO, EC", "Projection Strength": "Moderate (3–4 ft)", "Scent Profile & Notes Breakdown": "Crisp Jamaican lime zest, coconut water, white rum, and sugar cane. High-heat resort and beach staple.", "Season_Sheet": "High Summer / Vacation"},
    {"Custom Profile Name": "The Desert Oud Monarch", "Top Layer": "House of Kelam (HOK) Nomade Ember", "Pairing Type": "Standalone Solo Wear", "Base Layer": "None (Unscented Canvas)", "Particle Primer Compatible": "No", "Eligible Scenarios": "NL, DN", "Projection Strength": "Nuclear / Beast Mode (8+ ft / 2 sp cap)", "Scent Profile & Notes Breakdown": "Smoked agarwood, incense tears, sweet tart raspberry, and raw leather. Cold-weather formal evening galas.", "Season_Sheet": "Deep Winter / Late Fall"},
    {"Custom Profile Name": "The Sovereign Agarwood Suite", "Top Layer": "House of Kelam (HOK) Oud Noir", "Pairing Type": "Standalone Solo Wear", "Base Layer": "None (Unscented Canvas)", "Particle Primer Compatible": "Yes", "Eligible Scenarios": "WP, DN, NL", "Projection Strength": "Strong (5–6 ft)", "Scent Profile & Notes Breakdown": "Precious agarwood, rosewood, cardamom, Sichuan pepper, and smoky amber. Boardroom authority.", "Season_Sheet": "Deep Winter / Pre-Spring / Crisp Fall"},
    {"Custom Profile Name": "The Tactical Ambroxan Alpha", "Top Layer": "Dior Sauvage (EDT/EDP)", "Pairing Type": "Standalone Solo Wear", "Base Layer": "None (Unscented Canvas)", "Particle Primer Compatible": "Yes", "Eligible Scenarios": "WP, EC, NL", "Projection Strength": "Strong (5–6 ft / 3 sp cap)", "Scent Profile & Notes Breakdown": "Calabrian bergamot, Sichuan pepper, geranium, and clean metallic ambroxan. Pressed white shirt projection engine.", "Season_Sheet": "All-Season (6-Band Universal)"},
    {"Custom Profile Name": "The Mediterranean Blue Powerhouse", "Top Layer": "Versace Dylan Blue", "Pairing Type": "Standalone Solo Wear", "Base Layer": "None (Unscented Canvas)", "Particle Primer Compatible": "No", "Eligible Scenarios": "WP, EC, NL", "Projection Strength": "Strong (5–6 ft)", "Scent Profile & Notes Breakdown": "Aquatic citrus, violet leaf, black pepper, ambroxan, and incense. Clean modern power daily.", "Season_Sheet": "Spring / Summer / Early Fall"},
    {"Custom Profile Name": "The Boozy Oak Aristocrat", "Top Layer": "B&BW Whiskey Reserve (Cologne)", "Pairing Type": "Standalone Solo Wear", "Base Layer": "None (Unscented Canvas)", "Particle Primer Compatible": "Yes", "Eligible Scenarios": "WP, EC, DN", "Projection Strength": "Moderate to Strong (4–5 ft)", "Scent Profile & Notes Breakdown": "Crisp red apple, single malt whiskey, and aged white oak barrel staves. Rustic autumn refinement.", "Season_Sheet": "Early Fall / Crisp Fall"}
]

@st.cache_data(ttl=300, show_spinner="Syncing with Fragrance Matrix in Google Drive...")
def fetch_matrix_from_drive():
    """
    Connects to Google Drive using Streamlit Secrets.
    Ingests pairing worksheets and merges with standalone solo wears.
    """
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
            # Combine pairing matrix with standalone solo wears
            combined = pd.concat([master, solo_df], ignore_index=True)
            return combined
            
        return pd.concat([get_fallback_dataframe(), solo_df], ignore_index=True)
    except Exception as e:
        st.sidebar.error(f"Google Drive Sync Notice: {e}")
        return pd.concat([get_fallback_dataframe(), solo_df], ignore_index=True)

def clean_matrix_columns(df):
    """Standardizes column headers across sheets."""
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
    """Provides verified layering rows if Google Drive is offline."""
    data = [
        {"Season_Sheet": "Early Fall (Transitional 58°F – 72°F)", "Pairing Type": "Body Cream Layer", "Base Layer": "Graphite Cream", "Particle Primer Compatible": "Yes", "Top Layer": "Givenchy Gentleman Society", "Custom Profile Name": "The Modern Herbal Executive", "Eligible Scenarios": "WP, DN", "Projection Strength": "Strong (5–6 ft / 4 sp cap)", "Scent Profile & Notes Breakdown": "French sage mirrors Society sage; leatherwood grounds vetiver and cedarwood."},
        {"Season_Sheet": "Early Fall (Transitional 58°F – 72°F)", "Pairing Type": "Body Cream Layer", "Base Layer": "Graphite Cream", "Particle Primer Compatible": "Yes", "Top Layer": "Gucci Guilty Pour Homme", "Custom Profile Name": "The High-Style Executive", "Eligible Scenarios": "WP, DN, EC", "Projection Strength": "Moderate (3 ft)", "Scent Profile & Notes Breakdown": "French lavender and lemon slice through thawing chill over structured leatherwood."},
        {"Season_Sheet": "Early Fall (Transitional 58°F – 72°F)", "Pairing Type": "Body Cream Layer", "Base Layer": "Graphite Cream", "Particle Primer Compatible": "Yes", "Top Layer": "Alt. Identity (YSL MYSLF)", "Custom Profile Name": "The Tailored Contemporary Alpha", "Eligible Scenarios": "WP, EC, DN", "Projection Strength": "Moderate (3–4 ft)", "Scent Profile & Notes Breakdown": "Aromatic sage and bergamot contrast clean orange blossom and Ambrofix."},
        {"Season_Sheet": "Crisp Fall (45°F – 60°F)", "Pairing Type": "Body Cream Layer", "Base Layer": "Mahogany Teakwood", "Particle Primer Compatible": "Yes", "Top Layer": "Alt A (YSL Y)", "Custom Profile Name": "The Power Blue Executive", "Eligible Scenarios": "WP, EC", "Projection Strength": "Moderate to Strong (4–5 ft)", "Scent Profile & Notes Breakdown": "Crisp green apple, ginger, and sage anchored by dense mahogany and teakwood."},
        {"Season_Sheet": "Spring (Warming 55°F – 70°F)", "Pairing Type": "Cologne Mixology", "Base Layer": "Alt. Splish (D&G Light Blue)", "Particle Primer Compatible": "Yes", "Top Layer": "Alt. Reality (LV Imagination)", "Custom Profile Name": "The Sicilian Citrus Tea", "Eligible Scenarios": "EC, WP, LO", "Projection Strength": "Moderate (3–4 ft)", "Scent Profile & Notes Breakdown": "Mandarin and grapefruit peel blend into black tea, ginger, and ambroxan."},
        {"Season_Sheet": "High Summer (75°F – 95°F+)", "Pairing Type": "Body Cream Layer", "Base Layer": "Ocean Cream", "Particle Primer Compatible": "Yes", "Top Layer": "Alt. Blue Fate (Blue Talisman)", "Custom Profile Name": "The Luminous Azure Sea", "Eligible Scenarios": "EC, WP, LO", "Projection Strength": "Moderate to Strong (4–5 ft)", "Scent Profile & Notes Breakdown": "Juicy pear and Akigalawood float over coastal air and blue cypress."}
    ]
    return pd.DataFrame(data)

# ---------------------------------------------------------
# METEOROLOGICAL & GEOLOCATION LAYER
# ---------------------------------------------------------
PRESET_CITIES = {
    "Washington, D.C.": {"lat": 38.9072, "lon": -77.0369},
    "New York, NY": {"lat": 40.7128, "lon": -74.0060},
    "Miami, FL": {"lat": 25.7617, "lon": -80.1918},
    "Atlanta, GA": {"lat": 33.7490, "lon": -84.3880},
    "Chicago, IL": {"lat": 41.8781, "lon": -87.6298},
    "Los Angeles, CA": {"lat": 34.0522, "lon": -118.2437}
}

@st.cache_data(ttl=900)
def get_live_weather(lat, lon):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&temperature_unit=fahrenheit"
    try:
        r = requests.get(url, timeout=5).json()
        curr = r.get("current_weather", {})
        temp = float(curr.get("temperature", 65.0))
        wind = float(curr.get("windspeed", 5.0))
        return temp, wind
    except Exception:
        return 65.0, 5.0

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

def determine_seasonal_band(temp):
    if temp < 45:
        return "Deep Winter (< 45°F)"
    elif 45 <= temp <= 58:
        return "Pre-Spring (Transitional 45°F – 58°F) / Crisp Fall"
    elif 58 < temp <= 72:
        return "Early Fall (Transitional 58°F – 72°F) / Spring Warming"
    else:
        return "High Summer (75°F – 95°F+)"

# ---------------------------------------------------------
# SARTORIAL COLOR MATCHING REGISTRY
# ---------------------------------------------------------
SARTORIAL_MAP = {
    "The Crisp Blue Alpha": {"name": "Deep Navy & Crisp Gunmetal", "primary": "#0D2A6B", "accent": "#5A6570", "styling": "Crisp blue aromatic lift over modern tailored grey suiting."},
    "The Luminous Modern Executive": {"name": "Slate Charcoal & Soft Lavender", "primary": "#2B303A", "accent": "#9E97A9", "styling": "Modern ambroxan and orange blossom over tailored slate."},
    "The Sovereign Society Executive": {"name": "Midnight Navy & Cardamom Bronze", "primary": "#1A2238", "accent": "#A3704C", "styling": "Rich narcissus and dark vanilla over deep executive navy."},
    "The High-Tech Corporate Mind": {"name": "Slate Olive & Sunlit Amber", "primary": "#3B443B", "accent": "#D9822B", "styling": "Herbal myrtle and cedar balanced by energetic mandarin."},
    "The Modern Mineral Aristocrat": {"name": "Mineral Slate & Smoked Sage", "primary": "#3C4A57", "accent": "#8A9A86", "styling": "Mineral salt and clary sage over muted herbal earth."},
    "The Alpine Aristocrat": {"name": "Deep Teak Brown & Alpine Silver", "primary": "#2E1F18", "accent": "#D6DBDF", "styling": "Polished dark timber balancing frosty green tea air."},
    "The Seductive Modern Barbershop": {"name": "Charcoal Wool & French Lilac", "primary": "#33383B", "accent": "#92849E", "styling": "Clean orange blossom and French lavender over dark suiting."},
    "The Luminous Imperial Tea": {"name": "Black Tea Amber & Cool Slate", "primary": "#8C4A28", "accent": "#4A5868", "styling": "Chinese black tea and ginger grounded in tailored slate."},
    "The Modern Floral Executive": {"name": "Slate Charcoal & Soft Lilac", "primary": "#2C3038", "accent": "#A394AA", "styling": "Clean orange blossom and Ambrofix over dark structured slate."},
    "The Gunmetal Assassin": {"name": "Gunmetal Steel & Bourbon Ochre", "primary": "#3A3E45", "accent": "#B5732A", "styling": "Cold metallic slide and amber bourbon over tactical wool."},
    "The Deep Abyssal Ocean": {"name": "Deep Nautical Navy & Mineral Sea Grey", "primary": "#122038", "accent": "#8898A6", "styling": "Salty marine accords and green mandarin over abyssal navy."},
    "The Golden Gourmand Sovereign": {"name": "Dark Espresso & Warm Honey Tan", "primary": "#281D17", "accent": "#C48D47", "styling": "Sweet almond and benzoin resting on dark roasted espresso."},
    "The Intimate Tobacco Seduction": {"name": "Espresso & Spiced Cognac", "primary": "#2A1D15", "accent": "#9E5A2A", "styling": "Cozy tobacco and ginger over rich brown knitwear."},
    "The Authentic Caribbean King": {"name": "Palm Green & Coconut Shell Tan", "primary": "#324A38", "accent": "#9C7A58", "styling": "Lime zest, sugar cane, and white rum in island earth tones."},
    "The Desert Oud Monarch": {"name": "Midnight Black & Desert Crimson", "primary": "#1A1A1A", "accent": "#801B2B", "styling": "Smoky oud and sweet raspberry over sleek nocturnal darks."},
    "The Sovereign Agarwood Suite": {"name": "Smoked Charcoal & Rosewood Bronze", "primary": "#2B2D33", "accent": "#8C4F47", "styling": "Agarwood, rosewood, and cardamom in a sovereign corporate cut."},
    "The Tactical Ambroxan Alpha": {"name": "Tactical Gunmetal & Electric Bergamot Blue", "primary": "#2A2C2E", "accent": "#3A6B88", "styling": "Fiery Sichuan pepper and ambroxan over dark technical gear."},
    "The Mediterranean Blue Powerhouse": {"name": "Midnight Blue & Smoked Incense Grey", "primary": "#121F38", "accent": "#525B66", "styling": "Aquatic citrus, violet leaf, and incense in sharp contrast."},
    "The Boozy Oak Aristocrat": {"name": "Rich Cognac & Dark Oak Charcoal", "primary": "#8C4820", "accent": "#2A2E33", "styling": "Crisp apple and single malt whiskey over structured dark wool."}
}

DEFAULT_PALETTE = {"name": "Classic Executive Slate & White", "primary": "#2F3E46", "accent": "#F8F9FA", "styling": "Clean tailored neutral wardrobe with subtle brushed steel accent."}

# ---------------------------------------------------------
# SIDEBAR CONTROLS
# ---------------------------------------------------------
with st.sidebar:
    st.image("https://images.unsplash.com/photo-1592945403244-b3fbafd7f539?w=500&auto=format&fit=crop&q=60", use_container_width=True)
    st.title("Fragrance Ops")
    st.caption("Live Google Drive Matrix • Climate Engine")
    st.markdown("---")
    
    st.subheader("⚙️ Deployment Mode")
    rotation_mode = st.radio(
        "Daily Briefing Bias",
        ["🔄 Full Wardrobe (Mixology + Solo)", "🎯 Standalone Solo Only", "🧪 Layering & Mixology Only"],
        index=0
    )
    
    st.markdown("---")
    st.subheader("📍 Location Mode")
    loc_mode = st.radio(
        "Source",
        ["📱 Phone GPS (Live)", "🏙️ City Presets / Manual"],
        index=0 if HAS_GEOLOCATION else 1
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
    else:
        selected_city = st.selectbox("Select Preset", list(PRESET_CITIES.keys()), index=0)
        current_lat = PRESET_CITIES[selected_city]["lat"]
        current_lon = PRESET_CITIES[selected_city]["lon"]
        active_location_label = f"🏙️ {selected_city}"

    # Fetch live weather
    temp, wind = get_live_weather(current_lat, current_lon)
    active_band = determine_seasonal_band(temp)
    
    st.markdown("---")
    st.metric("Live Ambient Temp", f"{temp:.1f} °F", f"Wind: {wind} mph")
    st.caption(f"Location: **{active_location_label}**")
    st.info(f"**Target Seasonal Band:** {active_band}")
    
    if st.button("🔄 Sync with Google Drive Now"):
        st.cache_data.clear()
        st.success("Cache refreshed from Google Drive!")

# Load Master Matrix
matrix_df = fetch_matrix_from_drive()

# ---------------------------------------------------------
# MAIN APP TABS
# ---------------------------------------------------------
tab_briefing, tab_explorer, tab_directory = st.tabs([
    "👔 Daily Briefing & Ops",
    "🔍 Matrix Explorer & Generator",
    "📖 Standalone Directory"
])

# ---------------------------------------------------------
# TAB 1: DAILY BRIEFING & OPS
# ---------------------------------------------------------
with tab_briefing:
    st.header("Daily Operational Scent Briefing")
    st.caption(f"Atmospheric thermodynamics locked to {active_location_label} ({temp:.1f}°F).")
    
    # Filter based on rotation mode selection
    candidate_df = matrix_df.copy()
    if rotation_mode == "🎯 Standalone Solo Only":
        candidate_df = candidate_df[candidate_df["Pairing Type"] == "Standalone Solo Wear"]
    elif rotation_mode == "🧪 Layering & Mixology Only":
        candidate_df = candidate_df[candidate_df["Pairing Type"] != "Standalone Solo Wear"]
    
    # Filter matrix for office safe combinations (WP or EC)
    scen_col = candidate_df.get("Eligible Scenarios", pd.Series([], dtype=str))
    office_df = candidate_df[
        scen_col.str.contains("WP", case=False, na=False) |
        scen_col.str.contains("EC", case=False, na=False)
    ]
    
    if office_df.empty:
        office_df = candidate_df
    
    if not office_df.empty:
        today_num = datetime.date.today().toordinal()
        random.seed(today_num + int(temp))
        daily_idx = random.randint(0, len(office_df) - 1)
        daily_choice = office_df.iloc[daily_idx]
        
        def safe_val(val, fallback="N/A"):
            s = str(val).strip()
            return fallback if not s or s.lower() == "nan" else s

        profile_name = safe_val(daily_choice.get("Custom Profile Name"), "Custom Executive Profile")
        pairing_type = safe_val(daily_choice.get("Pairing Type"), "Standalone Solo Wear")
        base_layer = safe_val(daily_choice.get("Base Layer"), "None (Unscented Canvas)")
        top_layer = safe_val(daily_choice.get("Top Layer"), "Givenchy Gentleman Society")
        primer_compat = safe_val(daily_choice.get("Particle Primer Compatible"), "Yes")
        projection = safe_val(daily_choice.get("Projection Strength"), "Moderate (3–4 ft)")
        scent_notes = safe_val(daily_choice.get("Scent Profile & Notes Breakdown"), "Single-bottle natural progression worn over an unscented moisturizing canvas.")
        
        # Determine Canvas
        is_solo = (pairing_type == "Standalone Solo Wear" or "none" in base_layer.lower())
        canvas_base = "Unscented Body Butter" if temp < 65 else "Unscented Body Lotion"
        
        if is_solo:
            canvas_recommendation = f"{canvas_base} (Clean Canvas Prep)"
            canvas_reason = "Crucial blank canvas: Locks in baseline moisture and binds the single fragrance's volatile top notes without altering its authentic note pyramid."
        else:
            canvas_recommendation = f"{canvas_base} Base + {base_layer}"
            canvas_reason = "Binds volatile base timbers and leatherwood against crisp damp air." if temp < 65 else "Lightweight hydration preventing heavy oils from suffocating under warmer ambient heat."
        
        sartorial = SARTORIAL_MAP.get(profile_name, DEFAULT_PALETTE)
        badge_style = "badge-solo" if is_solo else "badge-tag"
        
        col1, col2 = st.columns([1.8, 1.2])
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <span class="{badge_style}">{"🎯 SOLO WEAR" if is_solo else "🧪 LAYERING PICK"}</span>
                <span class="badge-tag">{pairing_type}</span>
                <span class="badge-tag">Primer: {primer_compat}</span>
                <h2 style="color: #58A6FF; margin-top: 8px; font-weight: 700;">{profile_name}</h2>
                <p style="font-size: 15.5px; margin-bottom: 6px;">
                    <strong>{'Selected Fragrance' if is_solo else 'Top Layer'}:</strong> <span style="color: #58A6FF; font-weight: 600;">{top_layer}</span><br>
                    <strong>Base Preparation:</strong> {base_layer}
                </p>
                <p style="font-style: italic; color: #8B949E; font-size: 13.5px;">"{scent_notes}"</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.subheader("🎯 Application Strategy")
            st.write(f"- **Projection Cap:** {projection}")
            if is_solo:
                st.write("- **Spray Distribution:** 3–4 sprays total (1 behind each ear, 1 center collarbone over unscented canvas, 1 back of neck).")
            else:
                st.write("- **Spray Distribution:** 4 sprays total (1 behind each ear, 1 center chest directly over cream canvas, 1 across collar/lapel).")
            st.write(f"- **Grooming Canvas:** **{canvas_recommendation}**")
            st.caption(f"*{canvas_reason}*")

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
            if st.button("Generate Alternative Recipe"):
                st.rerun()
    else:
        st.warning("No pairing recipes found in the active matrix sheets. Please verify your Google Sheet tabs.")

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
        scenarios = ["All Scenarios", "WP (Work & Professional)", "EC (Everyday & Casual)", "DN (Date Night & Evening)", "NL (Nightlife & Lounges)", "LO (Leisure & Outdoors)"]
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

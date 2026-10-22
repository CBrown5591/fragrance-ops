import streamlit as st
import pandas as pd
import requests
import datetime
import random
import re
import gspread
from google.oauth2.service_account import Credentials

# ---------------------------------------------------------
# PAGE CONFIGURATION & STYLING
# ---------------------------------------------------------
st.set_page_config(
    page_title="Fragrance Ops Command Center",
    page_icon="🧴",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 16px;
        border-left: 5px solid #1F497D;
        margin-bottom: 12px;
    }
    .swatch-box {
        display: inline-block;
        width: 22px;
        height: 22px;
        border-radius: 4px;
        vertical-align: middle;
        margin-right: 8px;
        border: 1px solid #ccc;
    }
    .badge-tag {
        display: inline-block;
        padding: 3px 8px;
        border-radius: 12px;
        font-size: 11px;
        font-weight: 600;
        background-color: #E8EEF5;
        color: #1F497D;
        margin-right: 4px;
    }
    .warning-box {
        background-color: #FFF3CD;
        border-left: 4px solid #FFA000;
        padding: 10px 14px;
        border-radius: 6px;
        margin: 10px 0;
        font-size: 13px;
        color: #664D03;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# GOOGLE SHEETS DATA LAYER
# ---------------------------------------------------------
SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

@st.cache_data(ttl=300, show_spinner="Syncing with Fragrance Matrix in Google Drive...")
def fetch_matrix_from_drive():
    """
    Connects to Google Drive using Streamlit Secrets.
    If secrets are missing, returns sample fallback dataset so the app can still be previewed.
    """
    if "gcp_service_account" not in st.secrets:
        return get_fallback_dataframe()
    
    try:
        creds = Credentials.from_service_account_info(
            st.secrets["gcp_service_account"], scopes=SCOPE
        )
        client = gspread.authorize(creds)
        sheet_name = st.secrets.get("spreadsheet_name", "Fragrance Matrix")
        spreadsheet = client.open(sheet_name)
        
        all_dfs = []
        for ws in spreadsheet.worksheets():
            records = ws.get_all_records()
            if records:
                w_df = pd.DataFrame(records)
                w_df["Season_Sheet"] = ws.title
                all_dfs.append(w_df)
        
        if all_dfs:
            master = pd.concat(all_dfs, ignore_index=True)
            return clean_matrix_columns(master)
        return get_fallback_dataframe()
    except Exception as e:
        st.sidebar.error(f"Google Drive Sync Notice: {e}")
        return get_fallback_dataframe()

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
        for standard in col_map:
            if orig.strip().lower() == standard.lower():
                df.rename(columns={orig: standard}, inplace=True)
                break
    return df

def get_fallback_dataframe():
    """Provides essential verified rows if Google Drive is temporarily disconnected."""
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
# METEOROLOGICAL TELEMETRY (OPEN-METEO)
# ---------------------------------------------------------
CITIES = {
    "Washington, D.C.": {"lat": 38.9072, "lon": -77.0369},
    "New York, NY": {"lat": 40.7128, "lon": -74.0060},
    "Miami, FL": {"lat": 25.7617, "lon": -80.1918},
    "Atlanta, GA": {"lat": 33.7490, "lon": -84.3880},
    "Chicago, IL": {"lat": 41.8781, "lon": -87.6298},
    "Los Angeles, CA": {"lat": 34.0522, "lon": -118.2437}
}

@st.cache_data(ttl=900)
def get_live_weather(lat, lon):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&hourly=relative_humidity_2m&temperature_unit=fahrenheit"
    try:
        r = requests.get(url, timeout=5).json()
        curr = r.get("current_weather", {})
        temp = curr.get("temperature", 65.0)
        wind = curr.get("windspeed", 5.0)
        return temp, wind
    except Exception:
        return 65.0, 5.0

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
    "The Modern Herbal Executive": {"name": "Executive Navy & Cardamom Bronze", "primary": "#1A2238", "accent": "#A3704C", "styling": "Suited navy trouser with bronze/gunmetal hardware."},
    "The High-Style Executive": {"name": "Charcoal Wool & French Lilac", "primary": "#2B3038", "accent": "#9E92A8", "styling": "Charcoal relaxed trousers with soft heather lilac knit."},
    "The Tailored Contemporary Alpha": {"name": "Charcoal Slate & Ice Blue", "primary": "#3E444C", "accent": "#A5C9EB", "styling": "Slate tailored trousers with crisp ice-blue dress shirt."},
    "The Power Blue Executive": {"name": "Deep French Blue & Crisp White", "primary": "#0D2A6B", "accent": "#FFFFFF", "styling": "Dark structured blazer and crisp collared poplin."},
    "The Sicilian Citrus Tea": {"name": "Earthy Olive & Sunlit Ochre", "primary": "#4A5240", "accent": "#D4A373", "styling": "Smart casual linen/knit with warm ochre wrist watch strap."}
}

DEFAULT_PALETTE = {"name": "Classic Executive Slate & White", "primary": "#2F3E46", "accent": "#F8F9FA", "styling": "Clean tailored neutral wardrobe with subtle brushed steel accent."}

# ---------------------------------------------------------
# SIDEBAR CONTROLS
# ---------------------------------------------------------
with st.sidebar:
    st.image("https://images.unsplash.com/photo-1592945403244-b3fbafd7f539?w=500&auto=format&fit=crop&q=60", use_container_width=True)
    st.title("Fragrance Ops")
    st.caption("Live Google Drive Matrix • DMV Operations")
    
    st.markdown("---")
    st.subheader("📍 Location & Climate")
    selected_city = st.selectbox("Current Location", list(CITIES.keys()), index=0)
    city_data = CITIES[selected_city]
    
    temp, wind = get_live_weather(city_data["lat"], city_data["lon"])
    active_band = determine_seasonal_band(temp)
    
    st.metric("Live Ambient Temp", f"{temp:.1f} °F", f"Wind: {wind} mph")
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
    st.caption("Automated desk-safe selection governed by today's atmospheric thermodynamics.")
    
    # Filter matrix for office safe combinations
    office_df = matrix_df[
        matrix_df["Eligible Scenarios"].str.contains("WP", case=False, na=False) |
        matrix_df["Eligible Scenarios"].str.contains("EC", case=False, na=False)
    ]
    
    if office_df.empty:
        office_df = matrix_df
        
    # Rotate by day of week or manual roll
    today_weekday = datetime.date.today().weekday()
    random.seed(today_weekday + int(temp))
    daily_choice = office_df.iloc[random.randint(0, len(office_df) - 1)]
    
    # Determine Canvas
    canvas_recommendation = "Unscented Body Butter" if temp < 65 else "Unscented Body Lotion"
    canvas_reason = "Crucial to bind volatile base timbers and leatherwood against crisp damp air." if temp < 65 else "Lightweight hydration preventing heavy oils from suffocating under warmer ambient heat."
    
    # Sartorial Match
    profile_name = daily_choice.get("Custom Profile Name", "Custom Alpha")
    sartorial = SARTORIAL_MAP.get(profile_name, DEFAULT_PALETTE)
    
    col1, col2 = st.columns([1.8, 1.2])
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <span class="badge-tag">PRIMARY WORKDAY PICK</span>
            <span class="badge-tag">{daily_choice.get('Pairing Type', 'Layering')}</span>
            <span class="badge-tag">Primer: {daily_choice.get('Particle Primer Compatible', 'Yes')}</span>
            <h2 style="color: #1F497D; margin-top: 8px;">{profile_name}</h2>
            <p><strong>Base Layer:</strong> {daily_choice.get('Base Layer', 'N/A')}<br>
            <strong>Top Layer:</strong> {daily_choice.get('Top Layer', 'N/A')}</p>
            <p style="font-style: italic; color: #4A4A4A;">"{daily_choice.get('Scent Profile & Notes Breakdown', 'N/A')}"</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.subheader("🎯 Application Strategy")
        st.write(f"- **Projection Cap:** {daily_choice.get('Projection Strength', 'Controlled Moderate (3–4 ft)')}")
        st.write("- **Spray Distribution:** 4 sprays total (1 behind each ear, 1 center chest directly over cream canvas, 1 across collar/lapel).")
        st.write(f"- **Grooming Canvas:** **{canvas_recommendation}** — *{canvas_reason}*")

    with col2:
        st.subheader("🎨 Sartorial Color Harmony")
        st.markdown(f"""
        <div style="background-color: #FAFAFA; border: 1px solid #E0E0E0; border-radius: 8px; padding: 16px;">
            <div style="font-weight: 600; font-size: 16px; margin-bottom: 8px;">{sartorial['name']}</div>
            <p style="margin: 4px 0;"><span class="swatch-box" style="background-color: {sartorial['primary']};"></span> Primary: <code>{sartorial['primary']}</code></p>
            <p style="margin: 4px 0;"><span class="swatch-box" style="background-color: {sartorial['accent']};"></span> Accent: <code>{sartorial['accent']}</code></p>
            <div style="margin-top: 10px; font-size: 13px; color: #555;">{sartorial['styling']}</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("🔄 Alternate Roll")
        if st.button("Generate Alternative Recipe"):
            st.rerun()

# ---------------------------------------------------------
# TAB 2: MATRIX EXPLORER & GENERATOR
# ---------------------------------------------------------
with tab_explorer:
    st.header("Fragrance Matrix Query Engine")
    st.caption("Filter live recipes across all seasonal brackets, scenario badges, and chemical primers.")
    
    col_f1, col_f2, col_f3 = st.columns(3)
    
    with col_f1:
        if "Season_Sheet" in matrix_df.columns:
            seasons = ["All Sheets / Bands"] + sorted(list(matrix_df["Season_Sheet"].dropna().unique()))
            chosen_season = st.selectbox("Seasonal Sheet", seasons)
        else:
            chosen_season = "All Sheets / Bands"
            
    with col_f2:
        scenarios = ["All Scenarios", "WP (Work & Professional)", "EC (Everyday & Casual)", "DN (Date Night & Evening)", "NL (Nightlife & Lounges)", "LO (Leisure & Outdoors)"]
        chosen_scen = st.selectbox("Target Scenario Badge", scenarios)
        
    with col_f3:
        primer_opt = st.selectbox("Particle Primer Compatible", ["Any", "Yes", "No"])
        
    # Filtering logic
    filtered_df = matrix_df.copy()
    if chosen_season != "All Sheets / Bands" and "Season_Sheet" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["Season_Sheet"] == chosen_season]
        
    if chosen_scen != "All Scenarios":
        badge = chosen_scen.split()[0]
        filtered_df = filtered_df[filtered_df["Eligible Scenarios"].str.contains(badge, case=False, na=False)]
        
    if primer_opt != "Any" and "Particle Primer Compatible" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["Particle Primer Compatible"].astype(str).str.strip().str.lower() == primer_opt.lower()]

    # Quick Generator Card
    st.markdown("---")
    gen_col1, gen_col2 = st.columns([2, 1])
    with gen_col1:
        st.write(f"**Matching Recipes Found:** {len(filtered_df)}")
    with gen_col2:
        if st.button("🎲 Surprise Me (Random Pair from Filter)"):
            if not filtered_df.empty:
                pick = filtered_df.sample(1).iloc[0]
                st.info(f"**Random Pick:** **{pick.get('Custom Profile Name')}** ({pick.get('Base Layer')} + {pick.get('Top Layer')})

*{pick.get('Scent Profile & Notes Breakdown')}*")
            else:
                st.warning("No entries match the current filter.")
                
    st.dataframe(
        filtered_df[['Custom Profile Name', 'Pairing Type', 'Base Layer', 'Top Layer', 'Eligible Scenarios', 'Projection Strength', 'Scent Profile & Notes Breakdown']],
        use_container_width=True,
        hide_index=True
    )
    
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
        st.dataframe(search_res[['Custom Profile Name', 'Base Layer', 'Top Layer', 'Scent Profile & Notes Breakdown']], use_container_width=True, hide_index=True)
    else:
        st.info("Type a note (e.g. 'bergamot', 'leatherwood', 'pear') or fragrance name above to query matching profiles.")

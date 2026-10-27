import base64
import datetime
import io
import os
import random
from zoneinfo import ZoneInfo
from PIL import Image
import pandas as pd
import streamlit as st

# Import modular components
from config import (
    CUSTOM_CSS,
    DEFAULT_PALETTE,
    ICON_B64,
    PRESET_CITIES,
    SCENARIO_OPTIONS,
)
from data_layer import (
    delete_locked_fit,
    fetch_matrix_from_drive,
    get_recent_wears,
    is_favorite,
    load_favorites,
    load_locked_fits,
    load_wear_history,
    log_wear,
    save_locked_fit,
    toggle_favorite,
)
from transition_engine import evaluate_evening_transition
from trip_engine import (
    delete_saved_trip,
    generate_all_playbook_combinations,
    get_capsule_recommendations,
    load_saved_trips,
    save_trip,
)
from weather_engine import (
    evaluate_thermodynamic_band,
    get_comprehensive_weather,
    reverse_geocode_coords,
    search_city_geocoding,
)

# Optional GPS Geolocation & Client Timezone Detection
try:
  from streamlit_js_eval import get_geolocation, streamlit_js_eval

  HAS_GEOLOCATION = True
except ImportError:
  HAS_GEOLOCATION = False


def resolve_client_timezone():
  """Detects user device/phone IANA timezone via browser JavaScript.

  Defaults to America/New_York (US Eastern) if headless or uninitialized.
  """
  fallback_tz = "America/New_York"
  if not HAS_GEOLOCATION:
    return ZoneInfo(fallback_tz)
  try:
    device_tz_str = streamlit_js_eval(
        js_expressions="Intl.DateTimeFormat().resolvedOptions().timeZone",
        key="device_tz_eval",
    )
    if device_tz_str and isinstance(device_tz_str, str):
      return ZoneInfo(device_tz_str.strip())
  except Exception:
    pass
  return ZoneInfo(fallback_tz)


def get_local_now(tz=None):
  if tz is None:
    tz = resolve_client_timezone()
  return datetime.datetime.now(tz)


def deduplicate_catalog(df):
  """Deduplicates recipes in-memory by (Custom Profile Name, Base Layer, Top Layer).

  Keeps Google Sheets untouched while preventing duplicate rows in Explorer and
  Directory.
  """
  if df.empty:
    return df
  subset = [
      c
      for c in ["Custom Profile Name", "Base Layer", "Top Layer"]
      if c in df.columns
  ]
  if not subset:
    return df.drop_duplicates()
  df_clean = df.copy()
  for c in subset:
    df_clean[c] = df_clean[c].astype(str).str.strip()
  return df_clean.drop_duplicates(subset=subset, keep="first")


# ---------------------------------------------------------
# PAGE SETUP & CSS INJECTION
# ---------------------------------------------------------
app_icon_img = Image.open(io.BytesIO(base64.b64decode(ICON_B64)))

st.set_page_config(
    page_title="Fragrance Ops",
    page_icon=app_icon_img,
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ---------------------------------------------------------
# SIDEBAR CONTROLS & LIVE WEATHER
# ---------------------------------------------------------
with st.sidebar:
  st.image(
      "https://images.unsplash.com/photo-1592945403244-b3fbafd7f539?w=500&auto=format&fit=crop&q=60",
      use_container_width=True,
  )
  st.title("Fragrance Ops")
  st.caption("Modular Climate Engine • Live Matrix Sync")
  st.markdown("---")

  st.subheader("⚙️ Deployment Mode")
  rotation_mode = st.radio(
      "Wardrobe Deployment",
      [
          "🔄 Full Wardrobe (Mixology + Solo)",
          "🎯 Standalone Solo Only",
          "🧪 Layering & Mixology Only",
      ],
      index=0,
  )

  st.markdown("---")
  st.subheader("📍 Location Mode")
  loc_mode = st.radio(
      "Select Mode",
      ["📱 Phone GPS (Live)", "🔍 Search Any City", "🏙️ Quick Presets"],
      index=0 if HAS_GEOLOCATION else 2,
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
    search_input = st.text_input(
        "Enter City, State or Country",
        placeholder="e.g. Philadelphia, St. Thomas, Paris...",
    )
    if search_input:
      search_matches = search_city_geocoding(search_input)
      if search_matches:
        choice = st.selectbox(
            "Matching Locations Found",
            search_matches,
            format_func=lambda x: x["label"],
        )
        current_lat = choice["lat"]
        current_lon = choice["lon"]
        active_location_label = f"🔍 {choice['label']}"
      else:
        st.warning(f"No coordinates found for '{search_input}'.")
        active_location_label = "Washington, D.C. (Default)"
    else:
      st.caption(
          "Type any destination above to query live global weather telemetry."
      )
      active_location_label = "Washington, D.C. (Default)"

  else:  # Quick Presets
    selected_city = st.selectbox(
        "Select Metro Preset", list(PRESET_CITIES.keys()), index=0
    )
    current_lat = PRESET_CITIES[selected_city]["lat"]
    current_lon = PRESET_CITIES[selected_city]["lon"]
    active_location_label = f"🏙️ {selected_city}"

  wx = get_comprehensive_weather(current_lat, current_lon)
  active_band = evaluate_thermodynamic_band(wx["temp"], wx["wind_chill"])

  st.markdown("---")
  st.subheader("🌤️ Meteorological Panel")
  delta_chill = wx["wind_chill"] - wx["temp"]
  delta_str = (
      f"Feels like {wx['wind_chill']:.1f}°F"
      if abs(delta_chill) >= 1.0
      else "Stable air"
  )
  st.metric("Live Ambient Temp", f"{wx['temp']:.1f} °F", delta_str)

  w_col1, w_col2 = st.columns(2)
  with w_col1:
    st.write(f"📈 **High:** {wx['high']:.0f}°F")
    st.write(f"📉 **Low:** {wx['low']:.0f}°F")
  with w_col2:
    st.write(f"💧 **Humidity:** {wx['humidity']}%")
    st.write(f"🌧️ **Rain:** {wx['rain_chance']}%")

  st.caption(
      f"🌬️ **Wind Speed:** {wx['wind']:.1f} mph | **Active:**"
      f" {active_location_label}"
  )
  st.info(f"**Target Seasonal Band:** {active_band}")

  if st.button("🔄 Sync with Google Drive Now"):
    st.cache_data.clear()
    st.success("Cache refreshed from Google Drive!")

# Load Master Matrix
matrix_df, sartorial_registry = fetch_matrix_from_drive()

# ---------------------------------------------------------
# MAIN APP TABS
# ---------------------------------------------------------
tab_briefing, tab_explorer, tab_directory, tab_planner = st.tabs(
    ["👔 Daily Brief", "🔍 Explorer", "📖 Directory", "🧳 Trip Planner"]
)

# ---------------------------------------------------------
# TAB 1: DAILY BRIEFING & OPS (WITH LOCK, WEAR LOG, FAVORITES, & TRANSITION)
# ---------------------------------------------------------
with tab_briefing:
  client_tz = resolve_client_timezone()
  local_now = get_local_now(client_tz)

  if "reroll_counter" not in st.session_state:
    st.session_state.reroll_counter = 0
  if "locked_fits" not in st.session_state:
    st.session_state.locked_fits = load_locked_fits()
  if "wear_history" not in st.session_state:
    st.session_state.wear_history = load_wear_history()
  if "favorites" not in st.session_state:
    st.session_state.favorites = load_favorites()

  st.markdown(
      f"""<div class="mobile-weather-bar">
<div>📍 <strong>{active_location_label}</strong></div>
<div>🌡️ <strong>{wx['temp']:.1f}°F</strong> (H: {wx['high']:.0f}° | L: {wx['low']:.0f}°) • 💧 {wx['humidity']}%</div>
</div>""",
      unsafe_allow_html=True,
  )

  today_w = local_now.weekday()
  default_idx = 0 if today_w in [0, 1, 2, 3, 4] else (1 if today_w == 5 else 4)

  selected_scenario_label = st.selectbox(
      "🎯 Operational Scenario Context",
      list(SCENARIO_OPTIONS.keys()),
      index=default_idx,
  )

  scen_meta = SCENARIO_OPTIONS[selected_scenario_label]
  target_badge = scen_meta["badge"]
  today_str = str(local_now.date())

  active_lock = st.session_state.locked_fits.get(target_badge)
  is_locked_today = (
      active_lock is not None and active_lock.get("date") == today_str
  )

  candidate_df = matrix_df.copy()
  if rotation_mode == "🎯 Standalone Solo Only":
    candidate_df = candidate_df[
        candidate_df["Pairing Type"] == "Standalone Solo Wear"
    ]
  elif rotation_mode == "🧪 Layering & Mixology Only":
    candidate_df = candidate_df[
        candidate_df["Pairing Type"] != "Standalone Solo Wear"
    ]

  scen_col = candidate_df.get("Eligible Scenarios", pd.Series([], dtype=str))
  scenario_filtered_df = candidate_df[
      scen_col.str.contains(target_badge, case=False, na=False)
  ]
  if scenario_filtered_df.empty:
    scenario_filtered_df = candidate_df

  # Weather dynamic filtering
  weather_tags = []
  if wx["humidity"] >= 70 or wx["rain_chance"] >= 35:
    weather_tags.append("🌧️ Rain/Humidity Anchor")
    damp_mask = scenario_filtered_df[
        "Scent Profile & Notes Breakdown"
    ].str.contains(
        "sage|vetiver|leatherwood|ambroxan|oak|birch|ginger|cedar|pepper",
        case=False,
        na=False,
    )
    if damp_mask.any():
      scenario_filtered_df = scenario_filtered_df[damp_mask]

  if wx["wind_chill"] < 50.0:
    weather_tags.append("❄️ Wind Chill Shield")
    chill_mask = ~scenario_filtered_df[
        "Scent Profile & Notes Breakdown"
    ].str.contains(
        "eau fraiche|frozen grapefruit|lime zest|coconut water",
        case=False,
        na=False,
    )
    if chill_mask.any():
      scenario_filtered_df = scenario_filtered_df[chill_mask]

  if wx["high"] >= 78.0:
    weather_tags.append("☀️ Warm Peak Guard")
    warm_mask = ~scenario_filtered_df[
        "Scent Profile & Notes Breakdown"
    ].str.contains(
        "tonka bean|roasted vanilla|smoked agarwood|sweet almond|incense tears",
        case=False,
        na=False,
    )
    if warm_mask.any():
      scenario_filtered_df = scenario_filtered_df[warm_mask]

  # Anti-repetition filter: Deprioritize fragrances worn in the last 3 days
  recent_wears_list = get_recent_wears(days=3)
  if not is_locked_today and len(scenario_filtered_df) > 1 and recent_wears_list:
    fresh_candidates = scenario_filtered_df[
        ~scenario_filtered_df["Top Layer"].isin(recent_wears_list)
    ]
    if not fresh_candidates.empty:
      scenario_filtered_df = fresh_candidates

  def safe_val(val, fallback="N/A"):
    s = str(val).strip()
    return fallback if not s or s.lower() == "nan" else s

  if is_locked_today:
    profile_name = active_lock["profile_name"]
    top_layer = active_lock["top_layer"]
    base_layer = active_lock["base_layer"]
    pairing_type = active_lock["pairing_type"]
    primer_compat = active_lock["primer_compat"]
    scent_notes = active_lock["scent_notes"]
    projection = active_lock.get("projection", scen_meta["cap"])
    current_opt_idx = active_lock.get("palette_idx", 0)
  elif not scenario_filtered_df.empty:
    today_num = local_now.date().toordinal()
    badge_seed = sum(ord(c) for c in target_badge)
    wx_seed = int(
        wx["temp"] * 3 + wx["humidity"] + wx["rain_chance"] + wx["wind_chill"]
    )
    total_seed = (
        today_num + wx_seed + badge_seed + st.session_state.reroll_counter
    )
    random.seed(total_seed)

    # Deterministic index for active seed + reroll counter; does not flip upon lock
    daily_idx = random.randint(0, len(scenario_filtered_df) - 1)
    daily_choice = scenario_filtered_df.iloc[daily_idx]

    profile_name = safe_val(
        daily_choice.get("Custom Profile Name"), "Custom Executive Profile"
    )
    pairing_type = safe_val(
        daily_choice.get("Pairing Type"), "Standalone Solo Wear"
    )
    base_layer = safe_val(
        daily_choice.get("Base Layer"), "None (Unscented Canvas)"
    )
    top_layer = safe_val(
        daily_choice.get("Top Layer"), "Givenchy Gentleman Society"
    )
    primer_compat = safe_val(
        daily_choice.get("Particle Primer Compatible"), "Yes"
    )
    projection = safe_val(
        daily_choice.get("Projection Strength"), scen_meta["cap"]
    )
    scent_notes = safe_val(
        daily_choice.get("Scent Profile & Notes Breakdown"),
        "Harmonious scent progression tailored to the operational scenario.",
    )

    if "palette_idx" not in st.session_state:
      st.session_state.palette_idx = 0
    current_opt_idx = st.session_state.palette_idx
  else:
    profile_name = None

  if profile_name:
    is_solo = pairing_type == "Standalone Solo Wear" or "none" in base_layer.lower()
    is_mixology = pairing_type == "Cologne Mixology"
    use_butter = wx["wind_chill"] < 65.0
    canvas_base = (
        "Unscented Body Butter" if use_butter else "Unscented Body Lotion"
    )

    if is_solo:
      canvas_recommendation = f"{canvas_base} (Clean Canvas Prep)"
      canvas_reason = (
          f"Calibrated for {wx['temp']:.1f}°F air ({wx['humidity']}%"
          " humidity). "
          f"{'Locks moisture against chill' if use_butter else 'Weightless hydration'} without competing with solo notes."
      )
    elif is_mixology:
      canvas_recommendation = f"{canvas_base} (Neutral Layering Canvas)"
      canvas_reason = (
          f"Calibrated for {wx['temp']:.1f}°F air ({wx['humidity']}%"
          " humidity). "
          "Provides a fragrance-free lipid anchor so both colognes bond to"
          " skin cleanly without olfactory clash."
      )
    else:
      canvas_recommendation = f"{base_layer} (Direct Skin Application)"
      canvas_reason = (
          "Scented cream lipids provide the foundational base notes and"
          " thermal bonding; no neutral lotion needed."
      )

    spray_strategy = scen_meta["sprays"]
    if wx["wind"] >= 10.0 or target_badge == "LO":
      spray_strategy += (
          f" *[Wind Defense: 1 extra mist across collar to counter {wx['wind']:.1f}"
          " mph shear].*"
      )

    wash_rec = (
        f"{base_layer} Body Wash"
        if (not is_solo and "none" not in base_layer.lower())
        else "Freshwater Body Wash (Clean Canvas)"
    )

    palettes = sartorial_registry.get(
        profile_name
    ) or sartorial_registry.get(f"{base_layer} + {top_layer}")
    if not palettes:
      palettes = [DEFAULT_PALETTE]
    elif isinstance(palettes, dict):
      palettes = [palettes]

    active_opt_idx = current_opt_idx % len(palettes)
    sartorial = palettes[active_opt_idx]
    opt_num_display = sartorial.get("opt_num", active_opt_idx + 1)
    total_opts = len(palettes)
    badge_style = "badge-solo" if is_solo else "badge-tag"
    is_fav = profile_name in st.session_state.favorites
    fav_badge_html = (
        '<span class="badge-tag" style="background-color: rgba(241, 196, 15,'
        ' 0.2); color: #F1C40F; border: 1px solid rgba(241, 196, 15, 0.5);">⭐'
        " FAVORITE</span>"
        if is_fav
        else ""
    )

    # Check Day-to-Evening Transition Bridge
    daytime_fit = st.session_state.locked_fits.get(
        "WP"
    ) or st.session_state.locked_fits.get("EC")
    if not daytime_fit:
      today_daytime = [
          h
          for h in st.session_state.wear_history
          if h.get("date") == today_str and h.get("scenario") in ["WP", "EC"]
      ]
      if today_daytime:
        daytime_fit = today_daytime[-1]

    if (
        target_badge in ["DN", "NL"]
        and daytime_fit
        and daytime_fit.get("top_layer") != top_layer
    ):
      trans_eval = evaluate_evening_transition(
          daytime_fit.get("top_layer", ""), top_layer
      )
      if trans_eval:
        st.markdown(
            f"""<div style="background-color: #161B22; border-left: 5px solid {trans_eval['badge_color']}; border-radius: 8px; padding: 12px 16px; margin-bottom: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.3);">
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
<strong style="color: {trans_eval['badge_color']}; font-size: 13px;">🌇 DAY-TO-EVENING TRANSITION BRIDGE</strong>
<span style="font-size: 11px; font-weight: 600; color: #8B949E;">MORNING: {daytime_fit.get('top_layer', '')}</span>
</div>
<div style="font-weight: 700; font-size: 14.5px; color: #E6EDF3; margin-bottom: 4px;">{trans_eval['status']} • {trans_eval['headline']}</div>
<div style="font-size: 13px; color: #C9D1D9; margin-bottom: 6px;">{trans_eval['guidance']}</div>
<div style="font-size: 12.5px; color: #58A6FF; font-style: italic;">🎯 Protocol: {trans_eval['protocol']}</div>
</div>""",
            unsafe_allow_html=True,
        )

    lock_status_html = (
        '<span class="locked-badge">🔒 LOCKED FOR TODAY'
        f' ({target_badge}) • {active_lock.get("locked_time", "")}</span>'
        if is_locked_today
        else ""
    )

    # Primary Recipe Card
    st.markdown(
        f"""<div class="metric-card">
<div style="margin-bottom: 6px;">
{lock_status_html}
{fav_badge_html}
<span class="badge-scenario">🎯 {target_badge} PROTOCOL</span>
<span class="{badge_style}">{"🎯 SOLO WEAR" if is_solo else "🧪 LAYERING PICK"}</span>
<span class="badge-tag">{pairing_type}</span>
<span class="badge-tag">Primer: {primer_compat}</span>
{' '.join([f'<span class="badge-weather">{tag}</span>' for tag in weather_tags])}
</div>
<h2 style="color: #58A6FF; margin-top: 6px; margin-bottom: 10px; font-weight: 700; font-size: 24px;">{profile_name}</h2>
<div style="background-color: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.06); border-radius: 8px; padding: 12px; margin-bottom: 10px;">
<p style="font-size: 16px; margin: 0 0 6px 0;">
<strong>{'Selected Fragrance' if is_solo else 'Top Layer'}:</strong> <span style="color: #58A6FF; font-weight: 600;">{top_layer}</span>
</p>
<p style="font-size: 14.5px; margin: 0; color: #C9D1D9;">
<strong>Base Preparation:</strong> {base_layer}
</p>
</div>
<p style="font-style: italic; color: #8B949E; font-size: 13.5px; margin-bottom: 0;">"{scent_notes}"</p>
</div>""",
        unsafe_allow_html=True,
    )

    # Action Row: Lock & Log Wear, Favorite, and Roll Alternative
    act_col1, act_col2, act_col3 = st.columns([1.2, 1, 1.2])
    with act_col1:
      if is_locked_today:
        if st.button(
            f"🔓 Unlock / Reshuffle ({target_badge})", use_container_width=True
        ):
          delete_locked_fit(target_badge)
          del st.session_state.locked_fits[target_badge]
          st.rerun()
      else:
        if st.button(
            f"🔒 Lock & Log ({target_badge})", use_container_width=True
        ):
          fit_info = {
              "date": today_str,
              "badge": target_badge,
              "profile_name": profile_name,
              "top_layer": top_layer,
              "base_layer": base_layer,
              "pairing_type": pairing_type,
              "primer_compat": primer_compat,
              "scent_notes": scent_notes,
              "projection": projection,
              "palette_idx": active_opt_idx,
              "locked_time": local_now.strftime("%I:%M %p"),
          }
          st.session_state.locked_fits[target_badge] = fit_info
          save_locked_fit(target_badge, fit_info)

          # Automatically trigger wear logging
          wear_payload = {
              "date": today_str,
              "scenario": target_badge,
              "profile_name": profile_name,
              "top_layer": top_layer,
              "base_layer": base_layer,
              "temp": wx["temp"],
              "palette": sartorial["name"],
              "logged_at": local_now.strftime("%I:%M %p"),
          }
          log_wear(wear_payload)
          st.session_state.wear_history = load_wear_history()
          st.toast(
              f"Locked & Logged {top_layer} for {target_badge}!", icon="🎯"
          )
          st.rerun()

    with act_col2:
      fav_btn_label = "★ Favorited" if is_fav else "☆ Favorite"
      if st.button(fav_btn_label, use_container_width=True):
        recipe_payload = {
            "profile_name": profile_name,
            "top_layer": top_layer,
            "base_layer": base_layer,
            "pairing_type": pairing_type,
            "scent_notes": scent_notes,
            "scenario": target_badge,
            "projection": projection,
        }
        added = toggle_favorite(profile_name, recipe_payload)
        st.session_state.favorites = load_favorites()
        st.toast(
            f"{'Saved to' if added else 'Removed from'} Favorites!",
            icon="⭐" if added else "🗑️",
        )
        st.rerun()

    with act_col3:
      if not is_locked_today:
        if st.button("🎲 Roll Alternative", use_container_width=True):
          st.session_state.reroll_counter += 1
          if "palette_idx" in st.session_state:
            st.session_state.palette_idx = 0
          st.rerun()
      else:
        st.caption(f"🔒 Locked at {active_lock.get('locked_time', 'Today')}")

    # Recent Wears Strip (Last 3 days)
    if st.session_state.wear_history:
      recent_summary = []
      for h in reversed(st.session_state.wear_history[-4:]):
        recent_summary.append(
            f"**{h.get('top_layer', '').split('/')[0].strip()}**"
            f" ({h.get('scenario')}, {h.get('date')[5:]})"
        )
      if recent_summary:
        st.markdown(
            "<div style='font-size: 12px; color: #8B949E; margin-bottom:"
            " 8px;'>🕒 <strong>Recent Wears:</strong>"
            f" {' • '.join(recent_summary)}</div>",
            unsafe_allow_html=True,
        )

    # Application Strategy Card
    st.markdown(
        f"""<div class="sartorial-card">
<h4 style="color: #58A6FF; margin: 0 0 8px 0; font-size: 16px;">🎯 Application Strategy</h4>
<div style="font-size: 13.5px; color: #E6EDF3; line-height: 1.5;">
• <strong>Target Sillage Cap:</strong> {scen_meta['cap']}<br>
• <strong>Spray Distribution:</strong> {spray_strategy}<br>
• <strong>Shower Prep:</strong> {wash_rec}<br>
• <strong>Grooming Canvas:</strong> <strong>{canvas_recommendation}</strong><br>
<span style="color: #8B949E; font-size: 12.5px; font-style: italic;">{canvas_reason}</span>
</div>
</div>""",
        unsafe_allow_html=True,
    )

    # Sartorial Harmony Card
    st.markdown(
        f"""<div class="sartorial-card">
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
<h4 style="color: #58A6FF; margin: 0; font-size: 16px;">🎨 Sartorial Color Harmony</h4>
<span class="badge-tag">OPTION {opt_num_display} OF {total_opts}</span>
</div>
<div style="font-weight: 600; font-size: 15px; margin-bottom: 8px;">{sartorial['name']}</div>
<div style="display: flex; gap: 16px; margin-bottom: 8px;">
<div><span class="swatch-box" style="background-color: {sartorial['primary']};"></span> Primary: <code>{sartorial['primary']}</code></div>
<div><span class="swatch-box" style="background-color: {sartorial['accent']};"></span> Accent: <code>{sartorial['accent']}</code></div>
</div>
<div style="font-size: 13px; color: #8B949E; margin-bottom: 6px;">{sartorial['styling']}</div>
</div>""",
        unsafe_allow_html=True,
    )

    if not is_locked_today:
      if st.button(
          "🎨 Shuffle Colorway (Option 1 / 2 / 3)", use_container_width=True
      ):
        st.session_state.palette_idx += 1
        st.rerun()
  else:
    st.warning(
        "No pairing recipes found in the active matrix sheets for this"
        " scenario."
    )

# ---------------------------------------------------------
# TAB 2: MATRIX EXPLORER
# ---------------------------------------------------------
with tab_explorer:
  st.header("Matrix Explorer")
  st.caption(
      "Filter recipes across seasonal sheets, pairing modes, scenario badges,"
      " and favorites."
  )

  if "favorites" not in st.session_state:
    st.session_state.favorites = load_favorites()

  only_favs = st.checkbox("⭐ Show Favorites Only", value=False)

  # 7 Canonical Seasonal Options
  CANONICAL_SEASONS = [
      "Deep Winter (< 45°F)",
      "Pre-Spring (Transitional 45°F – 58°F)",
      "Spring (Warming 55°F – 70°F)",
      "High Summer (75°F – 95°F+)",
      "Early Fall (Transitional 58°F – 72°F)",
      "Crisp Fall (45°F – 60°F)",
      "All-Season (6-Band Universal)",
  ]

  col_f1, col_f2 = st.columns(2)
  with col_f1:
    chosen_seasons = st.multiselect(
        "Seasonal Sheets (Multi-Select / Leave Blank for All 7)",
        CANONICAL_SEASONS,
        default=[],
    )
    chosen_mode = st.selectbox(
        "Pairing Mode",
        [
            "All Modes",
            "Standalone Solo Wear",
            "Body Cream Layer",
            "Cologne Mixology",
        ],
    )
  with col_f2:
    chosen_scen = st.selectbox(
        "Scenario Badge",
        [
            "All Scenarios",
            "WP (Work & Professional)",
            "LO (Leisure & Outdoor)",
            "DN (Date Night & Evening)",
            "NL (Nightlife & Lounges)",
            "EC (Everyday & Casual)",
        ],
    )
    primer_opt = st.selectbox(
        "Particle Primer Compatible", ["Any", "Yes", "No"]
    )

  filtered_df = matrix_df.copy()

  # 1. Filter by Canonical 7 Seasons (Smart Substring / Universal Matching)
  if chosen_seasons and "Season_Sheet" in filtered_df.columns:
    kw_map = {
        "Deep Winter": ["deep winter", "winter"],
        "Pre-Spring": ["pre-spring"],
        "Spring": ["spring"],
        "High Summer": ["summer", "vacation"],
        "Early Fall": ["early fall"],
        "Crisp Fall": ["crisp fall", "late fall", "fall"],
        "All-Season": ["all-season", "universal"],
    }
    active_keywords = []
    include_universal = False
    for opt in chosen_seasons:
      for cat, words in kw_map.items():
        if cat in opt:
          active_keywords.extend(words)
          if cat == "All-Season":
            include_universal = True

    pat = "|".join(set(active_keywords))
    mask = filtered_df["Season_Sheet"].str.contains(pat, case=False, na=False)
    if not include_universal:
      mask = mask | filtered_df["Season_Sheet"].str.contains(
          "all-season|universal", case=False, na=False
      )
    filtered_df = filtered_df[mask]

  # 2. Always Deduplicate in-memory across the active search slice
  filtered_df = deduplicate_catalog(filtered_df)

  # 3. Apply Favorites, Mode, Scenario, and Primer Filters
  if only_favs:
    fav_names = list(st.session_state.favorites.keys())
    filtered_df = filtered_df[filtered_df["Custom Profile Name"].isin(fav_names)]
  if chosen_mode != "All Modes" and "Pairing Type" in filtered_df.columns:
    filtered_df = filtered_df[filtered_df["Pairing Type"] == chosen_mode]
  if chosen_scen != "All Scenarios" and "Eligible Scenarios" in filtered_df.columns:
    filtered_df = filtered_df[
        filtered_df["Eligible Scenarios"].str.contains(
            chosen_scen.split()[0], case=False, na=False
        )
    ]
  if primer_opt != "Any" and "Particle Primer Compatible" in filtered_df.columns:
    filtered_df = filtered_df[
        filtered_df["Particle Primer Compatible"]
        .astype(str)
        .str.strip()
        .str.lower()
        == primer_opt.lower()
    ]

  st.write(f"**Found {len(filtered_df)} Matching Recipes** (Deduplicated)")
  if st.button("🎲 Surprise Me (Random Filter Match)", use_container_width=True):
    if not filtered_df.empty:
      pick = filtered_df.sample(1).iloc[0]
      desc_text = pick.get("Scent Profile & Notes Breakdown", "")
      st.info(
          f"**Random Pick:** **{pick.get('Custom Profile Name')}**"
          f" ({pick.get('Top Layer')})\n\n*{desc_text}*"
      )

  disp_cols = [
      c
      for c in [
          "Custom Profile Name",
          "Pairing Type",
          "Base Layer",
          "Top Layer",
          "Eligible Scenarios",
          "Projection Strength",
          "Scent Profile & Notes Breakdown",
      ]
      if c in filtered_df.columns
  ]
  st.dataframe(filtered_df[disp_cols], use_container_width=True, hide_index=True)

# ---------------------------------------------------------
# TAB 3: STANDALONE DIRECTORY
# ---------------------------------------------------------
with tab_directory:
  st.header("Fragrance Directory")
  search_q = st.text_input(
      "🔍 Search notes, cologne names, or DNA",
      placeholder="e.g. Sage, Ambroxan, YSL Y, Aventus, Vetiver...",
  )
  if search_q:
    mask = (
        matrix_df.astype(str)
        .apply(lambda row: row.str.contains(search_q, case=False).any(), axis=1)
    )
    res = deduplicate_catalog(matrix_df[mask])
    st.write(f"Found **{len(res)}** unique references:")
    disp = [
        c
        for c in [
            "Custom Profile Name",
            "Base Layer",
            "Top Layer",
            "Scent Profile & Notes Breakdown",
        ]
        if c in res.columns
    ]
    st.dataframe(res[disp], use_container_width=True, hide_index=True)
  else:
    st.info("Type a note or fragrance name above to query matching profiles.")

# ---------------------------------------------------------
# TAB 4: 🧳 TRIP CAPSULE PLANNER (DYNAMIC SHUFFLE & PERMUTATIONS)
# ---------------------------------------------------------
with tab_planner:
  st.header("🧳 Trip Capsule Planner")
  st.caption(
      "Custom capsule builder, slot-level shuffling, full tactical playbook,"
      " and trip save management."
  )

  # Initialize slot shuffle offsets & saved trips
  if "trip_offsets" not in st.session_state:
    st.session_state.trip_offsets = {
        "base_1": 0,
        "base_2": 1,
        "col_1": 0,
        "col_2": 0,
        "col_3": 0,
        "col_4": 0,
    }
  saved_trips_data = load_saved_trips()

  # Sub-section: Load Saved Trip
  if saved_trips_data:
    with st.expander("📂 View / Load Saved Trip Capsules", expanded=False):
      trip_choice = st.selectbox(
          "Select Saved Itinerary", list(saved_trips_data.keys())
      )
      if trip_choice:
        t_record = saved_trips_data[trip_choice]
        st.write(
            f"**Trip:** {trip_choice} | **Destination:**"
            f" {t_record.get('dest')} | **Dates:** {t_record.get('dates')}"
        )
        st.write(
            "**Bases:**"
            f" {', '.join([b['name'] for b in t_record.get('bases', [])])}"
        )
        st.write(
            "**Colognes:**"
            f" {', '.join([c['name'] for c in t_record.get('colognes', [])])}"
        )
        if st.button(f"🗑️ Delete Saved Itinerary '{trip_choice}'"):
          delete_saved_trip(trip_choice)
          st.rerun()

  st.subheader("1. Trip Parameters")
  dest_mode = st.radio(
      "Destination Method",
      ["🏙️ Choose Preset", "🔍 Search Any City / Island"],
      index=0,
      horizontal=True,
  )
  if dest_mode == "🏙️ Choose Preset":
    chosen_dest_label = st.selectbox(
        "Destination Preset",
        list(PRESET_CITIES.keys()),
        index=2 if "St. Thomas" in str(list(PRESET_CITIES.keys())) else 0,
    )
    target_lat = PRESET_CITIES[chosen_dest_label]["lat"]
    target_lon = PRESET_CITIES[chosen_dest_label]["lon"]
    resolved_dest_title = chosen_dest_label
  else:
    dest_input = st.text_input("Destination City or Island", value="St. Thomas")
    s_matches = search_city_geocoding(dest_input)
    if s_matches:
      d_choice = st.selectbox(
          "Matching Destination", s_matches, format_func=lambda x: x["label"]
      )
      target_lat = d_choice["lat"]
      target_lon = d_choice["lon"]
      resolved_dest_title = d_choice["label"]
    else:
      target_lat, target_lon = 18.3419, -64.9307
      resolved_dest_title = "St. Thomas, USVI (Default)"

  client_tz = resolve_client_timezone()
  local_now = get_local_now(client_tz)
  d_start = local_now.date() + datetime.timedelta(days=30)
  d_end = d_start + datetime.timedelta(days=6)
  date_range = st.date_input("Travel Dates", value=(d_start, d_end))
  dates_str = (
      f"{date_range[0]} to {date_range[1]}"
      if len(date_range) == 2
      else str(date_range)
  )

  st.write("**Scenarios to Cover:**")
  sc1, sc2 = st.columns(2)
  with sc1:
    scen_lo = st.checkbox("🌊 Leisure / Beach", value=True)
    scen_ec = st.checkbox("☕ Casual / Transit", value=True)
    scen_dn = st.checkbox("🍸 Date Night / Dinner", value=True)
  with sc2:
    scen_nl = st.checkbox("🪩 Nightlife / Clubs", value=False)
    scen_wp = st.checkbox("💼 Work / Meetings", value=False)

  cream_choice = st.radio(
      "Base Cream Allowance",
      ["1 Universal Anchor Cream", "2 Dynamic Dual Creams"],
      index=0,
      horizontal=True,
  )

  target_badges = []
  if scen_lo:
    target_badges.append("LO")
  if scen_ec:
    target_badges.append("EC")
  if scen_dn:
    target_badges.append("DN")
  if scen_nl:
    target_badges.append("NL")
  if scen_wp:
    target_badges.append("WP")
  if not target_badges:
    target_badges = ["LO", "EC", "DN"]

  t_wx = get_comprehensive_weather(target_lat, target_lon)
  t_band = evaluate_thermodynamic_band(t_wx["temp"], t_wx["wind_chill"])

  st.markdown("---")
  st.subheader("2. Curated Travel Capsule (Slot-by-Slot Shuffling)")

  st.markdown(
      f"""<div style="background-color: #161B22; border: 1px solid #30363D; border-radius: 8px; padding: 12px; margin-bottom: 12px; font-size: 13.5px;">
📍 <strong>Location:</strong> <span style="color: #58A6FF; font-weight: 600;">{resolved_dest_title}</span><br>
🌡️ <strong>Climate:</strong> ~<strong>{t_wx['temp']:.1f}°F</strong> (H: <strong>{t_wx['high']:.0f}°F</strong> / L: <strong>{t_wx['low']:.0f}°F</strong>) • {t_wx['humidity']}% Humid<br>
🌴 <strong>Seasonal Bracket:</strong> <span style="color: #39D353; font-weight: 600;">{t_band}</span><br>
🎯 <strong>Coverage Scenarios:</strong> {', '.join(target_badges)}
</div>""",
      unsafe_allow_html=True,
  )

  capsule = get_capsule_recommendations(
      t_band, t_wx["temp"], cream_choice, st.session_state.trip_offsets
  )
  base_1 = capsule["base_1"]
  base_2 = capsule["base_2"]
  active_bases = [base_1] + ([base_2] if base_2 else [])

  # Base Creams Presentation with Shuffle
  st.markdown(
      f"""<div class="capsule-card">
<span class="badge-tag">FOUNDATION ANCHOR #1</span>
<h3 style="color: #58A6FF; margin: 4px 0; font-size: 18px;">{base_1['name']}</h3>
<p style="margin: 0; font-size: 13px; color: #8B949E;">{base_1['desc']}</p>
</div>""",
      unsafe_allow_html=True,
  )
  if st.button("🎲 Shuffle Anchor Cream #1", key="btn_shuf_b1"):
    st.session_state.trip_offsets["base_1"] += 1
    st.rerun()

  if base_2:
    st.markdown(
        f"""<div class="capsule-card">
<span class="badge-tag">FOUNDATION ANCHOR #2</span>
<h3 style="color: #BC8CFF; margin: 4px 0; font-size: 18px;">{base_2['name']}</h3>
<p style="margin: 0; font-size: 13px; color: #8B949E;">{base_2['desc']}</p>
</div>""",
        unsafe_allow_html=True,
    )
    if st.button("🎲 Shuffle Anchor Cream #2", key="btn_shuf_b2"):
      st.session_state.trip_offsets["base_2"] += 1
      st.rerun()

  # Colognes Presentation with Individual Slot Shuffle
  colognes = [
      capsule["col_1"],
      capsule["col_2"],
      capsule["col_3"],
      capsule["col_4"],
  ]
  st.write(f"**Curated {len(colognes)}-Bottle Roster:**")

  for i, col in enumerate(colognes, 1):
    slot_key = f"col_{i}"
    c_box1, c_box2 = st.columns([4, 1])
    with c_box1:
      st.markdown(
          f"""<div style="background-color: #161B22; border-left: 4px solid #58A6FF; border-radius: 6px; padding: 10px 14px; margin-bottom: 8px;">
<div style="font-size: 14.5px; font-weight: 600; color: #E6EDF3;">Bottle #{i}: <span style="color: #58A6FF;">{col['name']}</span></div>
<div style="font-size: 12px; color: #BC8CFF; margin-top: 1px;">{col['role']}</div>
<div style="font-size: 12.5px; color: #8B949E; margin-top: 3px;">{col['notes']}</div>
</div>""",
          unsafe_allow_html=True,
      )
    with c_box2:
      if st.button(
          f"🎲 Swap #{i}", key=f"btn_shuf_{slot_key}", use_container_width=True
      ):
        st.session_state.trip_offsets[slot_key] += 1
        st.rerun()

  st.markdown("---")
  st.subheader("3. Exhaustive Trip Deployment Playbook (All Combinations)")
  st.caption(
      "Full tactical matrix displaying every combination achievable with your"
      " selected travel kit across your chosen scenarios:"
  )

  playbook_df = generate_all_playbook_combinations(
      active_bases, colognes, target_badges, matrix_df
  )
  st.dataframe(playbook_df, use_container_width=True, hide_index=True)

  # Sub-section: Save Trip Capsule
  st.markdown("---")
  st.subheader("4. 💾 Save This Capsule Itinerary")
  save_col1, save_col2 = st.columns([3, 1])
  with save_col1:
    new_trip_name = st.text_input(
        "Itinerary Name", value=f"{resolved_dest_title} Capsule"
    )
  with save_col2:
    st.write("")
    st.write("")
    if st.button("💾 Save Trip Plan", use_container_width=True):
      trip_payload = {
          "dest": resolved_dest_title,
          "dates": dates_str,
          "temp": t_wx["temp"],
          "band": t_band,
          "bases": active_bases,
          "colognes": colognes,
          "scenarios": target_badges,
          "saved_at": get_local_now().strftime("%Y-%m-%d %I:%M %p"),
      }
      if save_trip(new_trip_name, trip_payload):
        st.success(f"Trip '{new_trip_name}' saved to disk!")
        st.rerun()

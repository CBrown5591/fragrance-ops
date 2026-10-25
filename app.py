                    st.session_state.reroll_counter += 1
                    if "palette_idx" in st.session_state:
                        st.session_state.palette_idx = 0
                    st.rerun()
            else:
                st.caption(f"🔒 Locked & Logged at {active_lock.get('locked_time', 'Today')}")

        # Recent Wears Strip (Last 3 days)
        if st.session_state.wear_history:
            recent_summary = []
            for h in reversed(st.session_state.wear_history[-4:]):
                recent_summary.append(f"**{h.get('top_layer', '').split('/')[0].strip()}** ({h.get('scenario')}, {h.get('date')[5:]})")
            if recent_summary:
                st.markdown(f"<div style='font-size: 12px; color: #8B949E; margin-bottom: 8px;'>🕒 <strong>Recent Wears:</strong> {' • '.join(recent_summary)}</div>", unsafe_allow_html=True)

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
            if st.button("🎨 Shuffle Colorway (Option 1 / 2 / 3)", use_container_width=True):
                st.session_state.palette_idx += 1
                st.rerun()
    else:
        st.warning("No pairing recipes found in the active matrix sheets for this scenario.")

# ---------------------------------------------------------
# TAB 2: MATRIX EXPLORER
# ---------------------------------------------------------
with tab_explorer:
    st.header("Matrix Explorer")
    st.caption("Filter recipes across seasonal brackets, scenario badges, and chemical primers.")
    
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        seasons = ["All Sheets / Bands"] + sorted([s for s in matrix_df["Season_Sheet"].unique() if str(s).strip() != ""]) if "Season_Sheet" in matrix_df.columns else ["All Sheets / Bands"]
        chosen_season = st.selectbox("Seasonal Sheet", seasons)
        chosen_mode = st.selectbox("Pairing Mode", ["All Modes", "Standalone Solo Wear", "Body Cream Layer", "Cologne Mixology"])
    with col_f2:
        chosen_scen = st.selectbox("Scenario Badge", ["All Scenarios", "WP (Work & Professional)", "LO (Leisure & Outdoor)", "DN (Date Night & Evening)", "NL (Nightlife & Lounges)", "EC (Everyday & Casual)"])
        primer_opt = st.selectbox("Particle Primer Compatible", ["Any", "Yes", "No"])
        
    filtered_df = matrix_df.copy()
    if chosen_season != "All Sheets / Bands" and "Season_Sheet" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["Season_Sheet"] == chosen_season]
    if chosen_mode != "All Modes" and "Pairing Type" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["Pairing Type"] == chosen_mode]
    if chosen_scen != "All Scenarios" and "Eligible Scenarios" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["Eligible Scenarios"].str.contains(chosen_scen.split()[0], case=False, na=False)]
    if primer_opt != "Any" and "Particle Primer Compatible" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["Particle Primer Compatible"].astype(str).str.strip().str.lower() == primer_opt.lower()]

    st.write(f"**Found {len(filtered_df)} Matching Recipes**")
    if st.button("🎲 Surprise Me (Random Filter Match)", use_container_width=True):
        if not filtered_df.empty:
            pick = filtered_df.sample(1).iloc[0]
            desc_text = pick.get("Scent Profile & Notes Breakdown", "")
            st.info(f"**Random Pick:** **{pick.get('Custom Profile Name')}** ({pick.get('Top Layer')})\n\n*{desc_text}*")
            
    disp_cols = [c for c in ['Custom Profile Name', 'Pairing Type', 'Base Layer', 'Top Layer', 'Eligible Scenarios', 'Projection Strength', 'Scent Profile & Notes Breakdown'] if c in filtered_df.columns]
    st.dataframe(filtered_df[disp_cols], use_container_width=True, hide_index=True)

# ---------------------------------------------------------
# TAB 3: STANDALONE DIRECTORY
# ---------------------------------------------------------
with tab_directory:
    st.header("Fragrance Directory")
    search_q = st.text_input("🔍 Search notes, cologne names, or DNA", placeholder="e.g. Sage, Ambroxan, YSL Y, Aventus, Vetiver...")
    if search_q:
        mask = matrix_df.astype(str).apply(lambda row: row.str.contains(search_q, case=False).any(), axis=1)
        res = matrix_df[mask]
        st.write(f"Found **{len(res)}** references:")
        disp = [c for c in ['Custom Profile Name', 'Base Layer', 'Top Layer', 'Scent Profile & Notes Breakdown'] if c in res.columns]
        st.dataframe(res[disp], use_container_width=True, hide_index=True)
    else:
        st.info("Type a note or fragrance name above to query matching profiles.")

# ---------------------------------------------------------
# TAB 4: 🧳 TRIP CAPSULE PLANNER (DYNAMIC SHUFFLE & PERMUTATIONS)
# ---------------------------------------------------------
with tab_planner:
    st.header("🧳 Trip Capsule Planner")
    st.caption("Custom capsule builder, slot-level shuffling, full tactical playbook, and trip save management.")
    
    # Initialize slot shuffle offsets & saved trips
    if "trip_offsets" not in st.session_state:
        st.session_state.trip_offsets = {"base_1": 0, "base_2": 1, "col_1": 0, "col_2": 0, "col_3": 0, "col_4": 0}
    saved_trips_data = load_saved_trips()
    
    # Sub-section: Load Saved Trip
    if saved_trips_data:
        with st.expander("📂 View / Load Saved Trip Capsules", expanded=False):
            trip_choice = st.selectbox("Select Saved Itinerary", list(saved_trips_data.keys()))
            if trip_choice:
                t_record = saved_trips_data[trip_choice]
                st.write(f"**Trip:** {trip_choice} | **Destination:** {t_record.get('dest')} | **Dates:** {t_record.get('dates')}")
                st.write(f"**Bases:** {', '.join([b['name'] for b in t_record.get('bases', [])])}")
                st.write(f"**Colognes:** {', '.join([c['name'] for c in t_record.get('colognes', [])])}")
                if st.button(f"🗑️ Delete Saved Itinerary '{trip_choice}'"):
                    delete_saved_trip(trip_choice)
                    st.rerun()
                    
    st.subheader("1. Trip Parameters")
    dest_mode = st.radio("Destination Method", ["🏙️ Choose Preset", "🔍 Search Any City / Island"], index=0, horizontal=True)
    if dest_mode == "🏙️ Choose Preset":
        chosen_dest_label = st.selectbox("Destination Preset", list(PRESET_CITIES.keys()), index=2 if "St. Thomas" in str(list(PRESET_CITIES.keys())) else 0)
        target_lat = PRESET_CITIES[chosen_dest_label]["lat"]
        target_lon = PRESET_CITIES[chosen_dest_label]["lon"]
        resolved_dest_title = chosen_dest_label
    else:
        dest_input = st.text_input("Destination City or Island", value="St. Thomas")
        s_matches = search_city_geocoding(dest_input)
        if s_matches:
            d_choice = st.selectbox("Matching Destination", s_matches, format_func=lambda x: x["label"])
            target_lat = d_choice["lat"]
            target_lon = d_choice["lon"]
            resolved_dest_title = d_choice["label"]
        else:
            target_lat, target_lon = 18.3419, -64.9307
            resolved_dest_title = "St. Thomas, USVI (Default)"
            
    d_start = datetime.date.today() + datetime.timedelta(days=30)
    d_end = d_start + datetime.timedelta(days=6)
    date_range = st.date_input("Travel Dates", value=(d_start, d_end))
    dates_str = f"{date_range[0]} to {date_range[1]}" if len(date_range) == 2 else str(date_range)
    
    st.write("**Scenarios to Cover:**")
    sc1, sc2 = st.columns(2)
    with sc1:
        scen_lo = st.checkbox("🌊 Leisure / Beach", value=True)
        scen_ec = st.checkbox("☕ Casual / Transit", value=True)
        scen_dn = st.checkbox("🍸 Date Night / Dinner", value=True)
    with sc2:
        scen_nl = st.checkbox("🪩 Nightlife / Clubs", value=False)
        scen_wp = st.checkbox("💼 Work / Meetings", value=False)
        
    cream_choice = st.radio("Base Cream Allowance", ["1 Universal Anchor Cream", "2 Dynamic Dual Creams"], index=0, horizontal=True)
    
    target_badges = []
    if scen_lo: target_badges.append("LO")
    if scen_ec: target_badges.append("EC")
    if scen_dn: target_badges.append("DN")
    if scen_nl: target_badges.append("NL")
    if scen_wp: target_badges.append("WP")
    if not target_badges:
        target_badges = ["LO", "EC", "DN"]
        
    t_wx = get_comprehensive_weather(target_lat, target_lon)
    t_band = evaluate_thermodynamic_band(t_wx["temp"], t_wx["wind_chill"])
    
    st.markdown("---")
    st.subheader("2. Curated Travel Capsule (Slot-by-Slot Shuffling)")
    
    st.markdown(f"""<div style="background-color: #161B22; border: 1px solid #30363D; border-radius: 8px; padding: 12px; margin-bottom: 12px; font-size: 13.5px;">
📍 <strong>Location:</strong> <span style="color: #58A6FF; font-weight: 600;">{resolved_dest_title}</span><br>
🌡️ <strong>Climate:</strong> ~<strong>{t_wx['temp']:.1f}°F</strong> (H: <strong>{t_wx['high']:.0f}°F</strong> / L: <strong>{t_wx['low']:.0f}°F</strong>) • {t_wx['humidity']}% Humid<br>
🌴 <strong>Seasonal Bracket:</strong> <span style="color: #39D353; font-weight: 600;">{t_band}</span><br>
🎯 <strong>Coverage Scenarios:</strong> {', '.join(target_badges)}
</div>""", unsafe_allow_html=True)

    capsule = get_capsule_recommendations(t_band, t_wx["temp"], cream_choice, st.session_state.trip_offsets)
    base_1 = capsule["base_1"]
    base_2 = capsule["base_2"]
    active_bases = [base_1] + ([base_2] if base_2 else [])
    
    # Base Creams Presentation with Shuffle
    st.markdown(f"""<div class="capsule-card">
<span class="badge-tag">FOUNDATION ANCHOR #1</span>
<h3 style="color: #58A6FF; margin: 4px 0; font-size: 18px;">{base_1['name']}</h3>
<p style="margin: 0; font-size: 13px; color: #8B949E;">{base_1['desc']}</p>
</div>""", unsafe_allow_html=True)
    if st.button("🎲 Shuffle Anchor Cream #1", key="btn_shuf_b1"):
        st.session_state.trip_offsets["base_1"] += 1
        st.rerun()

    if base_2:
        st.markdown(f"""<div class="capsule-card">
<span class="badge-tag">FOUNDATION ANCHOR #2</span>
<h3 style="color: #BC8CFF; margin: 4px 0; font-size: 18px;">{base_2['name']}</h3>
<p style="margin: 0; font-size: 13px; color: #8B949E;">{base_2['desc']}</p>
</div>""", unsafe_allow_html=True)
        if st.button("🎲 Shuffle Anchor Cream #2", key="btn_shuf_b2"):
            st.session_state.trip_offsets["base_2"] += 1
            st.rerun()

    # Colognes Presentation with Individual Slot Shuffle
    colognes = [capsule["col_1"], capsule["col_2"], capsule["col_3"], capsule["col_4"]]
    st.write(f"**Curated {len(colognes)}-Bottle Roster:**")
    
    for i, col in enumerate(colognes, 1):
        slot_key = f"col_{i}"
        c_box1, c_box2 = st.columns([4, 1])
        with c_box1:
            st.markdown(f"""<div style="background-color: #161B22; border-left: 4px solid #58A6FF; border-radius: 6px; padding: 10px 14px; margin-bottom: 8px;">
<div style="font-size: 14.5px; font-weight: 600; color: #E6EDF3;">Bottle #{i}: <span style="color: #58A6FF;">{col['name']}</span></div>
<div style="font-size: 12px; color: #BC8CFF; margin-top: 1px;">{col['role']}</div>
<div style="font-size: 12.5px; color: #8B949E; margin-top: 3px;">{col['notes']}</div>
</div>""", unsafe_allow_html=True)
        with c_box2:
            if st.button(f"🎲 Swap #{i}", key=f"btn_shuf_{slot_key}", use_container_width=True):
                st.session_state.trip_offsets[slot_key] += 1
                st.rerun()

    st.markdown("---")
    st.subheader("3. Exhaustive Trip Deployment Playbook (All Combinations)")
    st.caption("Full tactical matrix displaying every combination achievable with your selected travel kit across your chosen scenarios:")
    
    playbook_df = generate_all_playbook_combinations(active_bases, colognes, target_badges, matrix_df)
    st.dataframe(playbook_df, use_container_width=True, hide_index=True)
    
    # Sub-section: Save Trip Capsule
    st.markdown("---")
    st.subheader("4. 💾 Save This Capsule Itinerary")
    save_col1, save_col2 = st.columns([3, 1])
    with save_col1:
        new_trip_name = st.text_input("Itinerary Name", value=f"{resolved_dest_title} Capsule")
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
                "saved_at": datetime.datetime.now().strftime("%Y-%m-%d %I:%M %p")
            }
            if save_trip(new_trip_name, trip_payload):
                st.success(f"Trip '{new_trip_name}' saved to disk!")
                st.rerun()

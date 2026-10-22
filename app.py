        
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
                st.info(f"**Random Pick:** **{pick.get('Custom Profile Name')}** ({pick.get('Base Layer')} + {pick.get('Top Layer')})\n\n*{pick.get('Scent Profile & Notes Breakdown')}*")
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

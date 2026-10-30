"""Universal Scenario Transition Bridge Engine for Fragrance Ops.
Evaluates drydown residues and calculates over-spray synergy, note clashes, and application protocols across ANY scenario transition.
"""

def evaluate_scenario_transition(prev_scent, new_scent, prev_badge="DAY", new_badge="TARGET"):
    """
    Evaluates olfactory compatibility when spraying a new scenario fragrance
    over the lingering drydown of a previously worn fragrance.
    """
    if not prev_scent or not new_scent:
        return None
        
    p_low = prev_scent.lower()
    n_low = new_scent.lower()
    
    # 1. Perfect Natural Synergies & Harmonious Over-Sprays
    if ("society" in p_low or "gentleman" in p_low) and ("the one" in n_low or "whiskey" in n_low or "pi" in n_low):
        return {
            "status": "🌟 Harmonious Over-Spray",
            "badge_color": "#39D353",
            "headline": "Vetiver & Cardamom Synergy",
            "guidance": "Givenchy Society's lingering Haitian vetiver and cedarwood drydown binds effortlessly with warm tobacco, boozy amber, and vanilla.",
            "protocol": "Safe for direct over-spray. Apply 2 sprays to collarbones and 1 to back of neck to re-ignite sillage."
        }
        
    if ("blue fate" in p_low or "myslf" in p_low or "identity" in p_low) and ("the one" in n_low or "society" in n_low or "dylan" in n_low or "nomade" in n_low):
        return {
            "status": "🌟 Harmonious Over-Spray",
            "badge_color": "#39D353",
            "headline": "Modern Ambrofix & Floral Boost",
            "guidance": "The clean Ambrofix / Akigalawood skin residue acts as an organic booster, projecting incoming woods, spices, and amber with radiant lift.",
            "protocol": "Apply 2–3 sprays directly to pulse points. No skin reset required."
        }
        
    if ("pristine" in p_low or "aventus" in p_low or "br540" in p_low) and ("nomade" in n_low or "whiskey" in n_low or "the one" in n_low or "oud" in n_low):
        return {
            "status": "🌟 Harmonious Over-Spray",
            "badge_color": "#39D353",
            "headline": "Smoky Birch & Saffron Resonance",
            "guidance": "Fading smoky birch and burnt-sugar saffron creates an opulent primer underneath incoming woods, tobacco, or dark resins.",
            "protocol": "Controlled application: Cap at 2 sprays. The residual amber base will naturally amplify projection reach."
        }
        
    if ("reality" in p_low or "imagination" in p_low) and ("blue fate" in n_low or "society" in n_low or "guilty" in n_low):
        return {
            "status": "✨ Seamless Transition",
            "badge_color": "#58A6FF",
            "headline": "Black Tea & Citrus Awakening",
            "guidance": "The sparkling black tea and ambroxan skin trail provides an elegant, transparent backdrop that brightens incoming aromatics.",
            "protocol": "Apply normal spray cap. Residual afternoon tea notes will gently evaporate without muddling the new core."
        }
        
    # 2. Boundary Clashes (Shower / Canvas Reset Required)
    if ("profondo" in p_low or "ocean" in p_low or "viw" in p_low or "virgin island" in p_low) and ("nomade" in n_low or "oud" in n_low or "pi" in n_low):
        return {
            "status": "⚠️ Boundary Clash Detected",
            "badge_color": "#F85149",
            "headline": "Marine Ozone vs. Dense Resins / Oud",
            "guidance": "Marine sea salt and cypress accords clash directly against heavy smoky resins, benzoin, and raw oud, risking a muddled chemical aura.",
            "protocol": "Canvas Reset Recommended: Cleanse chest and neck with warm water and soap before applying heavy ouds or dense gourmands."
        }
        
    if ("pi" in p_low or "vanilla" in p_low or "tonka" in p_low) and ("profondo" in n_low or "reality" in n_low or "splish" in n_low or "light blue" in n_low):
        return {
            "status": "⚠️ Boundary Clash Detected",
            "badge_color": "#F85149",
            "headline": "Sweet Tonka Suffocation",
            "guidance": "Residual sweet almond and roasted tonka bean will suffocate delicate incoming sparkling citrus, mountain tea, or aquatic ozone notes.",
            "protocol": "Reset canvas with a warm shower or alcohol wipe before applying light daytime citrus or fresh aquatics."
        }

    # 3. Universal / General Transition Protocol
    return {
        "status": "✨ Clean Neutral Bridge",
        "badge_color": "#58A6FF",
        "headline": f"{prev_badge} ➔ {new_badge} Shift",
        "guidance": f"Residual drydown of {prev_scent.split('(')[0].strip()} provides a subtle background canvas for {new_scent.split('(')[0].strip()}.",
        "protocol": "Apply 2–3 sprays to pulse points. If earlier projection is still assertive on clothes, target fresh skin only."
    }

# Backwards compatibility alias
evaluate_evening_transition = evaluate_scenario_transition

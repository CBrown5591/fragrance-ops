"""Day-to-Evening Transition Bridge Engine for Fragrance Ops.
Analyzes daytime drydown residues and evaluates evening over-spray synergy, clashing notes, and spray caps.
"""

def evaluate_evening_transition(day_scent, evening_scent):
    """
    Evaluates olfactory compatibility when spraying an evening fragrance
    directly over the fading drydown of a daytime fragrance.
    """
    if not day_scent or not evening_scent:
        return None
        
    d_low = day_scent.lower()
    e_low = evening_scent.lower()
    
    # 1. Perfect Natural Synergies
    if ("society" in d_low or "gentleman" in d_low) and ("the one" in e_low or "whiskey" in e_low or "pi" in e_low):
        return {
            "status": "🌟 Harmonious Over-Spray",
            "badge_color": "#39D353",
            "headline": "Wood & Cardamom Bridge",
            "guidance": "Givenchy Society's lingering Haitian vetiver and cedarwood drydown binds effortlessly with evening tobacco, bourbon amber, and warm vanilla.",
            "protocol": "No shower needed. Apply 2 sprays to collarbones and 1 to back of neck to re-ignite sillage without overwhelming the baseline."
        }
        
    if ("blue fate" in d_low or "myslf" in d_low or "identity" in d_low) and ("the one" in e_low or "society" in e_low or "dylan" in e_low or "nomade" in e_low):
        return {
            "status": "🌟 Harmonious Over-Spray",
            "badge_color": "#39D353",
            "headline": "Modern Ambroxan & Floral Fusion",
            "guidance": "The clean Ambrofix / Akigalawood morning skin trail acts as a transparent booster, allowing evening woods, spices, and amber to project with radiant lift.",
            "protocol": "Safe for direct over-spray. Apply 2–3 sprays to chest and neck pulse points."
        }
        
    if ("pristine" in d_low or "aventus" in d_low or "br540" in d_low) and ("nomade" in e_low or "whiskey" in e_low or "the one" in e_low or "oud" in e_low):
        return {
            "status": "🌟 Harmonious Over-Spray",
            "badge_color": "#39D353",
            "headline": "Smoky Birch & Amber Saffron Layer",
            "guidance": "Fading smoky birch and burnt sugar saffron creates an opulent base layer under evening agarwood, cured tobacco, or bourbon oak.",
            "protocol": "Controlled re-application: 2 sprays maximum. The residual amber base will amplify evening sillage reach."
        }
        
    if ("reality" in d_low or "imagination" in d_low) and ("blue fate" in e_low or "society" in e_low or "guilty" in e_low):
        return {
            "status": "✨ Seamless Transition",
            "badge_color": "#58A6FF",
            "headline": "Black Tea & Citrus Awakening",
            "guidance": "The sparkling black tea and ambroxan skin scent provides a crisp, elegant backdrop that lifts evening aromatics and soft woods.",
            "protocol": "Apply 3 sprays to upper chest and neck. The afternoon tea notes will gently evaporate, leaving clean ambroxan resonance."
        }
        
    # 2. Boundary Clashes (Shower / Reset Required)
    if ("profondo" in d_low or "ocean" in d_low or "acqua" in d_low) and ("nomade" in e_low or "oud noir" in e_low or "pi" in e_low):
        return {
            "status": "⚠️ Boundary Clash Detected",
            "badge_color": "#F85149",
            "headline": "Marine Salt vs. Dense Gourmand / Oud",
            "guidance": "Marine salt and green cypress accords clash against heavy smoky resins, benzoin, and raw oud, creating a muddled, synthetic aura.",
            "protocol": "Shower / Clean Slate Recommended: Cleanse chest and neck with warm water and unscented soap before applying evening gourmands or heavy ouds."
        }
        
    if ("pi" in d_low or "vanilla" in d_low) and ("profondo" in e_low or "reality" in e_low or "splish" in e_low):
        return {
            "status": "⚠️ Boundary Clash Detected",
            "badge_color": "#F85149",
            "headline": "Sweet Tonka Suffocation",
            "guidance": "Residual almond and roasted tonka bean will suffocate delicate sparkling citrus, mountain tea, and aquatic ozone notes.",
            "protocol": "Reset canvas before applying light citrus or aquatic evening scents."
        }

    # 3. Default Neutral / General Bridge
    return {
        "status": "✨ Clean Neutral Bridge",
        "badge_color": "#58A6FF",
        "headline": "Standard Over-Spray",
        "guidance": f"Morning remnants of {day_scent.split('(')[0].strip()} provide a subtle underlying canvas for {evening_scent.split('(')[0].strip()}.",
        "protocol": "Apply 2–3 sprays to pulse points. If morning projection is still assertive, cap evening sprays at 2."
    }

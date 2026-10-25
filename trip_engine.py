"""Trip Capsule engine: dynamic candidate pools, slot shuffling, exhaustive permutations, and saved trips."""

import os
import json
import pandas as pd

SAVED_TRIPS_FILE = "saved_trips.json"

# Candidate pools for seasonal trip planning and slot-level shuffling
TRIP_POOLS = {
    "High Summer (75°F – 95°F+)": {
        "bases": [
            {
                "name": "Freshwater Cream",
                "desc": "Universal crisp mountain spring water & Italian bergamot canvas. Prevents heavy cream suffocation in Caribbean heat."
            },
            {
                "name": "Ocean Cream",
                "desc": "Blue cypress and coastal air foundation; builds dedicated saltwater and marine longevity for beach days."
            },
            {
                "name": "Unscented Body Lotion",
                "desc": "Weightless, non-occlusive hydration for ultra-high humidity without altering citrus/marine sillage."
            }
        ],
        "slot_1": [
            {
                "name": "Creed Virgin Island Water / Alt. Colada",
                "role": "Tropical Day & Beach (LO / EC)",
                "notes": "Lime zest, coconut water, white rum, and sugar cane."
            },
            {
                "name": "Alt. Splish (D&G Light Blue)",
                "role": "Icy Citrus Cascade (EC / LO)",
                "notes": "Sicilian mandarin, frozen grapefruit peel, and sea salt."
            },
            {
                "name": "Tommy Bahama Set Sail St. Barts",
                "role": "Resort Tequila Lime (LO / EC)",
                "notes": "Tequila accord, salty lime, agave, and blue palm."
            }
        ],
        "slot_2": [
            {
                "name": "Alt. Reality (LV Imagination DNA)",
                "role": "Luminous Day Refresher (EC / LO)",
                "notes": "Black tea, Sicilian citrus, fresh ginger, and ambroxan."
            },
            {
                "name": "Alt. Identity (YSL MYSLF DNA)",
                "role": "Contemporary White Floral (WP / EC)",
                "notes": "Calabrian bergamot, orange blossom, and clean Ambrofix."
            },
            {
                "name": "Givenchy Pi Neo",
                "role": "High-Tech Crisp Woods (WP / EC)",
                "notes": "Mandarin, bergamot, herbal myrtle, and crystalline cedar."
            }
        ],
        "slot_3": [
            {
                "name": "Alt. Blue Fate (Blue Talisman DNA)",
                "role": "Sunset Dinner (DN / EC)",
                "notes": "Juicy pear, fresh ginger, orange blossom, and Akigalawood."
            },
            {
                "name": "Givenchy Gentleman Society",
                "role": "Boardroom & Evening Anchor (WP / DN)",
                "notes": "Cardamom, French sage, wild narcissus, vetiver, and dark vanilla."
            },
            {
                "name": "Valentino Uomo Born in Roma",
                "role": "Mineral Street Aristocrat (WP / DN)",
                "notes": "Mineral salt accord, violet leaf, ginger, and smoky vetiver."
            }
        ],
        "slot_4": [
            {
                "name": "GA Acqua Di Gio Profondo",
                "role": "Marine Shield (LO / EC)",
                "notes": "Deep mineral marine accords, green mandarin, and blue cypress."
            },
            {
                "name": "Versace Dylan Blue",
                "role": "Nocturnal Power Alpha (NL / LO)",
                "notes": "Aquatic citrus, black pepper, incense, and ambroxan."
            },
            {
                "name": "Alt. Farouche Elixir (Sauvage Elixir DNA)",
                "role": "Nightlife Beast Mode (NL)",
                "notes": "Sichuan pepper, nutmeg, cinnamon, and rich lavender."
            }
        ]
    },
    "Deep Winter (< 45°F)": {
        "bases": [
            {
                "name": "Mahogany Teakwood Cream",
                "desc": "Dense dark timber and frosted lavender foundation; binds warm resins against freezing drafts."
            },
            {
                "name": "Whiskey Reserve Cream",
                "desc": "Boozy single-malt and white oak for intimate evening dining and cigar lounges."
            },
            {
                "name": "Graphite Cream",
                "desc": "Aromatic sage and leatherwood; provides a tailored backbone against dry cold winds."
            }
        ],
        "slot_1": [
            {
                "name": "Givenchy Gentleman Society",
                "role": "Boardroom King (WP / DN)",
                "notes": "Cardamom, French clary sage, vetiver trio, and dark vanilla."
            },
            {
                "name": "John Wick x Scentbird",
                "role": "Tactical Authority (WP / DN)",
                "notes": "Gunmetal slide accord, spiced lemon, clary sage, and cedar bourbon."
            },
            {
                "name": "House of Kelam (HOK) Oud Noir",
                "role": "Sovereign Agarwood Suite (WP / DN / NL)",
                "notes": "Precious agarwood, rosewood, cardamom, and smoky amber."
            }
        ],
        "slot_2": [
            {
                "name": "Alt. Pristine (Aventus x BR540)",
                "role": "Daytime Aristocrat (WP / EC)",
                "notes": "Pineapple, smoky birch, burnt sugar saffron, and amberwood."
            },
            {
                "name": "Gucci Guilty Pour Homme",
                "role": "French Barbershop Clean (WP / EC)",
                "notes": "French lavender, Italian lemon, and cedarwood."
            },
            {
                "name": "Alt. A (YSL Y DNA)",
                "role": "Crisp Blue Alpha (WP / EC)",
                "notes": "Green apple, ginger, sage, and clean amberwood."
            }
        ],
        "slot_3": [
            {
                "name": "D&G The One for Men",
                "role": "Intimate Date Night (DN)",
                "notes": "Warm cardamom, fresh ginger, cured tobacco, and cozy amber."
            },
            {
                "name": "Givenchy Pi",
                "role": "Golden Gourmand (DN / EC)",
                "notes": "Sweet almond, benzoin, tonka bean, and roasted vanilla."
            },
            {
                "name": "B&BW Whiskey Reserve (Cologne)",
                "role": "Boozy Oak Barrel (DN / LO)",
                "notes": "Crisp red apple, single malt whiskey, and aged white oak."
            }
        ],
        "slot_4": [
            {
                "name": "House of Kelam (HOK) Nomade Ember",
                "role": "Nightlife Weapon (NL / DN)",
                "notes": "Smoked agarwood, incense tears, sweet raspberry, and raw leather."
            },
            {
                "name": "Alt. Farouche Elixir (Sauvage Elixir DNA)",
                "role": "Nuclear Statement (NL / WP)",
                "notes": "Sichuan pepper, nutmeg, cinnamon, and rich lavender."
            },
            {
                "name": "Dior Sauvage (EDT/EDP)",
                "role": "Tactical Ambroxan Alpha (WP / NL)",
                "notes": "Calabrian bergamot, Sichuan pepper, and ambroxan."
            }
        ]
    },
    "Transitional": {
        "bases": [
            {
                "name": "Graphite Cream",
                "desc": "The #1 Versatility carrier; aromatic sage and leatherwood effortlessly anchor boardroom blues and evening woods."
            },
            {
                "name": "Mahogany Teakwood Cream",
                "desc": "Rich dark oak and frosted lavender; provides thermal reinforcement for outdoor breezes and night lounges."
            },
            {
                "name": "Freshwater Cream",
                "desc": "Alpine spring water and bergamot; cleanses heavy notes for breezy springtime afternoons."
            }
        ],
        "slot_1": [
            {
                "name": "Givenchy Gentleman Society",
                "role": "Boardroom Anchor (WP / DN)",
                "notes": "Cardamom, French sage, vetiver, and dark vanilla."
            },
            {
                "name": "Alt. A (YSL Y DNA)",
                "role": "Crisp Blue Alpha (WP / EC / LO)",
                "notes": "Green apple, ginger, clary sage, and amberwood."
            },
            {
                "name": "Valentino Uomo Born in Roma",
                "role": "Mineral Street Edge (WP / EC)",
                "notes": "Mineral salt accord, violet leaf, ginger, and smoky vetiver."
            }
        ],
        "slot_2": [
            {
                "name": "Alt. Identity (YSL MYSLF DNA)",
                "role": "Contemporary Daily (WP / EC)",
                "notes": "Calabrian bergamot, orange blossom, and Ambrofix."
            },
            {
                "name": "Alt. Reality (LV Imagination DNA)",
                "role": "Luminous Spa Tea (EC / LO)",
                "notes": "Chinese black tea, Sicilian citrus, ginger, and ambroxan."
            },
            {
                "name": "Givenchy Pi Neo",
                "role": "Tailored Corporate Cool (WP / EC)",
                "notes": "Mandarin, bergamot, herbal myrtle, and crystalline cedar."
            }
        ],
        "slot_3": [
            {
                "name": "Alt. Blue Fate (Blue Talisman DNA)",
                "role": "Social Bridge (DN / EC / LO)",
                "notes": "Juicy pear, fresh ginger, ambroxan, and Akigalawood."
            },
            {
                "name": "D&G The One for Men",
                "role": "Close Date Night (DN)",
                "notes": "Warm cardamom, fresh ginger, cured tobacco, and amber."
            },
            {
                "name": "Alt. Pristine (Aventus x BR540)",
                "role": "Executive Saffron (WP / DN)",
                "notes": "Pineapple, smoky birch, burnt sugar saffron, and amberwood."
            }
        ],
        "slot_4": [
            {
                "name": "GA Acqua Di Gio Profondo",
                "role": "Waterfront / Patio Shield (LO / EC)",
                "notes": "Deep mineral marine accords, green mandarin, and blue cypress."
            },
            {
                "name": "Gucci Guilty Pour Homme",
                "role": "Refined Barbershop (WP / EC / DN)",
                "notes": "French lavender, Italian lemon, and cedarwood."
            },
            {
                "name": "Alt. Farouche Elixir (Sauvage Elixir DNA)",
                "role": "Nightlife Weapon (NL)",
                "notes": "Sichuan pepper, nutmeg, cinnamon, and rich lavender."
            }
        ]
    }
}

def resolve_pool_key(band, temp):
    if "Summer" in band or temp >= 75.0:
        return "High Summer (75°F – 95°F+)"
    elif "Winter" in band or temp < 48.0:
        return "Deep Winter (< 45°F)"
    return "Transitional"

def get_capsule_recommendations(band, temp, cream_choice, offsets=None):
    if offsets is None:
        offsets = {}
        
    pool_key = resolve_pool_key(band, temp)
    pool = TRIP_POOLS[pool_key]
    
    bases_pool = pool["bases"]
    b1_idx = offsets.get("base_1", 0) % len(bases_pool)
    base_1 = bases_pool[b1_idx]
    
    base_2 = None
    if cream_choice == "2 Dynamic Dual Creams":
        b2_idx = offsets.get("base_2", (b1_idx + 1)) % len(bases_pool)
        if b2_idx == b1_idx:
            b2_idx = (b2_idx + 1) % len(bases_pool)
        base_2 = bases_pool[b2_idx]
        
    s1_pool = pool["slot_1"]
    s2_pool = pool["slot_2"]
    s3_pool = pool["slot_3"]
    s4_pool = pool["slot_4"]
    
    col_1 = s1_pool[offsets.get("col_1", 0) % len(s1_pool)]
    col_2 = s2_pool[offsets.get("col_2", 0) % len(s2_pool)]
    col_3 = s3_pool[offsets.get("col_3", 0) % len(s3_pool)]
    col_4 = s4_pool[offsets.get("col_4", 0) % len(s4_pool)]
    
    return {
        "pool_key": pool_key,
        "base_1": base_1,
        "base_2": base_2,
        "col_1": col_1,
        "col_2": col_2,
        "col_3": col_3,
        "col_4": col_4
    }

def generate_all_playbook_combinations(bases, colognes, target_badges, matrix_df=None):
    SCENARIO_NAMES = {
        "LO": "🌊 Leisure & Outdoor",
        "EC": "☕ Everyday & Casual",
        "DN": "🍸 Dinner & Date Night",
        "NL": "🪩 Nightlife & Clubs",
        "WP": "💼 Work & Professional"
    }
    
    CAP_BY_SCENARIO = {
        "LO": "Assertive Open-Air (4–6 ft reach)",
        "EC": "Approachable Moderate (2–3 ft)",
        "DN": "Intimate Bubble (2–3 ft)",
        "NL": "Bold Statement (6–8+ ft)",
        "WP": "Controlled Moderate (3–4 ft cap)"
    }
    
    playbook_rows = []
    
    for badge in target_badges:
        scen_title = SCENARIO_NAMES.get(badge, f"🎯 {badge} Protocol")
        scen_cap = CAP_BY_SCENARIO.get(badge, "Moderate (3–4 ft)")
        
        for col in colognes:
            # 1. Standalone Solo Option
            solo_desc = f"Clean canvas prep; highlights natural {col['notes']} without base interference."
            if matrix_df is not None and not matrix_df.empty:
                match = matrix_df[
                    (matrix_df["Top Layer"].astype(str).str.contains(col['name'].split('/')[0].strip()[:8], case=False, na=False)) &
                    (matrix_df["Pairing Type"] == "Standalone Solo Wear")
                ]
                if not match.empty:
                    solo_desc = match.iloc[0].get("Scent Profile & Notes Breakdown", solo_desc)
                    
            playbook_rows.append({
                "Scenario": scen_title,
                "Pairing Type": "🎯 Standalone Solo",
                "Base Layer": "Clean Canvas Prep",
                "Top Layer / Cologne": col['name'],
                "Target Sillage Cap": scen_cap,
                "Tactical Rationale": solo_desc
            })
            
            # 2. Layered with Base 1 (and Base 2 if present)
            for b in bases:
                layer_desc = f"Binds volatile top notes of {col['name'].split('/')[0].strip()} onto {b['name']} lipid foundation."
                if matrix_df is not None and not matrix_df.empty:
                    match = matrix_df[
                        (matrix_df["Top Layer"].astype(str).str.contains(col['name'].split('/')[0].strip()[:8], case=False, na=False)) &
                        (matrix_df["Base Layer"].astype(str).str.contains(b['name'].replace(" Cream", "").strip()[:6], case=False, na=False))
                    ]
                    if not match.empty:
                        layer_desc = match.iloc[0].get("Scent Profile & Notes Breakdown", layer_desc)
                        
                playbook_rows.append({
                    "Scenario": scen_title,
                    "Pairing Type": "🧪 Body Cream Layer",
                    "Base Layer": b['name'],
                    "Top Layer / Cologne": col['name'],
                    "Target Sillage Cap": scen_cap,
                    "Tactical Rationale": layer_desc
                })
                
    return pd.DataFrame(playbook_rows)

def load_saved_trips():
    if os.path.exists(SAVED_TRIPS_FILE):
        try:
            with open(SAVED_TRIPS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_trip(trip_name, trip_data):
    trips = load_saved_trips()
    trips[trip_name] = trip_data
    try:
        with open(SAVED_TRIPS_FILE, "w", encoding="utf-8") as f:
            json.dump(trips, f, indent=2)
        return True
    except Exception:
        return False

def delete_saved_trip(trip_name):
    trips = load_saved_trips()
    if trip_name in trips:
        del trips[trip_name]
        try:
            with open(SAVED_TRIPS_FILE, "w", encoding="utf-8") as f:
                json.dump(trips, f, indent=2)
            return True
        except Exception:
            return False
    return False

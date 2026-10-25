"""Configuration, styling, and static registries for Fragrance Ops."""

ICON_B64 = "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"

SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

NON_PAIRING_SHEETS = [
    "directory", "rules", "tips", "inventory", "rankings"
]

PRESET_CITIES = {
    "Washington, D.C.": {"lat": 38.9072, "lon": -77.0369},
    "National Harbor, MD": {"lat": 38.7848, "lon": -77.0169},
    "St. Thomas, USVI": {"lat": 18.3419, "lon": -64.9307},
    "New York, NY": {"lat": 40.7128, "lon": -74.0060},
    "Miami, FL": {"lat": 25.7617, "lon": -80.1918},
    "Orlando, FL": {"lat": 28.5383, "lon": -81.3792},
    "Atlanta, GA": {"lat": 33.7490, "lon": -84.3880},
    "Chicago, IL": {"lat": 41.8781, "lon": -87.6298},
    "Los Angeles, CA": {"lat": 34.0522, "lon": -118.2437}
}

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

SARTORIAL_MAP = {
    "The Modern Herbal Executive": [
        {"opt_num": 1, "name": "Executive Navy & Brushed Gold", "primary": "#1F497D", "accent": "#D4AF37", "styling": "Suited navy trouser with brushed gold/brass hardware mirroring French sage and Society vanilla."},
        {"opt_num": 2, "name": "Forest Hunter Green & Brushed Brass", "primary": "#1C3325", "accent": "#C5A059", "styling": "Hunter green mirrors French clary sage and Haitian vetiver; brass hardware matches smooth cedar."},
        {"opt_num": 3, "name": "Washed Charcoal & Warm Sandstone", "primary": "#2E3033", "accent": "#C2B69D", "styling": "Translates creamy vanilla and dark Haitian vetiver into understated neutral warmth."}
    ],
    "The Crisp Blue Alpha": [
        {"opt_num": 1, "name": "Deep Navy & Crisp Gunmetal", "primary": "#0D2A6B", "accent": "#5A6570", "styling": "Crisp blue aromatic lift over modern tailored suiting or clean dark denim."},
        {"opt_num": 2, "name": "Spruce Slate & Frost White", "primary": "#2C3E35", "accent": "#F4F6F8", "styling": "Crisp apple and herbal sage over dark spruce chino and optic white."},
        {"opt_num": 3, "name": "Charcoal & Warm Amber Leather", "primary": "#2B303A", "accent": "#C87D28", "styling": "Grounds bright ginger and amberwood into tailored executive amber."}
    ],
    "The Luminous Modern Executive": [
        {"opt_num": 1, "name": "Slate Charcoal & Soft Lavender", "primary": "#2B303A", "accent": "#9E97A9", "styling": "Modern ambroxan and orange blossom over tailored slate."},
        {"opt_num": 2, "name": "Washed Mineral & Desert Sand", "primary": "#4F6B85", "accent": "#C2B29D", "styling": "Sun-warmed pear and ginger balanced over neutral chinos."},
        {"opt_num": 3, "name": "Deep Navy & Sterling Grey", "primary": "#162238", "accent": "#9AA3AB", "styling": "Cool crystalline sillage with modern executive metallic hardware."}
    ],
    "The Sovereign Society Executive": [
        {"opt_num": 1, "name": "Midnight Navy & Cardamom Bronze", "primary": "#1A2238", "accent": "#A3704C", "styling": "Rich narcissus and dark vanilla over deep executive navy with warm leather accents."},
        {"opt_num": 2, "name": "Charcoal & Muted Moss", "primary": "#2F353B", "accent": "#606C5A", "styling": "Earthy cedar and organic vetiver in a tailored corporate silhouette."},
        {"opt_num": 3, "name": "Espresso & Brushed Gold", "primary": "#2B2118", "accent": "#C5A059", "styling": "Opulent evening wood and smooth amber warmth."}
    ],
    "The High-Tech Corporate Mind": [
        {"opt_num": 1, "name": "Slate Olive & Sunlit Amber", "primary": "#3B443B", "accent": "#D9822B", "styling": "Herbal myrtle and cedar balanced by energetic mandarin."},
        {"opt_num": 2, "name": "Charcoal & Ice Blue", "primary": "#36454F", "accent": "#A5C5D9", "styling": "Clean crystalline cedar and high-tech corporate cool."},
        {"opt_num": 3, "name": "Dark Chocolate & Clean Sand", "primary": "#342822", "accent": "#D1C2A5", "styling": "Warm modern wood base with lightweight neutral contrast."}
    ],
    "The Modern Mineral Aristocrat": [
        {"opt_num": 1, "name": "Mineral Slate & Smoked Sage", "primary": "#3C4A57", "accent": "#8A9A86", "styling": "Mineral salt and clary sage over muted herbal earth."},
        {"opt_num": 2, "name": "Slate Charcoal & Mineral Ice Blue", "primary": "#2B303A", "accent": "#7C99B3", "styling": "Airy ozone and violet leaf grounded in tailored charcoal."},
        {"opt_num": 3, "name": "Dark Plum & Frosted Platinum", "primary": "#422835", "accent": "#D8DEE4", "styling": "Smoky vetiver depth paired with modern mineral contrast."}
    ],
    "The Alpine Aristocrat": [
        {"opt_num": 1, "name": "Deep Teak Brown & Alpine Silver", "primary": "#2E1F18", "accent": "#D6DBDF", "styling": "Polished dark timber balancing frosty green tea air."},
        {"opt_num": 2, "name": "Dark Forest & Clean Cream", "primary": "#1E2B22", "accent": "#ECE6D8", "styling": "Herbal blackcurrant and tea over earthy forest wool."},
        {"opt_num": 3, "name": "Navy Indigo & Icy Steel", "primary": "#1B263B", "accent": "#8D99AE", "styling": "Crisp mountain ozone over structured executive blue."}
    ],
    "The Seductive Modern Barbershop": [
        {"opt_num": 1, "name": "Charcoal Wool & French Lilac", "primary": "#33383B", "accent": "#92849E", "styling": "Clean orange blossom and French lavender over dark suiting."},
        {"opt_num": 2, "name": "Dark Olive & Warm Chestnut", "primary": "#3F4436", "accent": "#8A4B2D", "styling": "Barbershop patchouli and cedar anchored by rich leather."},
        {"opt_num": 3, "name": "Deep Navy & Clean Silver", "primary": "#141E30", "accent": "#C0C5C9", "styling": "Italian lemon and cedarwood with crisp metallic accents."}
    ],
    "The Luminous Imperial Tea": [
        {"opt_num": 1, "name": "Burnt Terracotta & Dark Olive", "primary": "#B85D3B", "accent": "#363C2E", "styling": "Saturated warmth echoing Chinese black tea, ginger, and ambroxan."},
        {"opt_num": 2, "name": "Black Tea Amber & Cool Slate", "primary": "#8C4A28", "accent": "#4A5868", "styling": "Chinese black tea and ginger grounded in tailored slate chinos."},
        {"opt_num": 3, "name": "Earthy Olive & Sunlit Bergamot", "primary": "#3E4738", "accent": "#D99B26", "styling": "Crisp citrus sparkle anchored by grounding green wool."}
    ],
    "The Modern Floral Executive": [
        {"opt_num": 1, "name": "Slate Charcoal & Soft Lilac", "primary": "#2C3038", "accent": "#A394AA", "styling": "Clean orange blossom and Ambrofix over dark structured slate."},
        {"opt_num": 2, "name": "Deep Navy & Frosted Sage", "primary": "#172235", "accent": "#8B9B88", "styling": "Crisp ginger and white florals framed by deep executive blue."},
        {"opt_num": 3, "name": "Desert Sand & Washed Indigo", "primary": "#C4B49F", "accent": "#384E69", "styling": "Sun-wrenched modern freshness with tailored denim."}
    ],
    "The Gunmetal Assassin": [
        {"opt_num": 1, "name": "Gunmetal Steel & Bourbon Ochre", "primary": "#3A3E45", "accent": "#B5732A", "styling": "Cold metallic slide and amber bourbon over tactical wool or leather."},
        {"opt_num": 2, "name": "Tactical Black & Smoked Lemon", "primary": "#171717", "accent": "#A89F44", "styling": "Zesty lemon and clary sage cutting through midnight black."},
        {"opt_num": 3, "name": "Deep Charcoal & Raw Leather Tan", "primary": "#282A2E", "accent": "#8F5B34", "styling": "Rugged cedar and amber bourbon balanced by tailored suiting."}
    ],
    "The Deep Abyssal Ocean": [
        {"opt_num": 1, "name": "Deep Nautical Navy & Mineral Sea Grey", "primary": "#122038", "accent": "#8898A6", "styling": "Salty marine accords and green mandarin over abyssal navy."},
        {"opt_num": 2, "name": "Washed Denim & Clean Silver", "primary": "#384860", "accent": "#BFC7CE", "styling": "Heavy marine sillage paired with relaxed weekend denim."},
        {"opt_num": 3, "name": "Dark Slate Olive & Ocean Aqua", "primary": "#303B32", "accent": "#328294", "styling": "Coastal rosemary and cypress rooted in rich green earth."}
    ],
    "The Oceanic Executive": [
        {"opt_num": 1, "name": "Deep Marine Navy & Frosted Steel", "primary": "#0D2A6B", "accent": "#8A9EA7", "styling": "Tailored dark navy overshirt with frosted steel trousers; built for waterfront breezes."},
        {"opt_num": 2, "name": "Washed Denim & Clean Silver", "primary": "#384860", "accent": "#BFC7CE", "styling": "Heavy marine sillage paired with relaxed weekend denim."},
        {"opt_num": 3, "name": "Dark Slate Olive & Ocean Aqua", "primary": "#303B32", "accent": "#328294", "styling": "Coastal rosemary and cypress rooted in rich green earth."}
    ],
    "The Radiant Executive Timber": [
        {"opt_num": 1, "name": "Deep Teak Brown & Washed Mineral Blue", "primary": "#2E1F18", "accent": "#4F6B85", "styling": "Tailored selvedge denim or dark timber trousers with washed mineral blue layer."},
        {"opt_num": 2, "name": "Charcoal Wool & Soft Lilac", "primary": "#2C3038", "accent": "#A394AA", "styling": "Frosted lavender and orange blossom framed by dark charcoal."},
        {"opt_num": 3, "name": "Midnight Navy & Warm Caramel", "primary": "#162032", "accent": "#C2884E", "styling": "Juicy pear and radiating Akigalawood over dark naval suiting."}
    ],
    "The Golden Gourmand Sovereign": [
        {"opt_num": 1, "name": "Dark Espresso & Warm Honey Tan", "primary": "#281D17", "accent": "#C48D47", "styling": "Sweet almond and benzoin resting on dark roasted espresso."},
        {"opt_num": 2, "name": "Midnight Navy & Amber Ochre", "primary": "#182234", "accent": "#D18C38", "styling": "Rich tonka and vanilla contrast against deep suiting blue."},
        {"opt_num": 3, "name": "Charcoal Wool & Burnt Caramel", "primary": "#2F333A", "accent": "#A85926", "styling": "Warm winter gourmand woods with executive tailoring."}
    ],
    "The Intimate Tobacco Seduction": [
        {"opt_num": 1, "name": "Espresso & Spiced Cognac", "primary": "#2A1D15", "accent": "#9E5A2A", "styling": "Cozy tobacco and ginger over rich brown knitwear for close dining."},
        {"opt_num": 2, "name": "Charcoal & Warm Terracotta", "primary": "#2D3136", "accent": "#B85D3B", "styling": "Warm cardamom and amber balanced by tailored charcoal."},
        {"opt_num": 3, "name": "Deep Forest & Caramel Suede", "primary": "#233027", "accent": "#C2884E", "styling": "Earthy autumn woods and golden resinous tobacco."}
    ],
    "The Authentic Caribbean King": [
        {"opt_num": 1, "name": "Palm Green & Coconut Shell Tan", "primary": "#324A38", "accent": "#9C7A58", "styling": "Lime zest, sugar cane, and white rum in island earth tones."},
        {"opt_num": 2, "name": "Nautical Navy & Bleached White", "primary": "#1A2840", "accent": "#F5F5F7", "styling": "Resort-ready tropical air over structured dark naval blue."},
        {"opt_num": 3, "name": "Sunlit Sandstone & Ocean Aqua", "primary": "#B8A284", "accent": "#3D8B99", "styling": "Crisp white rum and coconut water in warm-weather neutrals."}
    ],
    "The Caribbean Mountain Stream": [
        {"opt_num": 1, "name": "Island Palm & Frosted White", "primary": "#234D34", "accent": "#FFFFFF", "styling": "Resort linen shirt with white or natural stone trousers."},
        {"opt_num": 2, "name": "Bleached Sand & Slate Teal", "primary": "#D8CCA3", "accent": "#3D6B73", "styling": "Tropical ozone and citrus balanced over cool coastal teal."},
        {"opt_num": 3, "name": "Nautical Navy & Raw Sugarcane", "primary": "#18253C", "accent": "#DDD1BA", "styling": "Lime and coconut layered over dark structured naval blue."}
    ],
    "The Desert Oud Monarch": [
        {"opt_num": 1, "name": "Midnight Black & Desert Crimson", "primary": "#1A1A1A", "accent": "#801B2B", "styling": "Smoky oud and sweet raspberry over sleek nocturnal darks."},
        {"opt_num": 2, "name": "Dark Chocolate & Burnt Amber", "primary": "#2E1E16", "accent": "#B05A28", "styling": "Dense leatherwood, incense, and warm resinous tones."},
        {"opt_num": 3, "name": "Deep Slate & Smoked Plum", "primary": "#30343F", "accent": "#542E43", "styling": "Incense smoke and dark rosewood with mysterious contrast."}
    ],
    "The Sovereign Agarwood Suite": [
        {"opt_num": 1, "name": "Smoked Charcoal & Rosewood Bronze", "primary": "#2B2D33", "accent": "#8C4F47", "styling": "Agarwood, rosewood, and cardamom in a sovereign corporate or gala cut."},
        {"opt_num": 2, "name": "Deep Espresso & Sage Leaf", "primary": "#261D17", "accent": "#7E8D7B", "styling": "Rich dark timber softened by aromatic herbal tones."},
        {"opt_num": 3, "name": "Midnight Navy & Antique Silver", "primary": "#151C28", "accent": "#A8B0B8", "styling": "High-authority evening woods with cool executive hardware."}
    ],
    "The Tactical Ambroxan Alpha": [
        {"opt_num": 1, "name": "Tactical Gunmetal & Electric Bergamot Blue", "primary": "#2A2C2E", "accent": "#3A6B88", "styling": "Fiery Sichuan pepper and ambroxan over dark technical gear."},
        {"opt_num": 2, "name": "Deep Indigo & Warm Bronze", "primary": "#192338", "accent": "#A66D3B", "styling": "Raw Calabrian bergamot and cedar with warm leather hits."},
        {"opt_num": 3, "name": "Washed Black & Cool Concrete", "primary": "#212121", "accent": "#8C9298", "styling": "Clean, aggressive projection anchored by monochrome neutrals."}
    ],
    "The Mediterranean Blue Powerhouse": [
        {"opt_num": 1, "name": "Midnight Blue & Smoked Incense Grey", "primary": "#121F38", "accent": "#525B66", "styling": "Aquatic citrus, violet leaf, and incense in sharp contrast."},
        {"opt_num": 2, "name": "Charcoal & Crisp Ocean Mist", "primary": "#2D3238", "accent": "#7D9CA8", "styling": "Clean ambroxan projection over executive office charcoal."},
        {"opt_num": 3, "name": "Deep Plum & Weathered Khaki", "primary": "#3F2633", "accent": "#B0A287", "styling": "Black pepper and papyrus anchored by earthy relaxed chinos."}
    ],
    "The Boozy Oak Aristocrat": [
        {"opt_num": 1, "name": "Rich Cognac & Dark Oak Charcoal", "primary": "#8C4820", "accent": "#2A2E33", "styling": "Crisp apple and single malt whiskey over structured dark wool or stadium jacket."},
        {"opt_num": 2, "name": "Bourbon Ochre & Gunmetal Steel", "primary": "#B5732A", "accent": "#3A3E45", "styling": "Amber bourbon and dark cedarwood over heavy wool or leather jacket."},
        {"opt_num": 3, "name": "Espresso & Spiced Cognac", "primary": "#2A1D15", "accent": "#9E5A2A", "styling": "Cozy apple, tobacco, and ginger over rich brown knitwear."}
    ],
    "The Premium Lounge": [
        {"opt_num": 1, "name": "Gunmetal Steel & Bourbon Ochre", "primary": "#3A3E45", "accent": "#B5732A", "styling": "Amber bourbon and dark cedarwood over heavy wool or leather jacket."},
        {"opt_num": 2, "name": "Rich Cognac & Dark Oak Charcoal", "primary": "#8C4820", "accent": "#2A2E33", "styling": "Crisp apple and single malt whiskey over structured dark wool."},
        {"opt_num": 3, "name": "Tactical Black & Smoked Amber", "primary": "#171717", "accent": "#C87D28", "styling": "Deep boozy resonance cutting through sleek nocturnal black."}
    ],
    "The High-Style Executive": [
        {"opt_num": 1, "name": "Charcoal Wool & French Lilac", "primary": "#2B3038", "accent": "#9E92A8", "styling": "Charcoal relaxed trousers with soft heather lilac knit mirroring French lavender."},
        {"opt_num": 2, "name": "Dark Olive & Warm Chestnut", "primary": "#3F4436", "accent": "#8A4B2D", "styling": "Barbershop patchouli and cedar anchored by rich chestnut leather."},
        {"opt_num": 3, "name": "Deep Navy & Clean Silver", "primary": "#141E30", "accent": "#C0C5C9", "styling": "Italian lemon and cedarwood with crisp metallic accents."}
    ],
    "The Tailored Contemporary Alpha": [
        {"opt_num": 1, "name": "Charcoal Slate & Ice Blue", "primary": "#3E444C", "accent": "#A5C9EB", "styling": "Slate tailored trousers with crisp ice-blue dress shirt."},
        {"opt_num": 2, "name": "Deep Navy & Frosted Sage", "primary": "#172235", "accent": "#8B9B88", "styling": "Crisp ginger and white florals framed by deep executive blue."},
        {"opt_num": 3, "name": "Desert Sand & Washed Indigo", "primary": "#C4B49F", "accent": "#384E69", "styling": "Sun-wrenched modern freshness with tailored denim."}
    ],
    "The Power Blue Executive": [
        {"opt_num": 1, "name": "Deep French Blue & Crisp White", "primary": "#0D2A6B", "accent": "#FFFFFF", "styling": "Dark structured blazer and crisp collared poplin."},
        {"opt_num": 2, "name": "Spruce Slate & Frost White", "primary": "#2C3E35", "accent": "#F4F6F8", "styling": "Crisp apple and herbal sage over dark spruce chino and optic white."},
        {"opt_num": 3, "name": "Charcoal & Warm Amber Leather", "primary": "#2B303A", "accent": "#C87D28", "styling": "Grounds bright ginger and amberwood into tailored executive amber."}
    ],
    "The Sicilian Citrus Tea": [
        {"opt_num": 1, "name": "Earthy Olive & Sunlit Ochre", "primary": "#4A5240", "accent": "#D4A373", "styling": "Smart casual linen/knit with warm ochre wrist watch strap."},
        {"opt_num": 2, "name": "Black Tea Amber & Cool Slate", "primary": "#8C4A28", "accent": "#4A5868", "styling": "Chinese black tea and ginger grounded in tailored slate chinos."},
        {"opt_num": 3, "name": "Deep Indigo & Frosted White", "primary": "#1B283E", "accent": "#F2F5F8", "styling": "Radiant ambroxan and sparkling tea with pristine lift."}
    ],
    "The Alpine Tea Stream": [
        {"opt_num": 1, "name": "Black Tea Amber & Cool Slate", "primary": "#8C4A28", "accent": "#4A5868", "styling": "Grounded warm-amber tones over tailored slate chinos."},
        {"opt_num": 2, "name": "Forest Hunter Green & Brushed Brass", "primary": "#1C3325", "accent": "#C5A059", "styling": "Mountain spring water and black tea balanced by deep organic greens."},
        {"opt_num": 3, "name": "Mountain Slate & Crisp Sky Blue", "primary": "#3F4C5A", "accent": "#87A9C7", "styling": "Rushing alpine stream water over clean corporate slate."}
    ],
    "The Sparking Alpine Aromatic": [
        {"opt_num": 1, "name": "Cobalt Blue & Optic White", "primary": "#1A4B8C", "accent": "#FFFFFF", "styling": "High-energy royal blue highlighting green apple, ginger, and rushing mountain spring water."},
        {"opt_num": 2, "name": "Deep Indigo Denim & Heather Sterling", "primary": "#1C2D42", "accent": "#9AA3AB", "styling": "Clean corporate denim and metallic lift reflecting crisp sage and juniper."},
        {"opt_num": 3, "name": "Dark Spruce & Oatmeal Stone", "primary": "#26382B", "accent": "#D1C7BD", "styling": "Captures tart green apple, juniper berries, and herbal sage over neutral linen."}
    ]
}

DEFAULT_PALETTE = {
    "opt_num": 1,
    "name": "Classic Executive Slate & White",
    "primary": "#2F3E46",
    "accent": "#F8F9FA",
    "styling": "Clean tailored neutral wardrobe with subtle brushed steel accent."
}

CUSTOM_CSS = """
<style>
    /* Responsive Global Container */
    @media (max-width: 768px) {
        .main .block-container {
            padding-top: 1rem !important;
            padding-bottom: 2.5rem !important;
            padding-left: 0.75rem !important;
            padding-right: 0.75rem !important;
        }
        /* Force side-by-side columns to stack vertically on mobile */
        [data-testid="column"] {
            width: 100% !important;
            flex: 1 1 100% !important;
            min-width: 100% !important;
            margin-bottom: 0.75rem !important;
        }
        /* Mobile Touch Target sizing */
        .stButton button {
            width: 100% !important;
            height: 48px !important;
            font-size: 15px !important;
            font-weight: 600 !important;
            border-radius: 8px !important;
        }
        /* Tab bar horizontal scroll styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 6px !important;
            padding-bottom: 6px !important;
            overflow-x: auto !important;
            -webkit-overflow-scrolling: touch !important;
        }
        .stTabs [data-baseweb="tab"] {
            padding: 8px 12px !important;
            font-size: 13px !important;
            white-space: nowrap !important;
        }
    }

    /* Core Executive Theme Cards */
    .metric-card {
        background: linear-gradient(145deg, #161B22 0%, #1C2128 100%);
        border-radius: 12px;
        padding: 18px;
        border-left: 6px solid #58A6FF;
        border-top: 1px solid rgba(255, 255, 255, 0.08);
        border-right: 1px solid rgba(255, 255, 255, 0.05);
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        margin-bottom: 14px;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.4);
    }
    .locked-badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.4px;
        background-color: rgba(212, 175, 55, 0.2);
        color: #F1C40F;
        border: 1px solid rgba(241, 196, 15, 0.5);
        margin-right: 6px;
        margin-bottom: 4px;
    }
    .swatch-box {
        display: inline-block;
        width: 22px;
        height: 22px;
        border-radius: 6px;
        vertical-align: middle;
        margin-right: 8px;
        border: 1px solid rgba(255, 255, 255, 0.25);
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.3);
    }
    .badge-tag {
        display: inline-block;
        padding: 3px 8px;
        border-radius: 12px;
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 0.3px;
        background-color: rgba(56, 139, 253, 0.15);
        color: #58A6FF;
        border: 1px solid rgba(56, 139, 253, 0.3);
        margin-right: 4px;
        margin-bottom: 4px;
    }
    .badge-solo {
        display: inline-block;
        padding: 3px 8px;
        border-radius: 12px;
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 0.3px;
        background-color: rgba(235, 142, 60, 0.15);
        color: #F0883E;
        border: 1px solid rgba(235, 142, 60, 0.35);
        margin-right: 4px;
        margin-bottom: 4px;
    }
    .badge-scenario {
        display: inline-block;
        padding: 3px 8px;
        border-radius: 12px;
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 0.3px;
        background-color: rgba(163, 113, 247, 0.15);
        color: #BC8CFF;
        border: 1px solid rgba(163, 113, 247, 0.35);
        margin-right: 4px;
        margin-bottom: 4px;
    }
    .badge-weather {
        display: inline-block;
        padding: 3px 8px;
        border-radius: 12px;
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 0.3px;
        background-color: rgba(57, 211, 83, 0.15);
        color: #39D353;
        border: 1px solid rgba(57, 211, 83, 0.35);
        margin-right: 4px;
        margin-bottom: 4px;
    }
    .sartorial-card {
        background: #161B22;
        border: 1px solid #30363D;
        border-radius: 10px;
        padding: 16px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.35);
        margin-bottom: 12px;
    }
    .capsule-card {
        background: #161B22;
        border: 1px solid #30363D;
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 12px;
    }
    .mobile-weather-bar {
        background: #161B22;
        border: 1px solid #30363D;
        border-radius: 8px;
        padding: 10px 14px;
        margin-bottom: 14px;
        font-size: 13.5px;
        display: flex;
        flex-wrap: wrap;
        justify-content: space-between;
        align-items: center;
    }
</style>
"""

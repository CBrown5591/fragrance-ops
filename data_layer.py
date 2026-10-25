"""Data access, Google Drive synchronization, and state persistence layer."""

import json
import os
from config import NON_PAIRING_SHEETS, SARTORIAL_MAP, SCOPE
from google.oauth2.service_account import Credentials
import gspread
import pandas as pd
import streamlit as st

LOCKED_FITS_FILE = "locked_fits.json"
WEAR_HISTORY_FILE = "wear_history.json"

STANDALONE_MASTER = [
    {
        "Custom Profile Name": "The Crisp Blue Alpha",
        "Top Layer": "Alt. A (YSL Y DNA)",
        "Pairing Type": "Standalone Solo Wear",
        "Base Layer": "None (Unscented Canvas)",
        "Particle Primer Compatible": "Yes",
        "Eligible Scenarios": "WP, EC, LO, NL",
        "Projection Strength": "Strong (5–6 ft / 4 sp cap)",
        "Scent Profile & Notes Breakdown": (
            "Green apple, fresh ginger, clary sage, and clean amberwood. Sharp,"
            " energetic workhorse."
        ),
        "Season_Sheet": "All-Season (6-Band Universal)",
    },
    {
        "Custom Profile Name": "The Luminous Modern Executive",
        "Top Layer": "Alt. Blue Fate (Blue Talisman DNA)",
        "Pairing Type": "Standalone Solo Wear",
        "Base Layer": "None (Unscented Canvas)",
        "Particle Primer Compatible": "Yes",
        "Eligible Scenarios": "WP, EC, DN, LO",
        "Projection Strength": "Strong (5–6 ft / 3-4 sp cap)",
        "Scent Profile & Notes Breakdown": (
            "Juicy pear, bergamot, ginger, and radiant ambroxan/Akigalawood."
            " Modern luminous aura."
        ),
        "Season_Sheet": "Spring / Summer / Early Fall",
    },
    {
        "Custom Profile Name": "The Sovereign Society Executive",
        "Top Layer": "Givenchy Gentleman Society",
        "Pairing Type": "Standalone Solo Wear",
        "Base Layer": "None (Unscented Canvas)",
        "Particle Primer Compatible": "Yes",
        "Eligible Scenarios": "WP, DN, NL",
        "Projection Strength": "Strong (5–6 ft / 4 sp cap)",
        "Scent Profile & Notes Breakdown": (
            "Cardamom, French clary sage, wild narcissus, Haitian vetiver, and"
            " dark vanilla. Universal boardroom king."
        ),
        "Season_Sheet": "All-Season (6-Band Universal)",
    },
    {
        "Custom Profile Name": "The High-Tech Corporate Mind",
        "Top Layer": "Givenchy Pi Neo",
        "Pairing Type": "Standalone Solo Wear",
        "Base Layer": "None (Unscented Canvas)",
        "Particle Primer Compatible": "Yes",
        "Eligible Scenarios": "WP, EC",
        "Projection Strength": "Moderate (3–4 ft)",
        "Scent Profile & Notes Breakdown": (
            "Mandarin, bergamot, herbal myrtle, crystalline cedarwood, and"
            " patchouli. Clean tailored office cool."
        ),
        "Season_Sheet": "Pre-Spring / Spring / Early Fall",
    },
    {
        "Custom Profile Name": "The Modern Mineral Aristocrat",
        "Top Layer": "Valentino Uomo Born in Roma",
        "Pairing Type": "Standalone Solo Wear",
        "Base Layer": "None (Unscented Canvas)",
        "Particle Primer Compatible": "Yes",
        "Eligible Scenarios": "WP, EC, DN",
        "Projection Strength": "Moderate (3–4 ft)",
        "Scent Profile & Notes Breakdown": (
            "Mineral salt accord, violet leaf, fresh ginger, aromatic sage, and"
            " smoky vetiver. Modern street-tailored edge."
        ),
        "Season_Sheet": "Pre-Spring / Spring / Early Fall",
    },
    {
        "Custom Profile Name": "The Alpine Aristocrat",
        "Top Layer": "Alt. Pristine (Aventus x BR540)",
        "Pairing Type": "Standalone Solo Wear",
        "Base Layer": "None (Unscented Canvas)",
        "Particle Primer Compatible": "Yes",
        "Eligible Scenarios": "WP, EC, DN, NL",
        "Projection Strength": "Moderate to Strong (4–5 ft)",
        "Scent Profile & Notes Breakdown": (
            "Crisp pineapple, smoky birch, burnt sugar saffron, and radiant"
            " amberwood. Pristine modern luxury trail."
        ),
        "Season_Sheet": "Pre-Spring / Spring / Fall",
    },
    {
        "Custom Profile Name": "The Seductive Modern Barbershop",
        "Top Layer": "Gucci Guilty Pour Homme",
        "Pairing Type": "Standalone Solo Wear",
        "Base Layer": "None (Unscented Canvas)",
        "Particle Primer Compatible": "Yes",
        "Eligible Scenarios": "WP, EC, DN",
        "Projection Strength": "Moderate (3 ft)",
        "Scent Profile & Notes Breakdown": (
            "Italian lemon, French lavender, orange blossom, and structured"
            " cedarwood/patchouli. Refined clean desk grooming."
        ),
        "Season_Sheet": "Pre-Spring / Spring / Early Fall",
    },
    {
        "Custom Profile Name": "The Luminous Imperial Tea",
        "Top Layer": "Alt. Reality (LV Imagination DNA)",
        "Pairing Type": "Standalone Solo Wear",
        "Base Layer": "None (Unscented Canvas)",
        "Particle Primer Compatible": "Yes",
        "Eligible Scenarios": "WP, EC, LO",
        "Projection Strength": "Moderate (3–4 ft)",
        "Scent Profile & Notes Breakdown": (
            "Chinese black tea, Sicilian citrus, fresh ginger, and sparkling"
            " ambroxan. Spa-like executive refinement."
        ),
        "Season_Sheet": "Spring / High Summer / Early Fall",
    },
    {
        "Custom Profile Name": "The Modern Floral Executive",
        "Top Layer": "Alt. Identity (YSL MYSLF DNA)",
        "Pairing Type": "Standalone Solo Wear",
        "Base Layer": "None (Unscented Canvas)",
        "Particle Primer Compatible": "Yes",
        "Eligible Scenarios": "WP, EC, DN",
        "Projection Strength": "Moderate (3–4 ft)",
        "Scent Profile & Notes Breakdown": (
            "Calabrian bergamot, orange blossom absolute, and crisp Ambrofix."
            " Tailored contemporary executive daily."
        ),
        "Season_Sheet": "Spring / Summer / Early Fall",
    },
    {
        "Custom Profile Name": "The Gunmetal Assassin",
        "Top Layer": "John Wick x Scentbird",
        "Pairing Type": "Standalone Solo Wear",
        "Base Layer": "None (Unscented Canvas)",
        "Particle Primer Compatible": "Yes",
        "Eligible Scenarios": "WP, DN, NL",
        "Projection Strength": "Moderate to Strong (4–5 ft)",
        "Scent Profile & Notes Breakdown": (
            "Cold gunmetal slide accord, spiced lemon, clary sage, and rich"
            " amber bourbon over cedar. Disciplined authority."
        ),
        "Season_Sheet": "Pre-Spring / Fall / Early Winter",
    },
    {
        "Custom Profile Name": "The Deep Abyssal Ocean",
        "Top Layer": "GA Acqua Di Gio Profondo",
        "Pairing Type": "Standalone Solo Wear",
        "Base Layer": "None (Unscented Canvas)",
        "Particle Primer Compatible": "Yes",
        "Eligible Scenarios": "WP, EC, LO",
        "Projection Strength": "Strong (5–6 ft)",
        "Scent Profile & Notes Breakdown": (
            "Deep mineral marine notes, green mandarin, rosemary, and blue"
            " cypress. Waterfront and outdoor humidity defense."
        ),
        "Season_Sheet": "High Summer / Warm Spring",
    },
    {
        "Custom Profile Name": "The Golden Gourmand Sovereign",
        "Top Layer": "Givenchy Pi",
        "Pairing Type": "Standalone Solo Wear",
        "Base Layer": "None (Unscented Canvas)",
        "Particle Primer Compatible": "No",
        "Eligible Scenarios": "DN, EC, WP",
        "Projection Strength": "Moderate to Strong (4–5 ft)",
        "Scent Profile & Notes Breakdown": (
            "Sweet almond, benzoin, tonka bean, and roasted vanilla."
            " Sentimental warmth for cold weather and close quarters."
        ),
        "Season_Sheet": "Crisp Fall / Deep Winter",
    },
    {
        "Custom Profile Name": "The Intimate Tobacco Seduction",
        "Top Layer": "D&G The One for Men",
        "Pairing Type": "Standalone Solo Wear",
        "Base Layer": "None (Unscented Canvas)",
        "Particle Primer Compatible": "Yes",
        "Eligible Scenarios": "DN, WP",
        "Projection Strength": "Intimate to Moderate (2–3 ft)",
        "Scent Profile & Notes Breakdown": (
            "Warm cardamom, fresh ginger, cured tobacco, and cozy amber."
            " Close-proximity evening & date night benchmark."
        ),
        "Season_Sheet": "Early Fall / Crisp Fall / Deep Winter",
    },
    {
        "Custom Profile Name": "The Authentic Caribbean King",
        "Top Layer": "Creed Virgin Island Water",
        "Pairing Type": "Standalone Solo Wear",
        "Base Layer": "None (Unscented Canvas)",
        "Particle Primer Compatible": "Yes",
        "Eligible Scenarios": "LO, EC",
        "Projection Strength": "Moderate (3–4 ft)",
        "Scent Profile & Notes Breakdown": (
            "Crisp Jamaican lime zest, coconut water, white rum, and sugar"
            " cane. High-heat resort and waterfront staple."
        ),
        "Season_Sheet": "High Summer / Vacation",
    },
    {
        "Custom Profile Name": "The Desert Oud Monarch",
        "Top Layer": "House of Kelam (HOK) Nomade Ember",
        "Pairing Type": "Standalone Solo Wear",
        "Base Layer": "None (Unscented Canvas)",
        "Particle Primer Compatible": "No",
        "Eligible Scenarios": "NL, DN",
        "Projection Strength": "Nuclear / Beast Mode (8+ ft / 2 sp cap)",
        "Scent Profile & Notes Breakdown": (
            "Smoked agarwood, incense tears, sweet tart raspberry, and raw"
            " leather. Cold-weather formal evening galas."
        ),
        "Season_Sheet": "Deep Winter / Late Fall",
    },
    {
        "Custom Profile Name": "The Sovereign Agarwood Suite",
        "Top Layer": "House of Kelam (HOK) Oud Noir",
        "Pairing Type": "Standalone Solo Wear",
        "Base Layer": "None (Unscented Canvas)",
        "Particle Primer Compatible": "Yes",
        "Eligible Scenarios": "WP, DN, NL",
        "Projection Strength": "Strong (5–6 ft)",
        "Scent Profile & Notes Breakdown": (
            "Precious agarwood, rosewood, cardamom, Sichuan pepper, and smoky"
            " amber. Authority and evening depth."
        ),
        "Season_Sheet": "Deep Winter / Pre-Spring / Crisp Fall",
    },
    {
        "Custom Profile Name": "The Tactical Ambroxan Alpha",
        "Top Layer": "Dior Sauvage (EDT/EDP)",
        "Pairing Type": "Standalone Solo Wear",
        "Base Layer": "None (Unscented Canvas)",
        "Particle Primer Compatible": "Yes",
        "Eligible Scenarios": "WP, EC, NL, LO",
        "Projection Strength": "Strong (5–6 ft / 3 sp cap)",
        "Scent Profile & Notes Breakdown": (
            "Calabrian bergamot, Sichuan pepper, geranium, and clean metallic"
            " ambroxan. Powerful projection engine."
        ),
        "Season_Sheet": "All-Season (6-Band Universal)",
    },
    {
        "Custom Profile Name": "The Mediterranean Blue Powerhouse",
        "Top Layer": "Versace Dylan Blue",
        "Pairing Type": "Standalone Solo Wear",
        "Base Layer": "None (Unscented Canvas)",
        "Particle Primer Compatible": "No",
        "Eligible Scenarios": "WP, EC, NL, LO",
        "Projection Strength": "Strong (5–6 ft)",
        "Scent Profile & Notes Breakdown": (
            "Aquatic citrus, violet leaf, black pepper, ambroxan, and incense."
            " Clean modern power daily."
        ),
        "Season_Sheet": "Spring / Summer / Early Fall",
    },
    {
        "Custom Profile Name": "The Boozy Oak Aristocrat",
        "Top Layer": "B&BW Whiskey Reserve (Cologne)",
        "Pairing Type": "Standalone Solo Wear",
        "Base Layer": "None (Unscented Canvas)",
        "Particle Primer Compatible": "Yes",
        "Eligible Scenarios": "WP, EC, DN, LO",
        "Projection Strength": "Moderate to Strong (4–5 ft)",
        "Scent Profile & Notes Breakdown": (
            "Crisp red apple, single malt whiskey, and aged white oak barrel"
            " staves. Autumn stadium & lounge refinement."
        ),
        "Season_Sheet": "Early Fall / Crisp Fall",
    },
]


def get_fallback_dataframe():
  data = [
      {
          "Season_Sheet": "Early Fall (Transitional 58°F – 72°F)",
          "Pairing Type": "Body Cream Layer",
          "Base Layer": "Graphite Cream",
          "Particle Primer Compatible": "Yes",
          "Top Layer": "Givenchy Gentleman Society",
          "Custom Profile Name": "The Modern Herbal Executive",
          "Eligible Scenarios": "WP, DN",
          "Projection Strength": "Strong (5–6 ft / 4 sp cap)",
          "Scent Profile & Notes Breakdown": (
              "French sage mirrors Society sage; leatherwood grounds vetiver"
              " and cedarwood."
          ),
      },
      {
          "Season_Sheet": "Early Fall (Transitional 58°F – 72°F)",
          "Pairing Type": "Body Cream Layer",
          "Base Layer": "Mahogany Teakwood",
          "Particle Primer Compatible": "Yes",
          "Top Layer": "Alt. Blue Fate",
          "Custom Profile Name": "The Radiant Executive Timber",
          "Eligible Scenarios": "WP, DN, LO, NL",
          "Projection Strength": "Strong (5–6 ft)",
          "Scent Profile & Notes Breakdown": (
              "Juicy pear, fresh ginger, and orange blossom over rich mahogany"
              " and oak. Magnetic waterfront evening presence."
          ),
      },
      {
          "Season_Sheet": "Early Fall (Transitional 58°F – 72°F)",
          "Pairing Type": "Body Cream Layer",
          "Base Layer": "Graphite Cream",
          "Particle Primer Compatible": "Yes",
          "Top Layer": "Gucci Guilty Pour Homme",
          "Custom Profile Name": "The High-Style Executive",
          "Eligible Scenarios": "WP, DN, EC",
          "Projection Strength": "Moderate (3 ft)",
          "Scent Profile & Notes Breakdown": (
              "French lavender and lemon slice through thawing chill over"
              " structured leatherwood."
          ),
      },
      {
          "Season_Sheet": "Early Fall (Transitional 58°F – 72°F)",
          "Pairing Type": "Body Cream Layer",
          "Base Layer": "Mahogany Teakwood",
          "Particle Primer Compatible": "Yes",
          "Top Layer": "GA Acqua Di Gio Profondo",
          "Custom Profile Name": "The Oceanic Executive",
          "Eligible Scenarios": "WP, EC, LO",
          "Projection Strength": "Moderate to Strong (4–5 ft)",
          "Scent Profile & Notes Breakdown": (
              "Crisp mineral deep sea notes cut through rich timbers and"
              " frosted lavender. Waterfront & open air ready."
          ),
      },
      {
          "Season_Sheet": "Crisp Fall (45°F – 60°F)",
          "Pairing Type": "Body Cream Layer",
          "Base Layer": "Whiskey Reserve",
          "Particle Primer Compatible": "Yes",
          "Top Layer": "John Wick x Scentbird",
          "Custom Profile Name": "The Premium Lounge",
          "Eligible Scenarios": "DN, WP, NL, LO",
          "Projection Strength": "Moderate to Strong (4–5 ft)",
          "Scent Profile & Notes Breakdown": (
              "Amber bourbon and cedarwood lock directly onto whiskey and oak."
              " Warm stadium & chilly evening benchmark."
          ),
      },
      {
          "Season_Sheet": "Spring (Warming 55°F – 70°F)",
          "Pairing Type": "Cologne Mixology",
          "Base Layer": "Alt. Splish (D&G Light Blue)",
          "Particle Primer Compatible": "Yes",
          "Top Layer": "Alt. Reality (LV Imagination)",
          "Custom Profile Name": "The Sicilian Citrus Tea",
          "Eligible Scenarios": "EC, WP, LO",
          "Projection Strength": "Moderate (3–4 ft)",
          "Scent Profile & Notes Breakdown": (
              "Mandarin and grapefruit peel blend into black tea, ginger, and"
              " ambroxan."
          ),
      },
      {
          "Season_Sheet": "High Summer (75°F – 95°F+)",
          "Pairing Type": "Body Cream Layer",
          "Base Layer": "Ocean Cream",
          "Particle Primer Compatible": "Yes",
          "Top Layer": "Alt. Blue Fate (Blue Talisman)",
          "Custom Profile Name": "The Luminous Azure Sea",
          "Eligible Scenarios": "EC, WP, LO",
          "Projection Strength": "Moderate to Strong (4–5 ft)",
          "Scent Profile & Notes Breakdown": (
              "Juicy pear and Akigalawood float over coastal air and blue"
              " cypress."
          ),
      },
      {
          "Season_Sheet": "High Summer (75°F – 95°F+)",
          "Pairing Type": "Body Cream Layer",
          "Base Layer": "Freshwater Cream",
          "Particle Primer Compatible": "Yes",
          "Top Layer": "Creed Virgin Island Water",
          "Custom Profile Name": "The Caribbean Mountain Stream",
          "Eligible Scenarios": "LO, EC",
          "Projection Strength": "Moderate (3–4 ft)",
          "Scent Profile & Notes Breakdown": (
              "Lime zest, coconut water, and white rum gliding over mountain"
              " spring water and crisp bergamot."
          ),
      },
  ]
  return pd.DataFrame(data)


def clean_matrix_columns(df):
  col_map = {
      'Pairing Type': 'Pairing Type',
      'Base Layer': 'Base Layer',
      'Top Layer': 'Top Layer',
      'Custom Profile Name': 'Custom Profile Name',
      'Eligible Scenarios': 'Eligible Scenarios',
      'Projection Strength': 'Projection Strength',
      'Scent Profile & Notes Breakdown': 'Scent Profile & Notes Breakdown',
      'Particle Primer Compatible': 'Particle Primer Compatible',
  }
  for orig in df.columns:
    clean_orig = str(orig).strip()
    for standard in col_map:
      if (
          clean_orig.lower() == standard.lower()
          or standard.lower() in clean_orig.lower()
      ):
        df.rename(columns={orig: standard}, inplace=True)
        break
  return df


@st.cache_data(
    ttl=300, show_spinner="Syncing with Fragrance Matrix in Google Drive..."
)
def fetch_matrix_from_drive():
  solo_df = pd.DataFrame(STANDALONE_MASTER)

  if "gcp_service_account" not in st.secrets:
    return (
        pd.concat([get_fallback_dataframe(), solo_df], ignore_index=True),
        SARTORIAL_MAP,
    )

  try:
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"], scopes=SCOPE
    )
    client = gspread.authorize(creds)
    sheet_name = st.secrets.get("spreadsheet_name", "Fragrance Matrix")
    spreadsheet = client.open(sheet_name)

    all_dfs = []
    drive_sartorial = {}
    for ws in spreadsheet.worksheets():
      ws_title_lower = ws.title.strip().lower()

      if "sartorial" in ws_title_lower:
        s_records = ws.get_all_records()
        for r in s_records:
          p_name = str(
              r.get("Custom Scent Profile Name")
              or r.get("Custom Profile Name")
              or ""
          ).strip()
          base = str(
              r.get("Base Layer / Entity") or r.get("Base Layer") or ""
          ).strip()
          top = str(
              r.get("Top Layer / Partner") or r.get("Top Layer") or ""
          ).strip()

          opts = []
          for opt_idx in [1, 2, 3]:
            o_name = str(r.get(f"Option {opt_idx}: Palette Name") or "").strip()
            o_prim = str(
                r.

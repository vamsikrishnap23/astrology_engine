import streamlit as st
import datetime
import base64
import os
from streamlit.components.v1 import html
import swisseph as swe
import importlib
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

from astro_core.chart_logic import (
    compute_planets_in_varga,
    get_sign_labels
)
from astro_core.planetary_info import compute_planetary_info_telugu
from astro_core.constants import TELUGU_PLANETS
from astro_core.vimshottari_dashas import compute_vimsottari_dashas
from astro_core.calculations import get_julian_day
from astro_core.panchang import get_panchang_minimal
from astro_core.shad_bala import compute_shadbala

# -------------------- Streamlit Config --------------------
st.set_page_config(page_title="Jyotish Engine", layout="centered")
st.title("🪐 Jyotish Engine")

# -------------------- Input Form --------------------
with st.form("input_form"):
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Name", "Vamsi")
        date = st.date_input("Date of Birth", datetime.date(2005, 11, 23), min_value=datetime.date(1900,1,1), max_value=datetime.date(2200,1,1))
        hour = st.number_input("Hour (24h)", 0, 23, 15)
        minute = st.number_input("Minute", 0, 59, 35)
        second = st.number_input("Second", 0, 59, 0)
    with col2:
        lat = st.number_input("Latitude", -90.0, 90.0, 17.385)
        lon = st.number_input("Longitude", -180.0, 180.0, 78.4867)
        tz = st.number_input("Timezone Offset (e.g. 5.5)", -12.0, 14.0, 5.5)
        language = st.selectbox("Language", ["English", "Telugu"])

    submitted = st.form_submit_button("Generate All Charts")

# -------------------- Utility Function --------------------
def jd_to_date(jd):
    y, m, d, frac = swe.revjul(jd, swe.GREG_CAL)
    total_seconds = frac * 86400
    hh = int(total_seconds // 3600)
    mm = int((total_seconds % 3600) // 60)
    ss = int(total_seconds % 60)
    return datetime.datetime(y, m, d, min(hh, 23), min(mm, 59), min(ss, 59))

# --- Panchang Section ---
if submitted:
    jd = get_julian_day(date.year, date.month, date.day, hour, minute, second, tz)
    panchang = get_panchang_minimal(jd, lat, lon, tz)

    st.markdown("## 🗓️ పంచాంగం (Panchang)")
    panchang_df = pd.DataFrame([
    {"Property": "Nakshatram", "Value": str(panchang["Nakshatram"])},
    {"Property": "Padam", "Value": str(panchang["Padam"])},
    {"Property": "Rasi", "Value": str(panchang["Rasi"])},
    {"Property": "Vaaram", "Value": str(panchang["Vaaram"])},
    ])
    st.table(panchang_df)




# -------------------- Main Processing --------------------
if submitted:
    # Create charts folder if not exists
    charts_folder = "charts"
    os.makedirs(charts_folder, exist_ok=True)

    # List of Vargas to generate
    varga_list = [
        (1, "D1 (Rāśi)"),
        (2, "D2 (Hora)"),
        (3, "D3 (Drekkana)"),
        (4, "D4 (Chaturthamsha)"),
        (7, "D7 (Saptamsha)"),
        (9, "D9 (Navamsa)"),
        (10, "D10 (Dashamsha)"),
        (12, "D12 (Dwadashamsha)"),
        (16, "D16 (Shodashamsha)"),
        (20, "D20 (Vimshamsha)"),
        (27, "D27 (Bhamsha)"),
        (30, "D30 (Trimsamsha)"),
        (40, "D40 (Khavedamsha)"),
        (45, "D45 (Akshavedamsha)"),
        (60, "D60 (Shastiamsa)"),
    ]

    sign_labels = get_sign_labels(language="English")
    rev_sign_labels = {v: k for k, v in sign_labels.items()}

    for varga_num, varga_label in varga_list:
        st.markdown(f"## {varga_label} Chart")

        planets_in_sign = compute_planets_in_varga(
            date.year, date.month, date.day, hour, minute, second, lat, lon, tz, varga_num
        )

        # Ascendant sign lookup
        asc_sign_num = next((sign for sign, pl in planets_in_sign.items() if "Ascendant" in pl), None)
        if not asc_sign_num:
            st.error("Ascendant not found in chart data.")
            continue

        asc_sign = sign_labels.get(((asc_sign_num - 1) % 12) + 1, sign_labels[1])

        # Chart creation
        import jyotichart
        importlib.reload(jyotichart)
        import jyotichart as chart

        mychart = chart.SouthChart(varga_label + " Chart", name, IsFullChart=True)
        mychart.set_ascendantsign(asc_sign)

        planet_symbols = {
            "Sun": "Su", "Moon": "Mo", "Mars": "Ma", "Mercury": "Me",
            "Jupiter": "Ju", "Venus": "Ve", "Saturn": "Sa",
            "Rahu": "Ra", "Ketu": "Ke", "Ascendant": "As"
        }

        asc_sign_num_for_calc = rev_sign_labels[asc_sign]
        for sign_num in range(1, 13):
            for planet in planets_in_sign.get(sign_num, []):
                if planet == "Ascendant":
                    continue
                if planet in planet_symbols:
                    house_num = (sign_num - asc_sign_num_for_calc) % 12 + 1
                    mychart.add_planet(planet, planet_symbols[planet], house_num)

        mychart.updatechartcfg(aspect=False)

        # Save chart permanently to charts folder
        chart_filename = f"{charts_folder}/{varga_label.replace(' ', '_').replace('(', '').replace(')', '')}_{name.replace(' ', '_')}.svg"
        mychart.draw(os.path.dirname(chart_filename), os.path.splitext(os.path.basename(chart_filename))[0], "svg")

        # Display SVG
        if os.path.exists(chart_filename):
            with open(chart_filename, "rb") as f:
                svg_bytes = f.read()
            b64 = base64.b64encode(svg_bytes).decode()
            html(f'<embed type="image/svg+xml" src="data:image/svg+xml;base64,{b64}" width="500" height="500">', height=550)
        else:
            st.error(f"Could not find SVG file: {chart_filename}")

    # -------------------- Planet Table --------------------
    st.markdown("## గ్రహ స్థితి పట్టిక")
    planetary_info = compute_planetary_info_telugu(
        date.year, date.month, date.day,
        hour, minute, second,
        lat, lon, tz
    )
    st.table([
        {
            "గ్రహం": TELUGU_PLANETS.get(p["planet"], p["planet"]),
            "డిగ్రీలు": p["degrees"],
            "రాశి": p["rasi"],
            "రాశి అధిపతి": p["rasi_adhipathi"],
            "నక్షత్రం": p["nakshatram"],
            "పదం": p["padam"],
            "వక్రగతి": p["retrogration"]
        } for p in planetary_info
    ])

    # -------------------- Vimshottari Dasha --------------------
    st.markdown("## వింశోత్తరి దశా పట్టిక (Vimshottari Dasha Table)")

    jd_birth = get_julian_day(date.year, date.month, date.day, hour, minute, second, tz)
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    flag = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
    moon_long = swe.calc_ut(jd_birth, swe.MOON, flag)[0][0] % 360

    dashas = compute_vimsottari_dashas(moon_long, jd_birth)

    for maha in dashas:
        st.markdown(f"### మహాదశ: {maha['lord']}")
        antar_table = []
        for antar in maha["antardashas"]:
            antar_table.append({
                "అంతర్దశ": antar["antardasha_lord"],
                "ప్రారంభం": jd_to_date(antar["start_jd"]).strftime("%Y-%m-%d"),
                "ముగింపు": jd_to_date(antar["end_jd"]).strftime("%Y-%m-%d")
            })
        st.table(pd.DataFrame(antar_table).astype(str))

    # -------------------- Shadbala --------------------
    def get_chart_data_stub(planet_name):
        # Stubbed version; you'll replace with real chart logic.
        # You already calculate many of these values inside your system.
        raise NotImplementedError("You need to hook this to your actual planetary data logic.")

    st.markdown("## 🔯 శడ్బల పట్టిక (Shadbala Table)")

    try:
        shadbala_data = compute_shadbala(jd_birth, lat, lon, tz, get_chart_data_stub)
        shadbala_df = pd.DataFrame([
            {
                "Planet": planet,
                "Sthana": round(data["Sthana"], 2),
                "Dig": round(data["Dig"], 2),
                "Kala": round(data["Kala"], 2),
                "Cheshta": round(data["Cheshta"], 2),
                "Naisargika": round(data["Naisargika"], 2),
                "Drik": round(data["Drik"], 2),
                "Total": round(data["Total"], 2),
                "Required": round(data["Required"], 2),
                "Percent": f'{data["Percent"]}%'
            }
            for planet, data in shadbala_data.items()
        ])
        st.dataframe(shadbala_df)

        # -------------------- Shadbala Bar Chart --------------------
        st.markdown("### 📊 Shadbala Total vs Required (Virupa Strength)")
        plt.figure(figsize=(10, 5))
        sns.barplot(
            data=shadbala_df,
            x="Planet",
            y="Total",
            color='green',
            label="Total Bala"
        )
        sns.barplot(
            data=shadbala_df,
            x="Planet",
            y="Required",
            color='red',
            alpha=0.5,
            label="Required Bala"
        )
        plt.ylabel("Virupas")
        plt.title("Shadbala Total vs Required")
        plt.legend()
        st.pyplot(plt.gcf())
    except NotImplementedError as e:
        st.warning("Shadbala not computed: " + str(e))


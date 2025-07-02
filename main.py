import streamlit as st
import datetime
import base64
import os
from streamlit.components.v1 import html
import swisseph as swe
import importlib
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
from astro_core.shadbala import compute_shadbala

# Import Ashtakavarga logic
from astro_core.ashtakavarga import Ashtakavarga, OSUN, OMOON, OMERCURY, OVENUS, OMARS, OJUPITER, OSATURN, OASCENDANT, REKHA

st.set_page_config(page_title="Jyotish Engine", layout="centered")
st.title("Jyotish Engine")

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

def jd_to_date(jd):
    y, m, d, frac = swe.revjul(jd, swe.GREG_CAL)
    total_seconds = frac * 86400
    hh = int(total_seconds // 3600)
    mm = int((total_seconds % 3600) // 60)
    ss = int(total_seconds % 60)
    return datetime.datetime(y, m, d, min(hh, 23), min(mm, 59), min(ss, 59))

def get_rasi_for_ashtakavarga(planets_in_sign):
    planet_order = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Ascendant"]
    planet_signs = [None] * 8
    for sign_num, planets in planets_in_sign.items():
        for planet in planets:
            if planet in planet_order:
                idx = planet_order.index(planet)
                planet_signs[idx] = (sign_num - 1) % 12
            elif planet == "Ascendant":
                planet_signs[7] = (sign_num - 1) % 12
    if planet_signs[7] is None:
        planet_signs[7] = 0
    def get_rasi(planet_idx):
        return planet_signs[planet_idx]
    return get_rasi

def ashtakavarga_rekha_table(ashta, planet_labels, sign_labels):
    data = []
    for pidx in range(7):  # Only Sun to Saturn (not Ascendant)
        row = [planet_labels[pidx]]
        for rasi in range(12):
            row.append(ashta.getItem(REKHA, pidx, rasi))
        data.append(row)
    df = pd.DataFrame(data, columns=["Planet"] + [sign_labels[i] for i in range(12)])
    # Add Sarva row (sum of Sun–Saturn only)
    sarva = ["Sarva"] + [sum(ashta.getItem(REKHA, pidx, rasi) for pidx in range(7)) for rasi in range(12)]
    df.loc[len(df)] = sarva
    return df

def sarva_ashtakavarga_svg_chart(sarva, sign_labels, asc_sign_num, name, folder, filename):
    """
    Draws a South Indian style chart with Sarva values using jyotichart.
    - sarva: list of 12 integers (Sarva for each sign, Aries=0)
    - sign_labels: list of sign names (1-based)
    - asc_sign_num: 1-based sign number for Ascendant
    - name: chart owner name
    - folder: output folder
    - filename: file name (without extension)
    """
    import jyotichart
    importlib.reload(jyotichart)
    chart = jyotichart.SouthChart("Sarva Ashtakavarga Chart", name, IsFullChart=True)
    # Place Sarva values as "planets" in each sign
    for sign_num in range(1, 13):
        value = sarva[sign_num - 1]
        label = str(value)
        chart.add_planet(label, label, sign_num)
    chart.set_ascendantsign(sign_labels[asc_sign_num])
    chart.updatechartcfg(aspect=False)
    chart.draw(folder, filename, "svg")

if submitted:
    jd = get_julian_day(date.year, date.month, date.day, hour, minute, second, tz)
    panchang = get_panchang_minimal(jd, lat, lon, tz)

    st.markdown("## 🗓️ పంచాంగం (Panchang)")
    panchang_df = pd.DataFrame([
        {"Property": "Nakshatram", "Value": str(panchang["Nakshatram"])},
        {"Property": "Padam", "Value": str(panchang["Padam"])},
        {"Property": "Rasi", "Value": str(panchang["Rasi"])},
        {"Property": "Vaaram", "Value": str(panchang["Vaaram"])}
    ])
    st.table(panchang_df)

    charts_folder = "charts"
    os.makedirs(charts_folder, exist_ok=True)

    varga_list = [
        (1, "D1 (Rāśi)"), (2, "D2 (Hora)"), (3, "D3 (Drekkana)"), (4, "D4 (Chaturthamsha)"),
        (7, "D7 (Saptamsha)"), (9, "D9 (Navamsa)"), (10, "D10 (Dashamsha)"), (12, "D12 (Dwadashamsha)"),
        (16, "D16 (Shodashamsha)"), (20, "D20 (Vimshamsha)"), (27, "D27 (Bhamsha)"), (30, "D30 (Trimsamsha)"),
        (40, "D40 (Khavedamsha)"), (45, "D45 (Akshavedamsha)"), (60, "D60 (Shastiamsa)")
    ]

    sign_labels = get_sign_labels(language="English")
    rev_sign_labels = {v: k for k, v in sign_labels.items()}

    for varga_num, varga_label in varga_list:
        st.markdown(f"## {varga_label} Chart")
        planets_in_sign = compute_planets_in_varga(date.year, date.month, date.day, hour, minute, second, lat, lon, tz, varga_num)

        asc_sign_num = next((sign for sign, pl in planets_in_sign.items() if "Ascendant" in pl), None)
        if not asc_sign_num:
            st.error("Ascendant not found in chart data.")
            continue

        asc_sign = sign_labels.get(((asc_sign_num - 1) % 12) + 1, sign_labels[1])

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
                if planet == "Ascendant": continue
                if planet in planet_symbols:
                    house_num = (sign_num - asc_sign_num_for_calc) % 12 + 1
                    mychart.add_planet(planet, planet_symbols[planet], house_num)

        mychart.updatechartcfg(aspect=False)

        chart_filename = f"{charts_folder}/{varga_label.replace(' ', '_').replace('(', '').replace(')', '')}_{name.replace(' ', '_')}.svg"
        mychart.draw(os.path.dirname(chart_filename), os.path.splitext(os.path.basename(chart_filename))[0], "svg")

        if os.path.exists(chart_filename):
            with open(chart_filename, "rb") as f:
                svg_bytes = f.read()
            b64 = base64.b64encode(svg_bytes).decode()
            html(f'<embed type="image/svg+xml" src="data:image/svg+xml;base64,{b64}" width="500" height="500">', height=550)
        else:
            st.error(f"Could not find SVG file: {chart_filename}")

        # ---- Ashtakavarga: Only for D1 (Rāśi) ----
        if varga_num == 1:
            st.markdown("### Ashtakavarga (Rekha, Sarva) for D1 (Rāśi) Chart")
            get_rasi = get_rasi_for_ashtakavarga(planets_in_sign)
            ashta = Ashtakavarga(get_rasi)
            ashta.update()

            planet_labels = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]
            sign_labels_row = [sign_labels[i+1] for i in range(12)]  # sign_labels is 1-based

            rekha_df = ashtakavarga_rekha_table(ashta, planet_labels, sign_labels_row)
            st.markdown("#### Rekha Table (Binna Ashtakavarga)")
            st.dataframe(rekha_df, use_container_width=True)

            # Sarva calculation: sum of Sun–Saturn only (not Ascendant)
            sarva = [sum(ashta.getItem(REKHA, pidx, rasi) for pidx in range(7)) for rasi in range(12)]

            # Draw Sarva Ashtakavarga chart as SVG with Sarva values as labels
            sarva_chart_filename = f"{charts_folder}/Sarva_Ashtakavarga_{name.replace(' ', '_')}.svg"
            sarva_ashtakavarga_svg_chart(
                sarva=sarva,
                sign_labels=sign_labels,
                asc_sign_num=asc_sign_num,
                name=name,
                folder=charts_folder,
                filename=f"Sarva_Ashtakavarga_{name.replace(' ', '_')}"
            )
            if os.path.exists(sarva_chart_filename):
                with open(sarva_chart_filename, "rb") as f:
                    svg_bytes = f.read()
                b64 = base64.b64encode(svg_bytes).decode()
                st.markdown("#### Sarva Ashtakavarga Chart (South Indian Style)")
                html(f'<embed type="image/svg+xml" src="data:image/svg+xml;base64,{b64}" width="500" height="500">', height=550)
            else:
                st.error(f"Could not find SVG file: {sarva_chart_filename}")

    st.markdown("## గ్రహ స్థితి పట్టిక")
    planetary_info = compute_planetary_info_telugu(date.year, date.month, date.day, hour, minute, second, lat, lon, tz)
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

    st.markdown("## వింశోత్తరి దశా పట్టిక")
    jd_birth = jd
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
                "ప్రారమ్భం": jd_to_date(antar["start_jd"]).strftime("%Y-%m-%d"),
                "ముగింపు": jd_to_date(antar["end_jd"]).strftime("%Y-%m-%d")
            })
        st.table(pd.DataFrame(antar_table).astype(str))

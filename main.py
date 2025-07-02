import streamlit as st
import datetime
import base64
import os
from streamlit.components.v1 import html
import swisseph as swe
import importlib
import pandas as pd
import sys

import jyotichart
importlib.reload(jyotichart)




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
from astro_core.ashtakavarga import Ashtakavarga, OSUN, OMOON, OMERCURY, OVENUS, OMARS, OJUPITER, OSATURN, OASCENDANT, REKHA
from astro_core.progression import compute_progressed_chart, get_sign_number, get_sign_labels as get_sign_labels_prog

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
    import jyotichart
    importlib.reload(jyotichart)
    chart = jyotichart.SouthChart("Sarva Ashtakavarga Chart", name, IsFullChart=True)

    # Add dummy Sun (to avoid internal chart error)
    chart.add_planet("Sun", "", 1)  # dummy entry in 1st sign

    for sign_num in range(1, 13):
        value = sarva[sign_num - 1]
        chart.add_planet(f"Sarva{sign_num}", str(value), sign_num)

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

            # --- Build full planets_in_sign for Ashtakavarga chart (Sun, Moon, Mercury, Venus, Mars, Jupiter, Saturn, Rahu, Ketu, Ascendant) ---
            planet_labels = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Ascendant"]
            ashta_planets_in_sign = {i: [] for i in range(1, 13)}
            # Sun–Saturn, Ascendant
            for idx, planet in enumerate(planet_labels):
                sign_num = get_rasi(idx) + 1
                ashta_planets_in_sign[sign_num].append(planet)
            # Rahu/Ketu from D1 chart
            for sign_num, planets in planets_in_sign.items():
                for planet in planets:
                    if planet == "Rahu" or planet == "Ketu":
                        ashta_planets_in_sign[sign_num].append(planet)
    
            # from rekha_sarva_chart import draw_rekha_sarva_only_chart



            # --- Rekha Table and Sarva Ashtakavarga Chart ---
            planet_labels_table = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]
            sign_labels_row = [sign_labels[i + 1] for i in range(12)]  # 1-based

            rekha_df = ashtakavarga_rekha_table(ashta, planet_labels_table, sign_labels_row)
            st.markdown("#### Rekha Table (Binna Ashtakavarga)")
            st.dataframe(rekha_df, use_container_width=True)

            # ➕ Sarva Ashtakavarga South Indian Chart (with Rekha values)
            sarva = [sum(ashta.getItem(REKHA, pidx, rasi) for pidx in range(7)) for rasi in range(12)]

            # ✅ Convert Sarva values list to dict with lowercase sign keys
            # sign_order = [
            #     "aries", "taurus", "gemini", "cancer", "leo", "virgo",
            #     "libra", "scorpio", "sagittarius", "capricorn", "aquarius", "pisces"
            # ]
            # sign_values = dict(zip(sign_order, sarva))
            # ascendantsign = sign_labels[asc_sign_num].lower()

            # # ✅ Draw SVG chart
            # sarva_chart_filename = f"SarvaAshtakavarga_{name.replace(' ', '_')}"
            # draw_rekha_sarva_only_chart(
            #     sign_values=sign_values,
            #     ascendantsign=ascendantsign,
            #     charts_folder=charts_folder,
            #     filename=sarva_chart_filename
            # )

            # # ✅ Embed SVG into Streamlit
            # full_chart_path = os.path.join(charts_folder, f"{sarva_chart_filename}.svg")
            # if os.path.exists(full_chart_path):
            #     with open(full_chart_path, "rb") as f:
            #         svg_bytes = f.read()
            #     b64 = base64.b64encode(svg_bytes).decode()
            #     st.markdown("#### Sarva Ashtakavarga Chart (South Indian Style)")
            #     html(f'<embed type="image/svg+xml" src="data:image/svg+xml;base64,{b64}" width="500" height="500">', height=550)
            # else:
            #     st.error(f"Could not find SVG file: {full_chart_path}")

    # --- Progression Chart Section ---
    st.markdown("## Progression Chart (Secondary Progression)")

    progression_mode = st.radio("Progression by", ["Age (years)", "Target Date"], index=0)
    if progression_mode == "Age (years)":
        progression_age = st.number_input("Progression Age (years)", min_value=1, max_value=120, value=20)
        birth_datetime = datetime.datetime(date.year, date.month, date.day, hour, minute, second)
        target_date = birth_datetime + datetime.timedelta(days=progression_age)
        age_years = progression_age
    else:
        prog_date = st.date_input("Progression Target Date", datetime.date.today(), min_value=date)
        target_date = datetime.datetime(prog_date.year, prog_date.month, prog_date.day, hour, minute, second)
        birth_datetime = datetime.datetime(date.year, date.month, date.day, hour, minute, second)
        age_years = (target_date - birth_datetime).days / 365.2425

    birth_jd = get_julian_day(date.year, date.month, date.day, hour, minute, second, tz)
    chart = compute_progressed_chart(birth_jd, age_years, lat, lon, tz_offset=tz)
    progressed_positions = chart["planets"]
    ascendant = chart["ascendant"]

    # Build planets_in_sign for progression (including Rahu/Ketu)
    progression_planets_in_sign = {i: [] for i in range(1, 13)}
    for planet in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]:
        if planet in progressed_positions:
            deg = progressed_positions[planet]["longitude"]
            sign_num = int(deg // 30) + 1
            progression_planets_in_sign[sign_num].append(planet)
    # Add Ascendant
    asc_sign_num = int(ascendant // 30) + 1
    progression_planets_in_sign[asc_sign_num].append("Ascendant")

    # Draw progression chart using the same logic as divisional charts
    import jyotichart
    importlib.reload(jyotichart)
    prog_chart = jyotichart.SouthChart("Progression Chart", name, IsFullChart=True)
    prog_chart.set_ascendantsign(sign_labels[asc_sign_num])

    planet_symbols = {
        "Sun": "Su", "Moon": "Mo", "Mars": "Ma", "Mercury": "Me",
        "Jupiter": "Ju", "Venus": "Ve", "Saturn": "Sa",
        "Rahu": "Ra", "Ketu": "Ke", "Ascendant": "As"
    }
    asc_sign_num_for_calc = asc_sign_num
    for sign_num in range(1, 13):
        for planet in progression_planets_in_sign.get(sign_num, []):
            if planet == "Ascendant": continue
            if planet in planet_symbols:
                house_num = (sign_num - asc_sign_num_for_calc) % 12 + 1
                prog_chart.add_planet(planet, planet_symbols[planet], house_num)

    prog_chart.updatechartcfg(aspect=False)
    prog_chart_filename = f"{charts_folder}/Progression_{name.replace(' ', '_')}.svg"
    prog_chart.draw(charts_folder, f"Progression_{name.replace(' ', '_')}", "svg")
    if os.path.exists(prog_chart_filename):
        with open(prog_chart_filename, "rb") as f:
            svg_bytes = f.read()
        b64 = base64.b64encode(svg_bytes).decode()
        st.markdown("### Progression Chart (South Indian Style)")
        html(f'<embed type="image/svg+xml" src="data:image/svg+xml;base64,{b64}" width="500" height="500">', height=550)
    else:
        st.error(f"Could not find SVG file: {prog_chart_filename}")

    # Table for progression chart
    progression_df = []
    sign_labels_prog = get_sign_labels_prog(language="English")
    for planet in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]:
        if planet in progressed_positions:
            deg = progressed_positions[planet]["longitude"]
            sign_num = int(deg // 30) + 1
            progression_df.append({
                "Planet": planet,
                "Longitude": f"{deg:.2f}°",
                "Sign": sign_labels_prog[sign_num],
                "Sign Num": sign_num,
                "Speed": f"{progressed_positions[planet]['speed']:.5f}",
                "Retrograde": "R" if progressed_positions[planet]["retrograde"] else ""
            })
    # Ascendant
    progression_df.append({
        "Planet": "Ascendant",
        "Longitude": f"{ascendant:.2f}°",
        "Sign": sign_labels_prog[asc_sign_num],
        "Sign Num": asc_sign_num,
        "Speed": "",
        "Retrograde": ""
    })
    st.markdown("### Progressed Planetary Positions")
    st.dataframe(pd.DataFrame(progression_df), use_container_width=True)

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


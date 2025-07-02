import streamlit as st
import datetime
import base64
import os
from streamlit.components.v1 import html
import swisseph as swe
import importlib
import pandas as pd
import sys
import time
import jyotichart
importlib.reload(jyotichart)

from datetime import datetime as dt




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

st.set_page_config(page_title="Jyotish Engine", layout="wide")
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




tabs = st.tabs(["View 1","Div Charts", "Rekha & Prog", "All"])

def draw_and_fix_svg_chart(chart_obj, charts_folder, filename_base):
    chart_obj.draw(charts_folder, filename_base, "svg")
    svg_path = os.path.join(charts_folder, f"{filename_base}.svg")
    if os.path.exists(svg_path):
        with open(svg_path, "r", encoding="utf-16") as f:
            svg_text = f.read()
        svg_text = svg_text.replace("stroke:red", "stroke:white")  # or 'black' or 'none'
        with open(svg_path, "w", encoding="utf-16") as f:
            f.write(svg_text)
        return svg_path
    else:
        st.error(f"Could not find SVG file: {svg_path}")
        return None




def display_svg_chart(file_path: str, title: str = ""):
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-16") as f:
            svg_text = f.read()
        svg_text = svg_text.replace("stroke:red", "stroke:white")
        b64 = base64.b64encode(svg_text.encode("utf-16")).decode()
        if title:
            st.markdown(f"### {title}")
        st.components.v1.html(
            f'<embed type="image/svg+xml" src="data:image/svg+xml;base64,{b64}" width="500" height="500">',
            height=550
        )
    else:
        st.error(f"Could not find SVG file: {file_path}")



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
        chart.add_planet(f"Sarva{sign_num}", str(value), sign_num, colour="black")

    chart.set_ascendantsign(sign_labels[asc_sign_num])
    house_colors = ["white"] * 12  # All houses white

    chart.updatechartcfg(
        aspect=False,              
        clr_background="white",    
        clr_outbox="black",        
        clr_line="black",         
        clr_Asc="darkblue",        
        clr_houses=house_colors    
    )

    chart.draw(folder, filename, "svg")


if submitted:
    with tabs[0]:
        import time
        time.sleep(3)
        charts_folder = "charts"
        name_safe = name.replace(" ", "_")

        # --- Panchangam First ---
        panchang_path = f"{charts_folder}/panchang_details_{name_safe}.csv"
        if os.path.exists(panchang_path):
            st.markdown("## 🗓️ పంచాంగం (Panchangam)")
            df_panchang = pd.read_csv(panchang_path)
            st.dataframe(df_panchang, use_container_width=True, hide_index=True)
        else:
            st.warning("Panchangam info not found.")

        # --- D1 & D9 Charts ---
        st.markdown("## 📊 D1 & D9 Charts")

        # Define chart file paths and labels
        d_charts = [
            ("D1_Rāśi", "D1 (రాశి)"),
            ("D9_Navamsa", "D9 (నవాంశం)")
        ]

        cols = st.columns(2)

        for (chart_key, label), col in zip(d_charts, cols):
            chart_path = f"{charts_folder}/{chart_key}_{name_safe}.svg"
            if os.path.exists(chart_path):
                with open(chart_path, "rb") as f:
                    svg_bytes = f.read()
                b64 = base64.b64encode(svg_bytes).decode()
                with col:
                    st.markdown(f"### {label}")
                    html(
                        f'<embed type="image/svg+xml" src="data:image/svg+xml;base64,{b64}" width="100%" height="500">',
                        height=550
                    )
            else:
                with col:
                    st.error(f"Missing chart: {os.path.basename(chart_path)}")



        # --- Planetary Info Table ---
        planetary_csv = f"{charts_folder}/planetary_info_telugu_{name_safe}.csv"
        if os.path.exists(planetary_csv):
            st.markdown("## గ్రహ స్థితి పట్టిక (Planetary Positions)")
            df_planets = pd.read_csv(planetary_csv)
            st.dataframe(df_planets, height=500, hide_index=True)
        else:
            st.warning("Planetary info not found.")

        # --- Dasha Tables in 3x3 Grid ---
        st.markdown("## వింశోత్తరి దశా పట్టికలు (Vimshottari Dasha Tables)")

        def extract_start_date(csv_path):
            try:
                df = pd.read_csv(csv_path)
                if not df.empty:
                    # Assuming the date format is DD-MM-YYYY (Indian format)
                    return dt.strptime(df.iloc[0]["ప్రారమ్భం"], "%d-%m-%Y")
            except Exception as e:
                print(f"⚠️ Error parsing {csv_path}: {e}")
            return dt.max  # fallback so faulty tables go to the end

        dasha_files = [
            f for f in os.listdir(charts_folder)
            if f.startswith("dasha_") and f.endswith(f"{name_safe}.csv")
        ]

        # Sort by first row's start date
        dasha_files.sort(key=lambda x: extract_start_date(os.path.join(charts_folder, x)))


        rows = [dasha_files[i:i+3] for i in range(0, len(dasha_files), 3)]
        for row in rows:
            cols = st.columns(3)
            for col, file in zip(cols, row):
                df = pd.read_csv(os.path.join(charts_folder, file))
                maha_name = file.split("_")[1]
                col.markdown(f"**{maha_name} మహాదశ**")
                col.dataframe(df, use_container_width=True, hide_index=True)


    with tabs[1]:
        st.markdown("## 🪐 All Divisional Charts")
        import re

        def extract_chart_number(filename):
            match = re.match(r"D(\d+)", filename)
            return int(match.group(1)) if match else 0

        chart_files = sorted(
            [f for f in os.listdir(charts_folder) if f.endswith(".svg") and f.startswith("D")],
            key=extract_chart_number
        )


        for i in range(0, len(chart_files), 2):
            cols = st.columns(2)
            for j in range(2):
                if i + j < len(chart_files):
                    with open(f"{charts_folder}/{chart_files[i + j]}", "rb") as f:
                        b64 = base64.b64encode(f.read()).decode()
                    with cols[j]:
                        parts = chart_files[i + j].replace(".svg", "").split("_")
                        label = " ".join(parts[:-1])  # Removes client name like "Vamsi"
                        st.markdown(f"### {label}")
                        html(f'<embed type="image/svg+xml" src="data:image/svg+xml;base64,{b64}" width="100%" height="500">', height=550)

    with tabs[2]:
        rekha_csv = f"{charts_folder}/rekha_table_{name_safe}.csv"
        if os.path.exists(rekha_csv):
            st.markdown("## 🧮 Binna Ashtakavarga Rekha Table")
            df_rekha = pd.read_csv(rekha_csv)
            st.dataframe(df_rekha, use_container_width=True)

        sarva_chart = f"{charts_folder}/Sarva_Ashtakavarga_{name_safe}.svg"
        if os.path.exists(sarva_chart):
            with open(sarva_chart, "rb") as f:
                b64 = base64.b64encode(f.read()).decode()
            st.markdown("### Sarva Ashtakavarga Chart")
            html(f'<embed type="image/svg+xml" src="data:image/svg+xml;base64,{b64}" width="100%" height="500">', height=550)
        st.markdown("## 🧭 Progression Chart & Table")

        prog_chart_file = f"{charts_folder}/Progression_{name_safe}.svg"
        if os.path.exists(prog_chart_file):
            with open(prog_chart_file, "rb") as f:
                b64 = base64.b64encode(f.read()).decode()
            html(f'<embed type="image/svg+xml" src="data:image/svg+xml;base64,{b64}" width="100%" height="500">', height=550)

        prog_table = f"{charts_folder}/progression_table_{name_safe}.csv"
        if os.path.exists(prog_table):
            df_prog = pd.read_csv(prog_table)
            st.dataframe(df_prog, use_container_width=True)



    with tabs[3]:
        charts_folder = "charts"
        os.makedirs(charts_folder, exist_ok=True)
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
        panchang_df.to_csv(f"{charts_folder}/panchang_details_{name}.csv", index=False)

        

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
                        mychart.add_planet(planet, planet_symbols[planet], house_num, colour="black")

            house_colors = ["white"] * 12  # All houses white

            mychart.updatechartcfg(
                aspect=False,              
                clr_background="white",    
                clr_outbox="black",       
                clr_line="black",         
                clr_Asc="darkblue",        
                clr_houses=house_colors    
            )

            filename_base = f"{varga_label.replace(' ', '_').replace('(', '').replace(')', '')}_{name.replace(' ', '_')}"
            chart_path = draw_and_fix_svg_chart(mychart, charts_folder, filename_base)

            if chart_path:
                display_svg_chart(chart_path)



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
        
                # --- Rekha Table and Sarva Ashtakavarga Chart ---
                planet_labels_table = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]
                sign_labels_row = [sign_labels[i + 1] for i in range(12)]  # 1-based

                rekha_df = ashtakavarga_rekha_table(ashta, planet_labels_table, sign_labels_row)
                rekha_df.to_csv(f"{charts_folder}/rekha_table_{name}.csv", index=False)
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
                    prog_chart.add_planet(planet, planet_symbols[planet], house_num, colour="black")

        house_colors = ["white"] * 12  # All houses white

        prog_chart.updatechartcfg(
            aspect=False,              
            clr_background="white",    
            clr_outbox="black",    
            clr_line="black",         
            clr_Asc="darkblue",        
            clr_houses=house_colors    
        )
        filename_base = f"Progression_{name.replace(' ', '_')}"
        prog_chart_filename = draw_and_fix_svg_chart(prog_chart, charts_folder, filename_base)

        if prog_chart_filename:
            display_svg_chart(prog_chart_filename)


        # Check if the file exists
        if os.path.exists(prog_chart_filename):
            with open(prog_chart_filename, "r", encoding="utf-16") as f:
                svg_text = f.read()

            svg_text = svg_text.replace('stroke:red', 'stroke:white')  # or 'stroke:black' or 'none'

            b64 = base64.b64encode(svg_text.encode("utf-16")).decode()
            st.markdown("### Progression Chart (South Indian Style)")
            st.components.v1.html(
                f'<embed type="image/svg+xml" src="data:image/svg+xml;base64,{b64}" width="500" height="500">',
                height=550
            )
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
        progression_df = pd.DataFrame(progression_df)  # ✅ Convert list to DataFrame
        st.dataframe(progression_df, use_container_width=True)
        progression_df.to_csv(f"{charts_folder}/progression_table_{name.replace(' ', '_')}.csv", index=False)



        st.markdown("## గ్రహ స్థితి పట్టిక")
        planetary_info = compute_planetary_info_telugu(date.year, date.month, date.day, hour, minute, second, lat, lon, tz)


        # Convert to DataFrame before displaying
        planetary_info_df = pd.DataFrame([
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

        # Display in app
        st.dataframe(planetary_info_df, use_container_width=True)

        # Save to file
        planetary_info_df.to_csv(f"{charts_folder}/planetary_info_telugu_{name.replace(' ', '_')}.csv", index=False)


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
                    "ప్రారమ్భం": jd_to_date(antar["start_jd"]).strftime("%d-%m-%Y"),
                    "ముగింపు": jd_to_date(antar["end_jd"]).strftime("%d-%m-%Y")
                })
            
            # Convert to DataFrame
            antar_df = pd.DataFrame(antar_table).astype(str)

            # Display using st.dataframe for better formatting
            st.dataframe(antar_df, use_container_width=True)

            # Save to CSV
            maha_filename = f"{charts_folder}/dasha_{maha['lord']}_{name.replace(' ', '_')}.csv"
            antar_df.to_csv(maha_filename, index=False)

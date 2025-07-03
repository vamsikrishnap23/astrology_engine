#----------------- IMPORTS ---------------------------------
import streamlit as st
import datetime
import base64
import os
from streamlit.components.v1 import html
import swisseph as swe
import importlib
import pandas as pd
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


#------------------------------ DICTIONARIES -------------------------







#---------------- PAGE CONFIG -------------------------------

st.set_page_config(page_title="Jyotish Engine", layout="wide")
st.title("Jyotish Engine")

MAX_RETRIES = 10
WAIT_SECONDS = 0.5


#----------------------- INPUT FORM -----------------------------------------

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






tabs = st.tabs(["View 1","Div Charts", "Ashtakavarga", "All"])



#----------------------------- HELPER FUNCTIONS --------------------------------------

def wait_for_files(file_list, timeout=5, poll_interval=0.5):
    start_time = time.time()
    while True:
        if all(os.path.exists(f) for f in file_list):
            return True
        if time.time() - start_time > timeout:
            return False
        time.sleep(poll_interval)

def draw_and_fix_svg_chart(chart_obj, charts_folder, filename_base):
    chart_obj.draw(charts_folder, filename_base, "svg")
    svg_path = os.path.join(charts_folder, f"{filename_base}.svg")
    if os.path.exists(svg_path):
        with open(svg_path, "r", encoding="utf-16") as f:
            svg_text = f.read()
        svg_text = svg_text.replace("stroke:red", "stroke:white")
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
    # sarva = ["Sarva"] + [sum(ashta.getItem(REKHA, pidx, rasi) for pidx in range(7)) for rasi in range(12)]
    # df.loc[len(df)] = sarva
    return df


#-------------------- RENDERING---------------------------
if submitted:
    charts_folder = "charts"
    name_safe = name.replace(" ", "_")
    os.makedirs(charts_folder, exist_ok=True)

    # --- TAB 1: Wait for files and display ---
    with tabs[0]:
        # ----------------- Panchangam -----------------------------
        panchang_path = f"{charts_folder}/panchang_details_{name_safe}.csv"
        if os.path.exists(panchang_path):
            st.markdown("## 🗓️ పంచాంగం")
            df_panchang = pd.read_csv(panchang_path)
            st.dataframe(df_panchang, use_container_width=True, hide_index=True)
        else:
            st.warning("Panchangam info not found.")

        # ------------------ D1 & D9 Charts ------------------------
        st.markdown("## D1 & D9 Charts")
        d_charts = [
            ("D1_Rāśi", "D1 (రాశి)"),
            ("D9_Navamsa", "D9 (నవాంశ)")
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


        # ---------------------- Planetary Info Table ------------------------
        planetary_csv = f"{charts_folder}/planetary_info_telugu_{name_safe}.csv"
        if os.path.exists(planetary_csv):
            st.markdown("## గ్రహ స్థితి")
            df_planets = pd.read_csv(planetary_csv)
            st.dataframe(df_planets, height=500, hide_index=True)
        else:
            st.warning("Planetary info not found.")

        # -------------------- Dasha Tables in 3x3 Grid -------------------------
        st.markdown("## వింశోత్తరి దశ")
        def extract_start_date(csv_path):
            try:
                df = pd.read_csv(csv_path)
                if not df.empty:
                    return dt.strptime(df.iloc[0]["ప్రారంభం"], "%d-%m-%Y")
            except Exception as e:
                print(f"Error parsing {csv_path}: {e}")
            return dt.max  

        dasha_files = [
            f for f in os.listdir(charts_folder)
            if f.startswith("dasha_") and f.endswith(f"{name_safe}.csv")
        ]

        dasha_files.sort(key=lambda x: extract_start_date(os.path.join(charts_folder, x)))


        rows = [dasha_files[i:i+3] for i in range(0, len(dasha_files), 3)]
        for row in rows:
            cols = st.columns(3)
            for col, file in zip(cols, row):
                df = pd.read_csv(os.path.join(charts_folder, file))
                maha_name = file.split("_")[1]
                col.markdown(f"**{maha_name} మహాదశ**")
                col.dataframe(df, use_container_width=True, hide_index=True)


        #------------------- TABS 1 -------------------------------------

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
                            label = " ".join(parts[:-1])
                            st.markdown(f"### {label}")
                            html(f'<embed type="image/svg+xml" src="data:image/svg+xml;base64,{b64}" width="100%" height="500">', height=550)



        # -------------------------- TAB 2 ----------------------------------

        with tabs[2]:
            # --- Rekha Table ---
            rekha_csv = f"{charts_folder}/rekha_table_{name_safe}_telugu.csv"
            if os.path.exists(rekha_csv):
                st.markdown("## Binna Ashtakavarga Rekha Table")
                df_rekha = pd.read_csv(rekha_csv)
                st.dataframe(df_rekha, use_container_width=True, hide_index=True)

            # --- Sarva Chart ---
            sarva_svg = f"{charts_folder}/Sarva_{name_safe}.svg"
            if os.path.exists(sarva_svg):
                st.markdown("## Sarva Ashtakavarga Chart")
                with open(sarva_svg, "r", encoding="utf-8") as f:
                    svg_text = f.read()
                b64 = base64.b64encode(svg_text.encode("utf-8")).decode()
                st.components.v1.html(
                    f'''
                    <div style="text-align:center;">
                        <embed type="image/svg+xml" src="data:image/svg+xml;base64,{b64}" width="980" height="700" />
                    </div>
                    ''',
                    height=720
                )
            else:
                st.warning("Sarva chart not found.")



        # --------------------------------- TAB 3 -----------------------------------------

        with tabs[3]:
            # Panchangam Labels and Translations (Inline Only)
            TELUGU_NAKSHATRAS = [
                "అశ్విని", "భరణి", "కృత్తిక", "రోహిణి", "మృగశిర", "ఆర్ద్ర", "పునర్వసు",
                "పుష్యమి", "ఆశ్లేష", "మఖ", "పుబ్బ", "ఉత్తర", "హస్త", "చిత్త", "స్వాతి", "విశాఖ",
                "అనూరాధ", "జ్యేష్ఠ", "మూల", "పూర్వాషాఢ", "ఉత్తరాషాఢ", "శ్రవణం", "ధనిష్ట",
                "శతభిష", "పూర్వాభాద్ర", "ఉత్తరాభాద్ర", "రేవతి"
            ]

            TELUGU_RASIS = {
                "Mesha": "మేషం", "Vrishabha": "వృషభం", "Mithuna": "మిథునం", "Karka": "కర్కాటకం",
                "Simha": "సింహం", "Kanya": "కన్యా", "Tula": "తుల", "Vrischika": "వృశ్చికం",
                "Dhanu": "ధనుస్సు", "Makara": "మకరం", "Kumbha": "కుంభం", "Meena": "మీనం"
            }

            TELUGU_VAARAM = {
                "Sunday": "ఆదివారం", "Monday": "సోమవారం", "Tuesday": "మంగళవారం",
                "Wednesday": "బుధవారం", "Thursday": "గురువారం", "Friday": "శుక్రవారం", "Saturday": "శనివారం"
            }

            # ---------- Panchangam Rendering Block ----------
            st.markdown("## 🗓️ పంచాంగం")
            jd = get_julian_day(date.year, date.month, date.day, hour, minute, second, tz)


            panchang = get_panchang_minimal(jd, lat, lon, tz)

            # Telugu Translations
            nakshatra_eng = panchang["Nakshatram"]
            nakshatra_idx = next((i for i, val in enumerate([
                "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra", "Punarvasu",
                "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni", "Hasta",
                "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha",
                "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha", "Purva Bhadrapada",
                "Uttara Bhadrapada", "Revati"
            ]) if val == nakshatra_eng), -1)


            nakshatra_te = TELUGU_NAKSHATRAS[nakshatra_idx] if nakshatra_idx != -1 else nakshatra_eng
            padam_te = f"{panchang['Padam']}వ పదం"  # e.g., "3వ పదం"
            rasi_te = TELUGU_RASIS.get(panchang["Rasi"], panchang["Rasi"])
            vaaram_te = TELUGU_VAARAM.get(panchang["Vaaram"], panchang["Vaaram"])

            # Build DataFrame
            panchang_df = pd.DataFrame([
                {"గుణము": "నక్షత్రం", "విలువ": nakshatra_te},
                {"గుణము": "పదం", "విలువ": padam_te},
                {"గుణము": "రాశి", "విలువ": rasi_te},
                {"గుణము": "వారం", "విలువ": vaaram_te}
            ])

            st.table(panchang_df)
            panchang_df.to_csv(f"{charts_folder}/panchang_details_{name_safe}.csv", index=False)

            # ---------------------------------- DIV CHARTS -------------------------------------

            varga_list = [
                (1, "D1 (Rāśi)"), (2, "D2 (Hora)"), (3, "D3 (Drekkana)"), (4, "D4 (Chaturthamsha)"),
                (7, "D7 (Saptamsha)"), (9, "D9 (Navamsa)"), (10, "D10 (Dashamsha)"), (12, "D12 (Dwadashamsha)"),
                (16, "D16 (Shodashamsha)"), (20, "D20 (Vimshamsha)"), (24, "D24 (Chaturvimshamsha)"), (27, "D27 (Bhamsha)"), (30, "D30 (Trimsamsha)"),
                (40, "D40 (Khavedamsha)"), (45, "D45 (Akshavedamsha)"), (60, "D60 (Shastiamsa)")
            ]

            sign_labels = get_sign_labels(language="English")
            rev_sign_labels = {v: k for k, v in sign_labels.items()}

            all_planetary_info = {}

            for varga_num, varga_label in varga_list:
                st.markdown(f"## {varga_label} Chart")
                planets_in_sign = compute_planets_in_varga(
                    date.year, date.month, date.day, hour, minute, second, lat, lon, tz, varga_num
                )

                # Ascendant logic as before...
                asc_sign_num = next((sign for sign, pl in planets_in_sign.items() if "Ascendant" in pl), None)
                if not asc_sign_num:
                    st.warning(f"Ascendant not found for {varga_label}. Skipping chart rendering.")
                    continue

                # --- Calculate planetary info for THIS divisional chart ---
                planetary_info = compute_planetary_info_telugu(
                    date.year, date.month, date.day, hour, minute, second, lat, lon, tz, varga_num
                )
                retrograde_lookup = {
                    p["planet"]: (p["retrogration"] in ["వక్రం", "Yes", "R", "vakram", "Retrograde"])
                    for p in planetary_info
                }
                all_planetary_info[varga_num] = retrograde_lookup

                import jyotichart
                importlib.reload(jyotichart)
                import jyotichart as chart

                mychart = chart.SouthChart(varga_label + " Chart", name, IsFullChart=True)

                asc_index = ((asc_sign_num - 1) % 12) + 1
                asc_sign = sign_labels.get(asc_index)
                result = mychart.set_ascendantsign(asc_sign)
                if result != "Success":
                    st.error(f"Failed to set ascendant sign '{asc_sign}' for {varga_label}: {result}")
                    continue

                planet_symbols = {
                    "Sun": "సూ",       # Sūryuḍu
                    "Moon": "చం",      # Chandra
                    "Mars": "కు",     # Kujudu
                    "Mercury": "బు",    # Budhudu
                    "Jupiter": "గు",    # Guru
                    "Venus": "శు",      # Shukrudu
                    "Saturn": "శ",      # Shani
                    "Rahu": "రా",       # Rahu
                    "Ketu": "కే",       # Ketu
                    "Ascendant": "ల"     # Lagna
                }

                asc_sign_num_for_calc = rev_sign_labels[asc_sign]
                for sign_num in range(1, 13):
                    for planet in planets_in_sign.get(sign_num, []):
                        if planet == "Ascendant":
                            symbol = planet_symbols["Ascendant"]  # "ల"
                            continue
                        if planet in planet_symbols:
                            house_num = (sign_num - asc_sign_num_for_calc) % 12 + 1
                            symbol = planet_symbols[planet]
                            is_retro = all_planetary_info[varga_num].get(planet, False)
                            mychart.add_planet(
                                planet,
                                symbol,
                                house_num,
                                retrograde=is_retro,
                                colour="black"
                            )

                house_colors = ["white"] * 12
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
                    st.markdown("### అష్టకవర్గ (Rekha, Sarva) - D1 (రాశి) చార్ట్")

                    get_rasi = get_rasi_for_ashtakavarga(planets_in_sign)
                    ashta = Ashtakavarga(get_rasi)
                    ashta.update()

                    # Build planet placement
                    planet_labels = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Ascendant"]
                    ashta_planets_in_sign = {i: [] for i in range(1, 13)}
                    for idx, planet in enumerate(planet_labels):
                        sign_num = get_rasi(idx) + 1
                        ashta_planets_in_sign[sign_num].append(planet)
                    for sign_num, planets in planets_in_sign.items():
                        for planet in planets:
                            if planet in ("Rahu", "Ketu"):
                                ashta_planets_in_sign[sign_num].append(planet)

                    # English Sign Labels (for original Rekha table)
                    sign_labels_row = [
                        "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
                        "Libra", "Scorpio", "Saggitarius", "Capricorn", "Aquarius", "Pisces"
                    ]

                    # Compute Rekha table
                    planet_labels_table = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]
                    rekha_df = ashtakavarga_rekha_table(ashta, planet_labels_table, sign_labels_row)

                    # Telugu Dictionaries
                    telugu_planets = {
                        "Sun": "సూర్యుడు", "Moon": "చంద్రుడు", "Mercury": "బుధుడు",
                        "Venus": "శుక్రుడు", "Mars": "కుజుడు", "Jupiter": "గురు", "Saturn": "శని"
                    }

                    telugu_signs = {
                        "Aries": "మేషం", "Taurus": "వృషభం", "Gemini": "మిథునం", "Cancer": "కర్కాటకం",
                        "Leo": "సింహం", "Virgo": "కన్యా", "Libra": "తులా", "Scorpio": "వృశ్చికం",
                        "Saggitarius": "ధనుస్సు", "Capricorn": "మకరం", "Aquarius": "కుంభం", "Pisces": "మీనం"
                    }

                    # Translate Columns: Signs (from second column onwards)
                    new_columns = ["గ్రహం"] + [telugu_signs.get(col, col) for col in rekha_df.columns[1:]]
                    rekha_df.columns = new_columns

                    # Translate Planet Names (first column)
                    rekha_df.iloc[:, 0] = rekha_df.iloc[:, 0].apply(lambda x: telugu_planets.get(x, x))

                    # Add Sarva row
                    sarva = [sum(ashta.getItem(REKHA, pidx, rasi) for pidx in range(7)) for rasi in range(12)]
                    sarva_row = ["సర్వ"] + sarva
                    rekha_df.loc[len(rekha_df.index)] = sarva_row

                    # Save to file
                    rekha_path = f"{charts_folder}/rekha_table_{name_safe}_telugu.csv"
                    rekha_df.to_csv(rekha_path, index=False, encoding="utf-8-sig")

                    # Display
                    st.markdown("#### 🗒️ బిన్న అష్టకవర్గ పట్టిక (Rekha Table)")
                    st.dataframe(rekha_df, use_container_width=True, hide_index=True)


                    # Sarva Ashtakavarga values (as list of 12 ints)
                    sarva = [sum(ashta.getItem(REKHA, pidx, rasi) for pidx in range(7)) for rasi in range(12)]

                    from sarva_chart_generator import draw_south_chart_with_sarva, SIGN_NAMES
                    sarva_dict = dict(zip(SIGN_NAMES, sarva))

                    name_safe = name.replace(" ", "_")  # ✅ Ensure it's defined
                    sarva_svg_path = draw_south_chart_with_sarva(sarva_dict, filename=f"Sarva_{name_safe}")

                    st.markdown("#### Sarva Ashtakavarga Chart")
                    with open(sarva_svg_path, "r", encoding="utf-8") as f:
                        svg_text = f.read()
                    b64 = base64.b64encode(svg_text.encode("utf-8")).decode()
                    st.components.v1.html(
                        f'<embed type="image/svg+xml" src="data:image/svg+xml;base64,{b64}" width="980" height="700">',
                        height=700
                    )



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
            st.dataframe(planetary_info_df, use_container_width=True, hide_index=True)

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
                st.dataframe(antar_df, use_container_width=True, hide_index=True)

                # Save to CSV
                maha_filename = f"{charts_folder}/dasha_{maha['lord']}_{name.replace(' ', '_')}.csv"
                antar_df.to_csv(maha_filename, index=False)
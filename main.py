import streamlit as st
import datetime
import base64
import os
from streamlit.components.v1 import html

from astro_core.chart_logic import (
    compute_planets_in_sign,
    compute_planets_in_d9,
    get_sign_labels
)
from astro_core.planetary_info import compute_planetary_info_telugu
from astro_core.constants import TELUGU_PLANETS
import jyotichart as chart

# Only import dasha logic when needed to avoid circular import
def get_vimsottari_dasha_dict(*args, **kwargs):
    from astro_core.vimshottari_dashas import compute_vimshottari_dasha_dict
    return compute_vimshottari_dasha_dict(*args, **kwargs)

st.set_page_config(page_title="Jyotish Engine", layout="centered")
st.title("Jyotish Engine")

with st.form("input_form"):
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Name", "Test User")
        date = st.date_input("Date of Birth", value=datetime.date(2005, 11, 23),
                             min_value=datetime.date(1900, 1, 1), max_value=datetime.date.today())
        hour = st.number_input("Hour (24h)", 0, 23, 12, value=15)
        minute = st.number_input("Minute", 0, 59, 0, value=35)
        second = st.number_input("Second", 0, 59, 0)

    with col2:
        lat = st.number_input("Latitude", -90.0, 90.0, 17.385)
        lon = st.number_input("Longitude", -180.0, 180.0, 78.4867)
        tz = st.number_input("Timezone Offset (e.g. 5.5)", -12.0, 14.0, 5.5)
        language = st.selectbox("Language", ["English", "Telugu"])

    submitted = st.form_submit_button("Generate All Charts")

if submitted:
    charts = {
        "D1 (Rāśi) Chart": compute_planets_in_sign(
            date.year, date.month, date.day, hour, minute, second, lat, lon, tz
        ),
        "D9 (Navamsa) Chart": compute_planets_in_d9(
            date.year, date.month, date.day, hour, minute, second, lat, lon, tz
        )
    }

    sign_labels = get_sign_labels(language="English")
    rev_sign_labels = {v: k for k, v in sign_labels.items()}

    for chart_title, planets_in_sign in charts.items():
        st.markdown(f"## {chart_title}")

        if "D9" in chart_title:
            import importlib
            import jyotichart
            importlib.reload(jyotichart)
            import jyotichart as chart  # reimport for current context

        asc_sign = next((sign_labels[sign] for sign, pl in planets_in_sign.items() if "Ascendant" in pl), None)
        if not asc_sign:
            st.error("Ascendant not found in chart data.")
            continue

        mychart = chart.SouthChart(chart_title, name, IsFullChart=True)
        mychart.set_ascendantsign(asc_sign)

        planet_symbols = {
            "Sun": "Su", "Moon": "Mo", "Mars": "Ma", "Mercury": "Me",
            "Jupiter": "Ju", "Venus": "Ve", "Saturn": "Sa",
            "Rahu": "Ra", "Ketu": "Ke", "Ascendant": "As"
        }

        asc_sign_num = rev_sign_labels[asc_sign]
        for sign_num in range(1, 13):
            for planet in planets_in_sign.get(sign_num, []):
                if planet == "Ascendant":
                    continue
                if planet in planet_symbols:
                    house_num = (sign_num - asc_sign_num) % 12 + 1
                    mychart.add_planet(planet, planet_symbols[planet], house_num)

        mychart.updatechartcfg(aspect=False)

        timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')
        basename = f"{chart_title.lower().replace(' ', '_')}_{timestamp}"
        mychart.draw(".", basename, "svg")
        svg_filename = f"{basename}.svg"

        with open(svg_filename, "rb") as f:
            svg_bytes = f.read()
            try:
                svg_data = svg_bytes.decode("utf-8")
            except UnicodeDecodeError:
                try:
                    svg_data = svg_bytes.decode("utf-16")
                except UnicodeDecodeError:
                    svg_data = svg_bytes.decode("latin-1")
            b64 = base64.b64encode(svg_data.encode('utf-8')).decode()
            html(f'<embed type="image/svg+xml" src="data:image/svg+xml;base64,{b64}" width="500" height="500">', height=550)

        try:
            os.remove(svg_filename)
        except Exception:
            pass

    # Telugu Planetary Info Table
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


    # Vimshottari Dasha Table (Maitreya/Parashara logic)
    from astro_core.vimshottari_dashas import compute_vimshottari_dasha_tree, jd_to_date

    st.markdown("## వింశోత్తరి దశా పట్టిక (Vimshottari Dasha Table)")

    dasha_data = compute_vimshottari_dasha_tree(
        date.year, date.month, date.day,
        hour, minute, second,
        lat, lon, tz
    )

    for maha in dasha_data:
        md_lord = maha["lord"]
        st.markdown(f"### మహాదశ: {md_lord}")
        antar_table = []

        for antar in maha["antardashas"]:
            antar_table.append({
                "అంతర్దశ": antar["antardasha_lord"],
                "ప్రారంభం": jd_to_date(antar["true_start_jd"]).strftime("%Y-%m-%d"),
                "ముగింపు": jd_to_date(antar["end_jd"]).strftime("%Y-%m-%d")
            })

        st.table(antar_table)

import streamlit as st
from astro_core import (
    compute_planets_in_sign,
    compute_planets_in_d9,
    get_sign_labels,
    compute_planetary_info_telugu,
    TELUGU_PLANETS  
)
import datetime
import jyotichart as chart
from streamlit.components.v1 import html
import base64
import os

st.set_page_config(page_title="Jyotish Chart Generator", layout="centered")
st.title("🪐 Jyotish Chart Generator")

with st.form("input_form"):
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Name", "Test User")
        date = st.date_input("Date of Birth", value=datetime.date(1990, 1, 1),
                             min_value=datetime.date(1900, 1, 1), max_value=datetime.date.today())
        hour = st.number_input("Hour (24h)", 0, 23, 12)
        minute = st.number_input("Minute", 0, 59, 0)
        second = st.number_input("Second", 0, 59, 0)
        chart_type = st.selectbox("Chart Type", ["D1 (Rāśi)", "D9 (Navamsa)"])

    with col2:
        lat = st.number_input("Latitude", -90.0, 90.0, 17.385)
        lon = st.number_input("Longitude", -180.0, 180.0, 78.4867)
        tz = st.number_input("Timezone Offset (e.g. 5.5)", -12.0, 14.0, 5.5)
        language = st.selectbox("Language", ["English", "Telugu"])

    submitted = st.form_submit_button("Generate Chart")

if submitted:
    if chart_type == "D1 (Rāśi)":
        planets_in_sign = compute_planets_in_sign(
            date.year, date.month, date.day,
            hour, minute, second,
            lat, lon, tz
        )
        chart_title = "D1 Chart"
        file_prefix = "d1_chart"
    else:
        planets_in_sign = compute_planets_in_d9(
            date.year, date.month, date.day,
            hour, minute, second,
            lat, lon, tz
        )
        chart_title = "D9 (Navamsa) Chart"
        file_prefix = "d9_chart"

    sign_labels = get_sign_labels(language="English")  # Chart needs English internally
    rev_sign_labels = {v: k for k, v in sign_labels.items()}

    # Get Ascendant sign name
    asc_sign = None
    for sign_num, planets in planets_in_sign.items():
        if "Ascendant" in planets:
            asc_sign = sign_labels[sign_num]
            break

    mychart = chart.SouthChart(chart_title, name, IsFullChart=True)
    mychart.set_ascendantsign(asc_sign)

    planet_symbols = {
        "Sun": "Su", "Moon": "Mo", "Mars": "Ma", "Mercury": "Me",
        "Jupiter": "Ju", "Venus": "Ve", "Saturn": "Sa",
        "Rahu": "Ra", "Ketu": "Ke", "Ascendant": "As"
    }

    # Correct mapping: sign -> relative house number
    asc_sign_num = rev_sign_labels[asc_sign]
    for sign_num in range(1, 13):
        for planet in planets_in_sign.get(sign_num, []):
            if planet == "Ascendant":
                continue
            if planet in planet_symbols:
                house_num = (sign_num - asc_sign_num) % 12 + 1
                mychart.add_planet(planet, planet_symbols[planet], house_num)

    mychart.updatechartcfg(aspect=False)

    svg_filename = f"{file_prefix}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.svg"
    mychart.draw(".", svg_filename.replace(".svg", ""), "svg")

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

    st.markdown("### Sign Labels")
    user_sign_labels = get_sign_labels(language)
    for i in range(1, 13):
        st.write(f"{i}: {user_sign_labels[i]}")

    st.markdown("### గ్రహ స్థితి పట్టిక")
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
    }
    for p in planetary_info
])
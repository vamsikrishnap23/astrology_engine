import streamlit as st
import pandas as pd
import base64
import os

# Constants from southindianchart.py
SIGN_NAMES = [
    "Aries", "Taurus", "Gemini", "Cancer",
    "Leo", "Virgo", "Libra", "Scorpio",
    "Saggitarius", "Capricorn", "Aquarius", "Pisces"
]
SIGN_SHORT = ["Ar", "Ta", "Ge", "Cn", "Le", "Vi", "Li", "Sc", "Sg", "Cp", "Aq", "Pi"]

SIGN_TO_OFFSET = {
    "aries": (0, 0), "taurus": (120, 0), "gemini": (240, 0), "cancer": (240, 80),
    "leo": (240, 160), "virgo": (240, 240), "libra": (120, 240), "scorpio": (0, 240),
    "saggitarius": (-120, 240), "capricorn": (-120, 160), "aquarius": (-120, 80), "pisces": (-120, 0)
}

BASE_COORD_9TH = (180, 30)  # From base_coordinates[8] in southindianchart.py

def get_sarva_coord(sign_name):
    ox, oy = SIGN_TO_OFFSET[sign_name.lower()]
    return ox + BASE_COORD_9TH[0], oy + BASE_COORD_9TH[1]

def draw_south_chart_with_sarva(sarva_dict, filename="SarvaSouthChart"):
    svg = []
    svg.append(f'''<svg width="490" height="330" viewBox="0 0 490 340" xmlns="http://www.w3.org/2000/svg">''')
    svg.append('''
        <style>
            .sign-num { font: bold 14px sans-serif; fill: gray; }
            .sarva-val { font: bold 18px sans-serif; fill: black; }
        </style>

    ''')

    # Draw 12 sign rectangles at fixed positions (mimicking draw_classicSouthChartSkeleton)
    box_coords = {
        "aries": (123, 10), "taurus": (243, 10), "gemini": (363, 10), "cancer": (363, 90),
        "leo": (363, 170), "virgo": (363, 250), "libra": (243, 250), "scorpio": (123, 250),
        "saggitarius": (3, 250), "capricorn": (3, 170), "aquarius": (3, 90), "pisces": (3, 10)
    }

    for idx, sign in enumerate(SIGN_NAMES):
        lower = sign.lower()
        x, y = box_coords[lower]
        svg.append(f'<rect x="{x}" y="{y}" width="120" height="80" fill="white" stroke="black" stroke-width="2"/>')
        svg.append(f'<text x="{x+5}" y="{y+15}" class="sign-num">{SIGN_SHORT[idx]}</text>')

    # Draw center rectangle (same as original skeleton)
    

    # Draw Sarva values
    for sign in SIGN_NAMES:
        val = sarva_dict.get(sign, "")
        x, y = get_sarva_coord(sign)
        # x += 123  # adjust for chart start x
        y += 15   # adjust for chart start y
        svg.append(f'<text x="{x}" y="{y}" class="sarva-val" text-anchor="middle">{val}</text>')

    svg.append('</svg>')

    charts_folder = "charts"
    os.makedirs(charts_folder, exist_ok=True)
    path = os.path.join(charts_folder, f"{filename}.svg")
    with open(path, "w", encoding="utf-8") as f:
        f.write('\n'.join(svg))
    return path


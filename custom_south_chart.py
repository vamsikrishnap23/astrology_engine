import os
import jyotichart
import importlib

# Reload to ensure latest
importlib.reload(jyotichart)

# Map numbers to sign names as per your general.py
SIGN_NAMES = [
    "Aries", "Taurus", "Gemini", "Cancer",
    "Leo", "Virgo", "Libra", "Scorpio",
    "Saggitarius", "Capricorn", "Aquarius", "Pisces"
]

PLANET_NAMES = [
    "Sun", "Moon", "Mars", "Mercury", "Jupiter",
    "Venus", "Saturn", "Rahu", "Ketu"
]
PLANET_SYMBOLS = {
    "Sun": "Su", "Moon": "Mo", "Mars": "Ma", "Mercury": "Me",
    "Jupiter": "Ju", "Venus": "Ve", "Saturn": "Sa",
    "Rahu": "Ra", "Ketu": "Ke"
}

def get_input_numbers():
    print("Enter ascendant sign number (1=Aries, ..., 12=Pisces):")
    asc_num = int(input().strip())
    asc_sign = SIGN_NAMES[asc_num - 1]

    print("Enter house numbers (1-12) for each planet:")
    planet_positions = {}
    for pname in PLANET_NAMES:
        h = int(input(f"{pname}: ").strip())
        if not (1 <= h <= 12):
            raise ValueError(f"Invalid house for {pname}")
        planet_positions[pname] = h

    print("Enter 12 Sarva Ashtakavarga values (space-separated, in zodiac order from Aries):")
    sarva_values = list(map(int, input().strip().split()))
    if len(sarva_values) != 12:
        raise ValueError("You must enter 12 Sarva values.")
    return asc_sign, planet_positions, sarva_values

def draw_south_chart_with_sarva(asc_sign, planet_positions, sarva_values, filename="SouthChartWithSarva"):
    chart = jyotichart.SouthChart("Custom South Chart", "User", IsFullChart=True)
    result = chart.set_ascendantsign(asc_sign)
    if result != "Success":
        raise ValueError(f"Invalid ascendant sign: {asc_sign}")

    # Add planets by house number
    for pname in PLANET_NAMES:
        h = planet_positions[pname]
        chart.add_planet(pname, PLANET_SYMBOLS[pname], h)

    # Now, inject Sarva values as "planets" with special symbols in each house
    # We'll use "Sa1", "Sa2", ... as fake planet names for this purpose
    for i in range(1, 13):
        sarva_symbol = str(sarva_values[i-1])
        fake_planet = f"SARVA{i}"
        # Add as a planet to house i, with a unique symbol and color (e.g., blue)
        # This is a hack: jyotichart expects only the 9 planets, but for display you can add custom "planets"
        chart.planets[fake_planet] = {
            "symbol": sarva_symbol,
            "aspect_symbol": "",
            "retro": False,
            "house_num": i,
            "colour": "blue",
            "pos": {"x": 0, "y": 0},
            "aspectpos": [],
            "isUpdated": False
        }
        # Use the same coordinate logic as for planets
        sign = jyotichart.gen.get_signofsign(i, asc_sign)
        # There may be up to 8 planets per house, so use index 9 for Sarva (see southindianchart.py)
        pos = jyotichart.sc.get_coordniates(sign, 9)
        chart.planets[fake_planet]["pos"]["x"] = pos[0]
        chart.planets[fake_planet]["pos"]["y"] = pos[1]
        chart.planets[fake_planet]["isUpdated"] = True

    # Chart config (colors etc)
    chart.updatechartcfg(
        aspect=False,
        clr_background="white",
        clr_outbox="black",
        clr_inbox="black",
        clr_line="black",
        clr_Asc="darkblue",
        clr_houses=["white"] * 12
    )

    charts_folder = "charts"
    os.makedirs(charts_folder, exist_ok=True)
    chart.draw(charts_folder, filename, "svg")
    print(f"Chart saved as {os.path.join(charts_folder, filename)}.svg")

if __name__ == "__main__":
    asc_sign, planet_positions, sarva_values = get_input_numbers()
    draw_south_chart_with_sarva(asc_sign, planet_positions, sarva_values)

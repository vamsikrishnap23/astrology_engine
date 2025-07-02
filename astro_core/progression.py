import swisseph as swe
from .calculations import get_julian_day, get_rasi

PLANET_ORDER = [
    "Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"
]
PLANET_SWISSEPH_IDS = [
    swe.SUN, swe.MOON, swe.MARS, swe.MERCURY, swe.JUPITER, swe.VENUS, swe.SATURN
]

def get_progressed_jd(birth_jd, age_years):
    """Progressed chart: 1 day after birth = 1 year of life."""
    return birth_jd + age_years

def compute_progressed_chart(
    birth_jd,
    age_years,
    lat,
    lon,
    tz_offset=0,
    ayanamsa_mode="lahiri",
    house_system="P"
):
    jd_prog = birth_jd + age_years

    if ayanamsa_mode.lower() == "lahiri":
        swe.set_sid_mode(swe.SIDM_LAHIRI)
    else:
        swe.set_sid_mode(swe.SIDM_FAGAN_BRADLEY)

    flag = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED

    planets = {}
    # Classical planets
    for idx, pid in enumerate(PLANET_SWISSEPH_IDS):
        lon_arr, _ = swe.calc_ut(jd_prog, pid, flag)
        longitude = lon_arr[0] % 360
        speed = lon_arr[3]
        retro = speed < 0
        planets[PLANET_ORDER[idx]] = {
            "longitude": longitude,
            "speed": speed,
            "retrograde": retro
        }
    # Rahu (Mean Node)
    rahu_arr, _ = swe.calc_ut(jd_prog, swe.MEAN_NODE, flag)
    rahu_long = rahu_arr[0] % 360
    rahu_speed = rahu_arr[3]
    planets["Rahu"] = {
        "longitude": rahu_long,
        "speed": rahu_speed,
        "retrograde": rahu_speed < 0
    }
    # Ketu (opposite Rahu, speed is -Rahu's speed, always retrograde)
    ketu_long = (rahu_long + 180) % 360
    ketu_speed = -rahu_speed
    planets["Ketu"] = {
        "longitude": ketu_long,
        "speed": ketu_speed,
        "retrograde": True
    }

    # Ascendant and houses
    cusps, ascmc = swe.houses_ex(jd_prog, lat, lon, house_system.encode('ascii'), flag)
    houses = [c % 360 for c in cusps[:12]]
    ascendant = ascmc[0] % 360

    return {
        "planets": planets,
        "ascendant": ascendant,
        "houses": houses
    }

def get_sign_number(degree):
    return int(degree // 30) + 1

def get_sign_labels(language="English"):
    return {
        1: "Aries", 2: "Taurus", 3: "Gemini", 4: "Cancer", 5: "Leo", 6: "Virgo",
        7: "Libra", 8: "Scorpio", 9: "Sagittarius", 10: "Capricorn", 11: "Aquarius", 12: "Pisces"
    }

def progression_chart_table(chart, sign_labels):
    import pandas as pd
    rows = []
    for planet in PLANET_ORDER + ["Rahu", "Ketu"]:
        p = chart["planets"].get(planet)
        if not p:
            continue
        sign_num = get_sign_number(p["longitude"])
        rows.append({
            "Planet": planet,
            "Longitude": f"{p['longitude']:.2f}°",
            "Sign": sign_labels[sign_num],
            "Sign Num": sign_num,
            "Speed": f"{p['speed']:.5f}",
            "Retrograde": "R" if p["retrograde"] else ""
        })
    asc_sign_num = get_sign_number(chart["ascendant"])
    rows.append({
        "Planet": "Ascendant",
        "Longitude": f"{chart['ascendant']:.2f}°",
        "Sign": sign_labels[asc_sign_num],
        "Sign Num": asc_sign_num,
        "Speed": "",
        "Retrograde": ""
    })
    return pd.DataFrame(rows)

# Example usage:
if __name__ == "__main__":
    import datetime
    birth_date = datetime.date(2005, 11, 23)
    birth_time = datetime.time(15, 35, 0)
    lat, lon, tz = 17.385, 78.4867, 5.5
    birth_jd = get_julian_day(
        birth_date.year, birth_date.month, birth_date.day,
        birth_time.hour, birth_time.minute, birth_time.second, tz
    )
    age_years = 35
    chart = compute_progressed_chart(birth_jd, age_years, lat, lon, tz_offset=tz)
    sign_labels = get_sign_labels()
    df = progression_chart_table(chart, sign_labels)
    print(df)

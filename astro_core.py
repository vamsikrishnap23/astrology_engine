# astro_core.py

import swisseph as swe
import datetime

PLANETS = {
    'Sun': swe.SUN,
    'Moon': swe.MOON,
    'Mars': swe.MARS,
    'Mercury': swe.MERCURY,
    'Jupiter': swe.JUPITER,
    'Venus': swe.VENUS,
    'Saturn': swe.SATURN,
    # Rahu/Ketu handled separately
}

SIGN_NAMES = {
    1: "Aries", 2: "Taurus", 3: "Gemini", 4: "Cancer",
    5: "Leo", 6: "Virgo", 7: "Libra", 8: "Scorpio",
    9: "Sagittarius", 10: "Capricorn", 11: "Aquarius", 12: "Pisces"
}

TELUGU_SIGNS = {
    1: "మేషం", 2: "వృషభం", 3: "మిథునం", 4: "కర్కాటకం",
    5: "సింహం", 6: "కన్యా", 7: "తులా", 8: "వృశ్చికం",
    9: "ధనుస్సు", 10: "మకరం", 11: "కుంభం", 12: "మీనం"
}

def get_julian_day(year, month, day, hour, minute, second, tz_offset):
    dt = datetime.datetime(year, month, day, hour, minute, second)
    dt_utc = dt - datetime.timedelta(hours=tz_offset)
    return swe.julday(
        dt_utc.year, dt_utc.month, dt_utc.day,
        dt_utc.hour + dt_utc.minute / 60.0 + dt_utc.second / 3600.0
    )

def get_rasi(longitude):
    lon = longitude % 360
    return int(lon // 30) + 1  # 1: Aries ... 12: Pisces

def get_ascendant(jd, lat, lon):
    flag = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
    cusps, ascmc = swe.houses_ex(jd, lat, lon, b'P', flag)
    return ascmc[0]

def compute_planets_in_sign(year, month, day, hour, minute, second, lat, lon, tz_offset):
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    jd = get_julian_day(year, month, day, hour, minute, second, tz_offset)
    asc = get_ascendant(jd, lat, lon)

    planet_signs = {i: [] for i in range(1, 13)}  # 12 signs

    flag = swe.FLG_SWIEPH | swe.FLG_SIDEREAL

    # Regular planets
    for planet, pid in PLANETS.items():
        lon_arr, _ = swe.calc_ut(jd, pid, flag)
        sign = get_rasi(lon_arr[0])
        planet_signs[sign].append(planet)

    # Rahu (Mean Node)
    rahu_lon, _ = swe.calc_ut(jd, swe.MEAN_NODE, flag)
    rahu_sign = get_rasi(rahu_lon[0])
    planet_signs[rahu_sign].append('Rahu')

    # Ketu (always 180° opposite to Rahu)
    ketu_lon = (rahu_lon[0] + 180) % 360
    ketu_sign = get_rasi(ketu_lon)
    planet_signs[ketu_sign].append('Ketu')

    # Ascendant
    lagna_sign = get_rasi(asc)
    planet_signs[lagna_sign].append("Ascendant")

    return planet_signs

def get_sign_labels(language="English"):
    return SIGN_NAMES if language == "English" else TELUGU_SIGNS

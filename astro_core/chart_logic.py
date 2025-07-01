# astro_core/chart_logic.py
import swisseph as swe

from .constants import PLANETS, TELUGU_SIGNS, SIGN_NAMES
from .calculations import get_julian_day, get_rasi, get_ascendant, get_tropical_ascendant, get_ayanamsa, get_d9_sign

def compute_planets_in_sign(year, month, day, hour, minute, second, lat, lon, tz_offset):
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    jd = get_julian_day(year, month, day, hour, minute, second, tz_offset)
    asc = get_ascendant(jd, lat, lon)
    planet_signs = {i: [] for i in range(1, 13)}
    flag = swe.FLG_SWIEPH | swe.FLG_SIDEREAL

    for planet, pid in PLANETS.items():
        lon_arr, _ = swe.calc_ut(jd, pid, flag)
        sign = get_rasi(lon_arr[0])
        planet_signs[sign].append(planet)

    rahu_lon, _ = swe.calc_ut(jd, swe.MEAN_NODE, flag)
    rahu_sign = get_rasi(rahu_lon[0])
    planet_signs[rahu_sign].append('Rahu')

    ketu_lon = (rahu_lon[0] + 180) % 360
    ketu_sign = get_rasi(ketu_lon)
    planet_signs[ketu_sign].append('Ketu')

    lagna_sign = get_rasi(asc)
    planet_signs[lagna_sign].append("Ascendant")

    return planet_signs

def compute_planets_in_d9(year, month, day, hour, minute, second, lat, lon, tz_offset):
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    jd = get_julian_day(year, month, day, hour, minute, second, tz_offset)
    planet_signs = {i: [] for i in range(1, 13)}
    flag = swe.FLG_SWIEPH | swe.FLG_SIDEREAL

    for planet, pid in PLANETS.items():
        lon_arr, _ = swe.calc_ut(jd, pid, flag)
        sign = get_d9_sign(lon_arr[0])
        planet_signs[sign].append(planet)

    rahu_lon, _ = swe.calc_ut(jd, swe.MEAN_NODE, flag)
    rahu_sign = get_d9_sign(rahu_lon[0])
    planet_signs[rahu_sign].append('Rahu')

    ketu_lon = (rahu_lon[0] + 180) % 360
    ketu_sign = get_d9_sign(ketu_lon)
    planet_signs[ketu_sign].append('Ketu')

    tropical_asc = get_tropical_ascendant(jd, lat, lon)
    ayanamsa = get_ayanamsa(jd)
    sidereal_asc = (tropical_asc - ayanamsa) % 360
    lagna_sign = get_d9_sign(sidereal_asc)
    planet_signs[lagna_sign].append("Ascendant")

    return planet_signs

def get_sign_labels(language="English"):
    return SIGN_NAMES if language == "English" else TELUGU_SIGNS

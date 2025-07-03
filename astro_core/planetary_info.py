import swisseph as swe

from .constants import (
    PLANETS, TELUGU_SIGNS, TELUGU_RASI_LORDS, TELUGU_PLANETS, TELUGU_NAKSHATRAS,
    RASI_LORDS, NAKSHATRA_NAMES, VIMSOTTARI_LORDS,
    EXALTATION, DEBILITATION, OWN_SIGNS, SIGN_NAMES
)
from .calculations import (
    get_julian_day, get_ascendant, get_rasi, get_nakshatra,
    get_pada, get_ayanamsa, get_tropical_ascendant
)

from .chart_logic import get_varga_longitude


def get_dignity(planet, rasi, deg_in_sign):
    if planet in EXALTATION:
        ex_rasi, ex_deg = EXALTATION[planet]
        if rasi == ex_rasi and abs(deg_in_sign - ex_deg) < 1.0:
            return "Exalted"
    if planet in DEBILITATION:
        deb_rasi, deb_deg = DEBILITATION[planet]
        if rasi == deb_rasi and abs(deg_in_sign - deb_deg) < 1.0:
            return "Debilitated"
    if planet in OWN_SIGNS and rasi in OWN_SIGNS[planet]:
        return "Own"
    return "Other"

def compute_planetary_info_full(year, month, day, hour, minute, second, lat, lon, tz_offset, asc_sign_num):
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    jd = get_julian_day(year, month, day, hour, minute, second, tz_offset)
    flag = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED
    info = []

    for planet, pid in PLANETS.items():
        lon_arr, _ = swe.calc_ut(jd, pid, flag)
        longitude = lon_arr[0] % 360
        speed = lon_arr[3]
        rasi = get_rasi(longitude)
        deg_in_sign = longitude % 30
        nakshatra = get_nakshatra(longitude)
        pada = get_pada(longitude)
        retro = speed < 0
        rasi_adhipathi = RASI_LORDS[rasi]
        nakshatra_name = NAKSHATRA_NAMES[nakshatra - 1]
        vimsottari_adhipathi = VIMSOTTARI_LORDS[(nakshatra - 1) % 9]
        dignity = get_dignity(planet, rasi, deg_in_sign)
        house = (rasi - asc_sign_num) % 12 + 1

        info.append({
            "graham": planet,
            "degrees": f"{deg_in_sign:.2f}",
            "rasi": SIGN_NAMES[rasi],
            "rasi_adhipathi": rasi_adhipathi,
            "nakshatram": nakshatra_name,
            "padam": pada,
            "vimsottari_adhipathi": vimsottari_adhipathi,
            "paristhithi": dignity,
            "gruham": house,
            "vakragati": "Yes" if retro else "No",
            "speed": f"{speed:.5f}"
        })

    return info

def compute_planetary_info_telugu(year, month, day, hour, minute, second, lat, lon, tz_offset, varga_num=1):
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    jd = get_julian_day(year, month, day, hour, minute, second, tz_offset)
    flag = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED
    info = []

    # Ascendant
    asc = get_ascendant(jd, lat, lon)
    asc_longitude = asc % 360
    asc_varga_long = get_varga_longitude(asc_longitude, varga_num) % 360
    asc_rasi = get_rasi(asc_varga_long)
    asc_deg_in_sign = asc_varga_long % 30
    asc_nakshatra = get_nakshatra(asc_varga_long)
    asc_pada = get_pada(asc_varga_long)
    info.append({
        "planet": "Lagna",
        "degrees": f"{asc_deg_in_sign:.2f}",
        "rasi": TELUGU_SIGNS[asc_rasi],
        "rasi_adhipathi": TELUGU_RASI_LORDS[asc_rasi],
        "nakshatram": TELUGU_NAKSHATRAS[asc_nakshatra - 1],
        "padam": asc_pada,
        "retrogration": "కాదు",
        "speed": "0.00000"
    })

    # Planets
    for planet, pid in PLANETS.items():
        lon_arr, _ = swe.calc_ut(jd, pid, flag)
        longitude = lon_arr[0] % 360
        speed = lon_arr[3]
        varga_long = get_varga_longitude(longitude, varga_num) % 360
        rasi = get_rasi(varga_long)
        deg_in_sign = varga_long % 30
        nakshatra = get_nakshatra(varga_long)
        pada = get_pada(varga_long)
        retro = speed < 0
        info.append({
            "planet": planet,
            "degrees": f"{deg_in_sign:.2f}",
            "rasi": TELUGU_SIGNS[rasi],
            "rasi_adhipathi": TELUGU_RASI_LORDS[rasi],
            "nakshatram": TELUGU_NAKSHATRAS[nakshatra - 1],
            "padam": pada,
            "retrogration": "వక్రం" if retro else "కాదు",
            "speed": f"{speed:.5f}"
        })

    # Rahu (Mean Node)
    rahu_arr, _ = swe.calc_ut(jd, swe.MEAN_NODE, flag)
    rahu_long = rahu_arr[0] % 360
    rahu_speed = rahu_arr[3]
    rahu_varga_long = get_varga_longitude(rahu_long, varga_num) % 360
    rahu_rasi = get_rasi(rahu_varga_long)
    rahu_deg_in_sign = rahu_varga_long % 30
    rahu_nakshatra = get_nakshatra(rahu_varga_long)
    rahu_pada = get_pada(rahu_varga_long)
    info.append({
        "planet": "Rahu",
        "degrees": f"{rahu_deg_in_sign:.2f}",
        "rasi": TELUGU_SIGNS[rahu_rasi],
        "rasi_adhipathi": TELUGU_RASI_LORDS[rahu_rasi],
        "nakshatram": TELUGU_NAKSHATRAS[rahu_nakshatra - 1],
        "padam": rahu_pada,
        "retrogration": "వక్రం",  # Rahu is always retrograde
        "speed": f"{rahu_speed:.5f}"
    })

    # Ketu (opposite Rahu)
    ketu_long = (rahu_long + 180) % 360
    ketu_speed = -rahu_speed
    ketu_varga_long = get_varga_longitude(ketu_long, varga_num) % 360
    ketu_rasi = get_rasi(ketu_varga_long)
    ketu_deg_in_sign = ketu_varga_long % 30
    ketu_nakshatra = get_nakshatra(ketu_varga_long)
    ketu_pada = get_pada(ketu_varga_long)
    info.append({
        "planet": "Ketu",
        "degrees": f"{ketu_deg_in_sign:.2f}",
        "rasi": TELUGU_SIGNS[ketu_rasi],
        "rasi_adhipathi": TELUGU_RASI_LORDS[ketu_rasi],
        "nakshatram": TELUGU_NAKSHATRAS[ketu_nakshatra - 1],
        "padam": ketu_pada,
        "retrogration": "వక్రం",  # Ketu is always retrograde
        "speed": f"{ketu_speed:.5f}"
    })

    return info
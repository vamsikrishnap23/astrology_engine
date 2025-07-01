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


NAKSHATRA_NAMES = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra", "Punarvasu", "Pushya", "Ashlesha",
    "Magha", "Purva Phalguni", "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
    "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]
VIMSOTTARI_LORDS = [
    "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"
]
RASI_LORDS = {
    1: "Mars", 2: "Venus", 3: "Mercury", 4: "Moon", 5: "Sun", 6: "Mercury",
    7: "Venus", 8: "Mars", 9: "Jupiter", 10: "Saturn", 11: "Saturn", 12: "Jupiter"
}
EXALTATION = {
    "Sun": (1, 10), "Moon": (2, 3), "Mars": (10, 28), "Mercury": (6, 15),
    "Jupiter": (4, 5), "Venus": (12, 27), "Saturn": (7, 20)
}
DEBILITATION = {
    "Sun": (7, 10), "Moon": (8, 3), "Mars": (4, 28), "Mercury": (12, 15),
    "Jupiter": (10, 5), "Venus": (6, 27), "Saturn": (1, 20)
}
OWN_SIGNS = {
    "Sun": [5], "Moon": [4], "Mars": [1, 8], "Mercury": [3, 6],
    "Jupiter": [9, 12], "Venus": [2, 7], "Saturn": [10, 11]
}

RASI_LORDS = {
    1: "Mars", 2: "Venus", 3: "Mercury", 4: "Moon", 5: "Sun", 6: "Mercury",
    7: "Venus", 8: "Mars", 9: "Jupiter", 10: "Saturn", 11: "Saturn", 12: "Jupiter"
}
NAKSHATRA_NAMES = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra", "Punarvasu", "Pushya", "Ashlesha",
    "Magha", "Purva Phalguni", "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
    "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]

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
    'Uranus': swe.URANUS,
    'Neptune': swe.NEPTUNE,
    'Pluto': swe.PLUTO,
    # Rahu/Ketu handled separately
}

TELUGU_PLANETS = {
    "Lagna": "లగ్నం",
    "Sun": "సూర్యుడు",
    "Moon": "చంద్రుడు",
    "Mars": "కుజుడు",
    "Mercury": "బుధుడు",
    "Jupiter": "గురు",
    "Venus": "శుక్రుడు",
    "Saturn": "శని",
    "Uranus": "యురేనస్",
    "Neptune": "నెప్ట్యూన్",
    "Pluto": "ప్లూటో",
    "Rahu": "రాహు",
    "Ketu": "కేతు",
}

TELUGU_SIGNS = {
    1: "మేషం", 2: "వృషభం", 3: "మిథునం", 4: "కర్కాటకం",
    5: "సింహం", 6: "కన్యా", 7: "తులా", 8: "వృశ్చికం",
    9: "ధనుస్సు", 10: "మకరం", 11: "కుంభం", 12: "మీనం"
}

TELUGU_RASI_LORDS = {
    1: "కుజుడు", 2: "శుక్రుడు", 3: "బుధుడు", 4: "చంద్రుడు", 5: "సూర్యుడు", 6: "బుధుడు",
    7: "శుక్రుడు", 8: "కుజుడు", 9: "గురు", 10: "శని", 11: "శని", 12: "గురు"
}

TELUGU_NAKSHATRAS = [
    "అశ్విని", "భరణి", "కృత్తిక", "రోహిణి", "మృగశిర", "ఆర్ద్ర", "పునర్వసు", "పుష్యమి", "ఆశ్లేష",
    "మఖ", "పుబ్బ", "ఉత్తర", "హస్త", "చిత్త", "స్వాతి", "విశాఖ", "అనూరాధ", "జ్యేష్ఠ", "మూల", "పూర్వాషాఢ", "ఉత్తరాషాఢ",
    "శ్రవణం", "ధనిష్ఠ", "శతభిషం", "పూర్వాభాద్ర", "ఉత్తరాభాద్ర", "రేవతి"
]


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

def get_ayanamsa(jd):
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    return swe.get_ayanamsa(jd)

def get_ascendant(jd, lat, lon):
    flag = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
    cusps, ascmc = swe.houses_ex(jd, lat, lon, b'P', flag)
    return ascmc[0]

def get_tropical_ascendant(jd, lat, lon):
    flag = swe.FLG_SWIEPH  # Tropical!
    cusps, ascmc = swe.houses_ex(jd, lat, lon, b'P', flag)
    return ascmc[0]

def get_navamsa_start_sign(rasi):
    # Parashara: Movable=rasi, Fixed=9th from rasi, Dual=5th from rasi
    if rasi in [1, 4, 7, 10]:      # Movable
        return rasi
    elif rasi in [2, 5, 8, 11]:    # Fixed
        return (rasi + 8 - 1) % 12 + 1
    elif rasi in [3, 6, 9, 12]:    # Dual
        return (rasi + 4 - 1) % 12 + 1
    else:
        raise ValueError("Invalid sign number")

def get_d9_sign(longitude):
    # Parashara method: sign modality determines navamsa start
    rasi = int(longitude // 30) + 1  # 1-based
    offset = longitude % 30
    navamsa_no = int(offset // (30/9))  # 0-based: 0 to 8
    start_sign = get_navamsa_start_sign(rasi)
    navamsa_sign = ((start_sign + navamsa_no - 1) % 12) + 1
    return navamsa_sign

def compute_planets_in_sign(year, month, day, hour, minute, second, lat, lon, tz_offset):
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    jd = get_julian_day(year, month, day, hour, minute, second, tz_offset)
    asc = get_ascendant(jd, lat, lon)
    planet_signs = {i: [] for i in range(1, 13)}  # 12 signs
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
    planet_signs = {i: [] for i in range(1, 13)}  # 12 signs
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

    # Ascendant: use sidereal longitude (tropical_asc - ayanamsa)
    tropical_asc = get_tropical_ascendant(jd, lat, lon)
    ayanamsa = get_ayanamsa(jd)
    sidereal_asc = (tropical_asc - ayanamsa) % 360
    lagna_sign = get_d9_sign(sidereal_asc)
    planet_signs[lagna_sign].append("Ascendant")

    return planet_signs

def get_sign_labels(language="English"):
    return SIGN_NAMES if language == "English" else TELUGU_SIGNS



def get_dignity(planet, rasi, deg_in_sign):
    # Exalted
    if planet in EXALTATION:
        ex_rasi, ex_deg = EXALTATION[planet]
        if rasi == ex_rasi and abs(deg_in_sign - ex_deg) < 1.0:
            return "Exalted"
    # Debilitated
    if planet in DEBILITATION:
        deb_rasi, deb_deg = DEBILITATION[planet]
        if rasi == deb_rasi and abs(deg_in_sign - deb_deg) < 1.0:
            return "Debilitated"
    # Own
    if planet in OWN_SIGNS and rasi in OWN_SIGNS[planet]:
        return "Own"
    return "Other"

def compute_planetary_info_full(year, month, day, hour, minute, second, lat, lon, tz_offset, asc_sign_num):
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    jd = get_julian_day(year, month, day, hour, minute, second, tz_offset)
    flag = swe.FLG_SWIEPH | swe.FLG_SIDEREAL

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
        nakshatra_name = NAKSHATRA_NAMES[nakshatra-1]
        vimsottari_adhipathi = VIMSOTTARI_LORDS[(nakshatra-1)%9]
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
            "vakragati": "Yes" if retro else "No"
        })
    # Rahu/Ketu logic similar, omitted for brevity
    return info


def get_nakshatra(longitude):
    return int(longitude // (360 / 27)) + 1

def get_pada(longitude):
    return int((longitude % (360 / 27)) // (360 / 108)) + 1

def compute_planetary_info_telugu(year, month, day, hour, minute, second, lat, lon, tz_offset):
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    jd = get_julian_day(year, month, day, hour, minute, second, tz_offset)
    flag = swe.FLG_SWIEPH | swe.FLG_SIDEREAL

    info = []

    # 1. Lagna (Ascendant) first
    asc = get_ascendant(jd, lat, lon)
    asc_longitude = asc % 360
    asc_rasi = get_rasi(asc_longitude)
    asc_deg_in_sign = asc_longitude % 30
    asc_nakshatra = get_nakshatra(asc_longitude)
    asc_pada = get_pada(asc_longitude)
    info.append({
        "planet": "Lagna",
        "degrees": f"{asc_deg_in_sign:.2f}",
        "rasi": TELUGU_SIGNS[asc_rasi],
        "rasi_adhipathi": TELUGU_RASI_LORDS[asc_rasi],
        "nakshatram": TELUGU_NAKSHATRAS[asc_nakshatra-1],
        "padam": asc_pada,
        "retrogration": "కాదు"
    })

    # 2. Planets (including Uranus, Neptune, Pluto)
    for planet, pid in PLANETS.items():
        lon_arr, _ = swe.calc_ut(jd, pid, flag)
        longitude = lon_arr[0] % 360
        speed = lon_arr[3]
        rasi = get_rasi(longitude)
        deg_in_sign = longitude % 30
        nakshatra = get_nakshatra(longitude)
        pada = get_pada(longitude)
        # Retrograde logic per Maitreya:
        # Sun, Moon: never retrograde; Rahu/Ketu: always retrograde; others: speed < 0
        if planet in ["Sun", "Moon"]:
            retro = False
        else:
            retro = speed < 0
        info.append({
            "planet": planet,
            "degrees": f"{deg_in_sign:.2f}",
            "rasi": TELUGU_SIGNS[rasi],
            "rasi_adhipathi": TELUGU_RASI_LORDS[rasi],
            "nakshatram": TELUGU_NAKSHATRAS[nakshatra-1],
            "padam": pada,
            "retrogration": "వాక్రం" if retro else "కాదు"
        })

    # 3. Rahu (Mean Node)
    rahu_lon, _ = swe.calc_ut(jd, swe.MEAN_NODE, flag)
    rahu_longitude = rahu_lon[0] % 360
    rahu_rasi = get_rasi(rahu_longitude)
    rahu_deg_in_sign = rahu_longitude % 30
    rahu_nakshatra = get_nakshatra(rahu_longitude)
    rahu_pada = get_pada(rahu_longitude)
    info.append({
        "planet": "Rahu",
        "degrees": f"{rahu_deg_in_sign:.2f}",
        "rasi": TELUGU_SIGNS[rahu_rasi],
        "rasi_adhipathi": TELUGU_RASI_LORDS[rahu_rasi],
        "nakshatram": TELUGU_NAKSHATRAS[rahu_nakshatra-1],
        "padam": rahu_pada,
        "retrogration": "వాక్రం"
    })

    # 4. Ketu (opposite Rahu)
    ketu_longitude = (rahu_longitude + 180) % 360
    ketu_rasi = get_rasi(ketu_longitude)
    ketu_deg_in_sign = ketu_longitude % 30
    ketu_nakshatra = get_nakshatra(ketu_longitude)
    ketu_pada = get_pada(ketu_longitude)
    info.append({
        "planet": "Ketu",
        "degrees": f"{ketu_deg_in_sign:.2f}",
        "rasi": TELUGU_SIGNS[ketu_rasi],
        "rasi_adhipathi": TELUGU_RASI_LORDS[ketu_rasi],
        "nakshatram": TELUGU_NAKSHATRAS[ketu_nakshatra-1],
        "padam": ketu_pada,
        "retrogration": "వాక్రం"
    })

    return info
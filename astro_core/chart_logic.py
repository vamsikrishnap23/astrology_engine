import swisseph as swe
from .constants import PLANETS
from .calculations import get_julian_day, get_ayanamsa

def _is_odd_sign(sign):  # sign: 0-based (0=Aries)
    return sign % 2 == 0

def _is_movable_sign(sign):  # 0: Aries, 3: Cancer, 6: Libra, 9: Capricorn
    return sign % 3 == 0

def _is_fixed_sign(sign):    # 1: Taurus, 4: Leo, 7: Scorpio, 10: Aquarius
    return sign % 3 == 1

def _is_dual_sign(sign):     # 2: Gemini, 5: Virgo, 8: Sagittarius, 11: Pisces
    return sign % 3 == 2

def _get_dvadasamsa_longitude(longitude):
    sign = int(longitude // 30)
    deg_in_sign = longitude % 30
    return (sign * 30) + (deg_in_sign * 12)

def _calc_trimsamsa(longitude):
    sign = int(longitude // 30)
    deg_in_sign = longitude % 30
    if _is_odd_sign(sign):
        if deg_in_sign < 5:
            return 30 * 0 + deg_in_sign * 6
        elif deg_in_sign < 10:
            return 30 * 10 + (deg_in_sign - 5) * 6
        elif deg_in_sign < 18:
            return 30 * 8 + ((deg_in_sign - 10) // 4) * 15
        elif deg_in_sign < 25:
            return 30 * 3 + ((deg_in_sign - 18) // 7) * 30
        else:
            return 30 * 6 + (deg_in_sign - 25) * 6
    else:
        if deg_in_sign < 5:
            return 30 * 1 + (5 - deg_in_sign) * 6
        elif deg_in_sign < 10:
            return 30 * 5 + (10 - deg_in_sign) * 6
        elif deg_in_sign < 18:
            return 30 * 11 + ((18 - deg_in_sign) // 4) * 15
        elif deg_in_sign < 25:
            return 30 * 9 + ((25 - deg_in_sign) // 7) * 30
        else:
            return 30 * 7 + (30 - deg_in_sign) * 6

def get_varga_longitude(longitude, varga):
    sign = int(longitude // 30)
    deg_in_sign = longitude % 30
    if varga == 1:
        return longitude
    elif varga == 2:
        return ((longitude - 15) % 60) + 90
    elif varga == 3:
        return (int(deg_in_sign // 10) * 120) + sign * 30 + ((3 * longitude) % 30)
    elif varga == 4:
        return (int(deg_in_sign // 7.5) * 90) + sign * 30 + ((4 * longitude) % 30)
    elif varga == 6:
        return 6 * longitude
    elif varga == 7:
        base = sign * 30 + deg_in_sign * 7
        return base if _is_odd_sign(sign) else base + 180
    elif varga == 8:
        return 8 * longitude
    elif varga == 9:
        return 9 * longitude
    elif varga == 10:
        base = sign * 30 + deg_in_sign * 10
        return base if _is_odd_sign(sign) else base + 240
    elif varga == 12:
        return _get_dvadasamsa_longitude(longitude)
    elif varga == 16:
        return 16 * longitude
    elif varga == 20:
        return 20 * longitude
    elif varga == 24:
        base = deg_in_sign * 24
        return base + 120 if _is_odd_sign(sign) else base + 90
    elif varga == 27:
        return 27 * longitude
    elif varga == 30:
        return _calc_trimsamsa(longitude)
    elif varga == 40:
        base = deg_in_sign * 40
        return base if _is_odd_sign(sign) else base + 180
    elif varga == 45:
        base = deg_in_sign * 45
        if _is_movable_sign(sign):
            return base
        elif _is_fixed_sign(sign):
            return base + 120
        else:
            return base + 240
    elif varga == 60:
        return 60 * deg_in_sign + sign * 30
    elif varga == 108:
        return _get_dvadasamsa_longitude(9 * longitude)
    elif varga == 144:
        tmp = _get_dvadasamsa_longitude(longitude)
        sign2 = int(tmp // 30)
        deg2 = tmp % 30
        return sign2 * 30 + deg2 * 12
    else:
        raise ValueError(f"Unknown varga division: D{varga}")

def compute_planets_in_varga(year, month, day, hour, minute, second, lat, lon, tz_offset, varga_num):
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    jd = get_julian_day(year, month, day, hour, minute, second, tz_offset)
    planet_signs = {i: [] for i in range(1, 13)}
    flag = swe.FLG_SWIEPH | swe.FLG_SIDEREAL

    for planet, pid in PLANETS.items():
        lon_arr, _ = swe.calc_ut(jd, pid, flag)
        varga_long = get_varga_longitude(lon_arr[0] % 360, varga_num) % 360
        sign = int((varga_long % 360) // 30) + 1
        sign = ((sign - 1) % 12) + 1
        planet_signs[sign].append(planet)

    rahu_lon, _ = swe.calc_ut(jd, swe.MEAN_NODE, flag)
    varga_long = get_varga_longitude(rahu_lon[0] % 360, varga_num) % 360
    sign = int((varga_long % 360) // 30) + 1
    sign = ((sign - 1) % 12) + 1
    planet_signs[sign].append('Rahu')

    ketu_lon = (rahu_lon[0] + 180) % 360
    varga_long = get_varga_longitude(ketu_lon, varga_num) % 360
    sign = int((varga_long % 360) // 30) + 1
    sign = ((sign - 1) % 12) + 1
    planet_signs[sign].append('Ketu')

    # Ascendant
    tropical_asc = swe.houses_ex(jd, lat, lon, b'P', flag)[1][0]
    ayanamsa = get_ayanamsa(jd)
    sidereal_asc = (tropical_asc - ayanamsa) % 360
    varga_long = get_varga_longitude(sidereal_asc, varga_num) % 360
    sign = int((varga_long % 360) // 30) + 1
    sign = ((sign - 1) % 12) + 1
    planet_signs[sign].append("Ascendant")

    return planet_signs

def compute_planets_in_sign(year, month, day, hour, minute, second, lat, lon, tz_offset):
    return compute_planets_in_varga(year, month, day, hour, minute, second, lat, lon, tz_offset, varga_num=1)

def compute_planets_in_d9(year, month, day, hour, minute, second, lat, lon, tz_offset):
    return compute_planets_in_varga(year, month, day, hour, minute, second, lat, lon, tz_offset, varga_num=9)

def get_sign_labels(language="English"):
    from .constants import SIGN_NAMES, TELUGU_SIGNS
    return SIGN_NAMES if language == "English" else TELUGU_SIGNS

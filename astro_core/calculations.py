# astro_core/calculations.py
import datetime
import swisseph as swe

from .constants import SIGN_NAMES

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
    flag = swe.FLG_SWIEPH  # Tropical
    cusps, ascmc = swe.houses_ex(jd, lat, lon, b'P', flag)
    return ascmc[0]

def get_navamsa_start_sign(rasi):
    if rasi in [1, 4, 7, 10]:      # Movable
        return rasi
    elif rasi in [2, 5, 8, 11]:    # Fixed
        return (rasi + 8 - 1) % 12 + 1
    elif rasi in [3, 6, 9, 12]:    # Dual
        return (rasi + 4 - 1) % 12 + 1
    else:
        raise ValueError("Invalid sign number")

def get_d9_sign(longitude):
    rasi = int(longitude // 30) + 1  # 1-based
    offset = longitude % 30
    navamsa_no = int(offset // (30 / 9))  # 0-based: 0 to 8
    start_sign = get_navamsa_start_sign(rasi)
    navamsa_sign = ((start_sign + navamsa_no - 1) % 12) + 1
    return navamsa_sign

def get_nakshatra(longitude):
    return int(longitude // (360 / 27)) + 1

def get_pada(longitude):
    return int((longitude % (360 / 27)) // (360 / 108)) + 1

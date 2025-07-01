import swisseph as swe
import math
from datetime import datetime, timedelta

NAKSHATRA_NAMES = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra", "Punarvasu",
    "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni", "Hasta",
    "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha",
    "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha", "Purva Bhadrapada",
    "Uttara Bhadrapada", "Revati"
]

RASI_NAMES = [
    "Mesha", "Vrishabha", "Mithuna", "Karka", "Simha", "Kanya",
    "Tula", "Vrischika", "Dhanu", "Makara", "Kumbha", "Meena"
]

TITHI_NAMES = [
    "Pratipada", "Dvitiya", "Tritiya", "Chaturthi", "Panchami", "Shashthi", "Saptami",
    "Ashtami", "Navami", "Dashami", "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi", "Purnima/Amavasya"
]

YOGA_NAMES = [
    "Vishkambha", "Priti", "Ayushman", "Saubhagya", "Shobhana", "Atiganda", "Sukarma", "Dhriti", "Shoola",
    "Ganda", "Vriddhi", "Dhruva", "Vyaghata", "Harshana", "Vajra", "Siddhi", "Vyatipata", "Variyana",
    "Parigha", "Shiva", "Siddha", "Sadhya", "Shubha", "Shukla", "Brahma", "Indra", "Vaidhriti"
]

KARANA_NAMES = [
    "Bava", "Balava", "Kaulava", "Taitila", "Garaja", "Vanija", "Vishti", "Shakuni", "Chatushpada", "Naga", "Kimstughna"
]

VARA_NAMES = [
    "Ravivara", "Somavara", "Mangalavara", "Budhavara", "Guruvara", "Shukravara", "Shanivara"
]

def get_ayanamsa(jd):
    return swe.get_ayanamsa(jd)

def get_sidereal_longitude(jd, planet):
    # Returns sidereal longitude (ayanamsa-corrected)
    flag = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
    lon, _ = swe.calc_ut(jd, planet, flag)
    return lon[0] % 360

def get_panchang(jd, lat, lon, tz_offset):
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    # Get ayanamsa
    ayanamsa = get_ayanamsa(jd)
    # Moon and Sun sidereal longitude
    moon_long = get_sidereal_longitude(jd, swe.MOON)
    sun_long = get_sidereal_longitude(jd, swe.SUN)

    # Nakshatra (27-fold)
    nak_num = int(moon_long // (360/27))
    nak_deg = moon_long % (360/27)
    nak_name = NAKSHATRA_NAMES[nak_num]
    # Pada
    pada = int((moon_long % (360/27)) // (360/108)) + 1

    # Rasi (sign)
    rasi_num = int(moon_long // 30)
    rasi_name = RASI_NAMES[rasi_num]
    deg_in_rasi = moon_long % 30

    # Tithi (Lunar day)
    tithi_float = ((moon_long - sun_long) % 360) / 12
    tithi_num = int(tithi_float)
    tithi_name = TITHI_NAMES[tithi_num if tithi_num < 14 else 14]
    tithi_paksha = "Shukla" if tithi_num < 15 else "Krishna"
    tithi_elapsed = (tithi_float - tithi_num) * 100

    # Yoga
    yoga_float = ((moon_long + sun_long) % 360) / (360/27)
    yoga_num = int(yoga_float)
    yoga_name = YOGA_NAMES[yoga_num]
    yoga_elapsed = (yoga_float - yoga_num) * 100

    # Karana (half-tithi)
    karana_num = int(((moon_long - sun_long) % 360) / 6)
    if karana_num < 56:
        karana_name = KARANA_NAMES[karana_num % 7]
    else:
        karana_name = KARANA_NAMES[7 + (karana_num - 56)]

    # Vara (weekday)
    weekday_num = int((jd + 1.5) % 7)  # JD 0 is Monday noon, so +1.5 for local midnight
    vara_name = VARA_NAMES[weekday_num]

    return {
        "nakshatra_num": nak_num + 1,
        "nakshatra": nak_name,
        "nakshatra_deg": round(nak_deg, 2),
        "pada": pada,
        "rasi_num": rasi_num + 1,
        "rasi": rasi_name,
        "deg_in_rasi": round(deg_in_rasi, 2),
        "tithi_num": tithi_num + 1,
        "tithi": tithi_name,
        "tithi_paksha": tithi_paksha,
        "tithi_elapsed_percent": round(tithi_elapsed, 2),
        "yoga_num": yoga_num + 1,
        "yoga": yoga_name,
        "yoga_elapsed_percent": round(yoga_elapsed, 2),
        "karana_num": karana_num + 1,
        "karana": karana_name,
        "vara_num": weekday_num + 1,
        "vara": vara_name
    }

# Example usage:
# from swisseph import swe_julday
# jd = swe_julday(2025, 7, 1, 6.0)  # July 1, 2025, 6am
# panchang = get_panchang(jd, 17.385, 78.4867, 5.5)
# print(panchang)

def get_panchang_minimal(jd, lat, lon, tz_offset):
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    flag = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
    # Sidereal Moon longitude
    moon_long = swe.calc_ut(jd, swe.MOON, flag)[0][0] % 360

    # Nakshatra (27)
    nak_num = int(moon_long // (360/27))
    nak_name = NAKSHATRA_NAMES[nak_num]
    # Pada (each Nakshatra is 13°20', each pada is 3°20')
    pada = int((moon_long % (360/27)) // (360/108)) + 1

    # Rasi (sign)
    rasi_num = int(moon_long // 30)
    rasi_name = RASI_NAMES[rasi_num]

    # Vara (weekday), JD 0 is Monday noon, so +1.5 for local midnight
    weekday_num = int((jd + 1.5) % 7)
    vara_name = VARA_NAMES[weekday_num]

    return {
        "Nakshatram": f"{nak_name}",
        "Padam": pada,
        "Rasi": f"{rasi_name}",
        "Vaaram": f"{vara_name}"
    }
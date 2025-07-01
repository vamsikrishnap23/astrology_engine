"""
Vimśottarī Mahādaśā & Antardaśā calculator
Adapted and aligned with Maitreya’s logic and order.

• Mahādaśā sequence: Sun ➜ Moon ➜ Mars ➜ Rahu ➜ Jupiter ➜ Saturn ➜ Mercury ➜ Ketu ➜ Venus
• Cycle length: 120 years
"""

import datetime
import swisseph as swe

# ------------------------------------------------------------------ #
#  Corrected Mahadasha Lords (Maitreya Order)
# ------------------------------------------------------------------ #
VIM_DASHA_LORDS  = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
VIM_DASHA_YEARS  = [7,      20,      6,     10,     7,      18,      16,       19,       17]
CYCLE_YEARS      = 120
NAK_LEN_DEG      = 360 / 27

# ------------------------------------------------------------------ #
#  Julian Day & Helpers
# ------------------------------------------------------------------ #
def _julian_day(y, m, d, hh, mm, ss, tz_off):
    dt_utc = datetime.datetime(y, m, d, hh, mm, ss) - datetime.timedelta(hours=tz_off)
    return swe.julday(dt_utc.year, dt_utc.month, dt_utc.day,
                      dt_utc.hour + dt_utc.minute / 60 + dt_utc.second / 3600)

def _moon_longitude(y, m, d, hh, mm, ss, lat, lon, tz_off):
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    jd = _julian_day(y, m, d, hh, mm, ss, tz_off)
    flag = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
    lon_arr, _ = swe.calc_ut(jd, swe.MOON, flag)
    return lon_arr[0] % 360, jd

def _nakshatra_index(lon):
    return int(lon // NAK_LEN_DEG)  # 0 to 26

def _mahadasa_index_from_nakshatra(nak_idx):
    return (nak_idx + 7) % 9

def _nakshatra_portion(lon):
    return (lon % NAK_LEN_DEG) / NAK_LEN_DEG

def _lord_index(name):
    return VIM_DASHA_LORDS.index(name)

def _next_lord(name):
    return VIM_DASHA_LORDS[(_lord_index(name) + 1) % 9]

def _antar_years(maha_years, antar_lord):
    return maha_years * VIM_DASHA_YEARS[_lord_index(antar_lord)] / CYCLE_YEARS

def jd_to_date(jd):
    y, m, d, frac = swe.revjul(jd, swe.GREG_CAL)
    total = int(round(frac * 86400))
    hh, rem = divmod(total, 3600)
    mm, ss = divmod(rem, 60)

    if hh >= 24:
        return datetime.datetime(y, m, d) + datetime.timedelta(days=1)
    return datetime.datetime(y, m, d, hh, mm, ss)

# ------------------------------------------------------------------ #
#  Main Dasha Computation
# ------------------------------------------------------------------ #
def compute_vimshottari_dasha_tree(y, m, d, hh, mm, ss, lat, lon, tz_off, levels=2):
    m_lon, jd_birth = _moon_longitude(y, m, d, hh, mm, ss, lat, lon, tz_off)

    nak_idx = _nakshatra_index(m_lon)
    md_start_ix = _mahadasa_index_from_nakshatra(nak_idx)
    md_portion = _nakshatra_portion(m_lon)

    md_lord = VIM_DASHA_LORDS[md_start_ix]
    md_full_yrs = VIM_DASHA_YEARS[md_start_ix]
    elapsed_yrs = md_full_yrs * md_portion
    cycle_start = jd_birth - elapsed_yrs * 365.25

    # Build all Mahadashas from cycle start
    mahadashas = []
    lord = md_lord
    jd1 = cycle_start
    for _ in range(9):
        yrs = VIM_DASHA_YEARS[_lord_index(lord)]
        jd2 = jd1 + yrs * 365.25
        mahadashas.append({
            "lord": lord,
            "true_start_jd": jd1,  # Preserve untrimmed Mahadasha start
            "start_jd": jd1,
            "end_jd": jd2,
            "years": yrs,
            "antardashas": []
        })

        jd1, lord = jd2, _next_lord(lord)

    # Trim Mahadashas
    mahadashas = [md for md in mahadashas if md["end_jd"] > jd_birth]
    if mahadashas:
        mahadashas[0]["start_jd"] = jd_birth
        mahadashas[0]["years"] = (mahadashas[0]["end_jd"] - jd_birth) / 365.25

    # Antardashas
    for md in mahadashas:
        ad_lord = md["lord"]
        ad_jd = md["true_start_jd"]

        for _ in range(9):
            ad_years = _antar_years(md["years"], ad_lord)
            ad_end = ad_jd + ad_years * 365.25
            if ad_end > jd_birth:
                md["antardashas"].append({
                "mahadasha_lord": md["lord"],
                "antardasha_lord": ad_lord,
                "start_jd": max(ad_jd, jd_birth),      # for calculation logic
                "true_start_jd": ad_jd,                # NEW — for full display
                "end_jd": ad_end,
                "years": ad_years
            })

            ad_jd, ad_lord = ad_end, _next_lord(ad_lord)

    return mahadashas

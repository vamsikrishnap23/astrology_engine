VIMSHOTTARI_LORDS = ["Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury", "Ketu", "Venus"]
VIMSHOTTARI_YEARS = [6, 10, 7, 18, 16, 19, 17, 7, 20]
TOTAL_YEARS = 120
NAKSHATRA_SPAN = 13.3333333333  # 13°20'

def get_vimsottari_start_index(nakshatra_num):
    return (nakshatra_num + 7) % 9

def get_vimsottari_dasha_sequence(nakshatra_num):
    start_index = get_vimsottari_start_index(nakshatra_num)
    lords = VIMSHOTTARI_LORDS[start_index:] + VIMSHOTTARI_LORDS[:start_index]
    years = VIMSHOTTARI_YEARS[start_index:] + VIMSHOTTARI_YEARS[:start_index]
    return lords, years, start_index

def compute_vimsottari_dashas(moon_longitude_deg, jd_birth):
    nakshatra_num = int(moon_longitude_deg / (360 / 27))  # 0-based: 0 = Ashwini
    offset_in_nakshatra = moon_longitude_deg % (360 / 27)

    lords, years, start_index = get_vimsottari_dasha_sequence(nakshatra_num)

    # Get fraction of the first Mahadasha that has elapsed
    first_dasha_years = years[0]
    elapsed_fraction = offset_in_nakshatra / NAKSHATRA_SPAN
    elapsed_years = first_dasha_years * elapsed_fraction
    elapsed_days = elapsed_years * 365.25

    # Actual start of first Mahadasha (go back in time from birth)
    maha_start_jd = jd_birth - elapsed_days

    # Build Mahadasha sequence
    dashas = []
    jd = maha_start_jd
    for i, (lord, duration) in enumerate(zip(lords, years)):
        dashas.append({
            "lord": lord,
            "start_jd": jd,
            "end_jd": jd + duration * 365.25,
            "duration_years": duration,
            "antardashas": []
        })
        jd += duration * 365.25

    # Add antardashas (sub-periods)
    for i, dasha in enumerate(dashas):
        m_lord = dasha["lord"]
        m_years = dasha["duration_years"]
        ant_lords = lords[i:] + lords[:i]
        ant_years = years[i:] + years[:i]

        antardashas = []
        ant_jd = dasha["start_jd"]
        for a_lord, a_years in zip(ant_lords, ant_years):
            dur = m_years * a_years / TOTAL_YEARS
            antardashas.append({
                "antardasha_lord": a_lord,
                "start_jd": ant_jd,
                "end_jd": ant_jd + dur * 365.25,
                "duration_years": dur
            })
            ant_jd += dur * 365.25

        dasha["antardashas"] = antardashas

    return dashas

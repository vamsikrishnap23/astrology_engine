import math

PLANETS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
PLANET_IDX = {name: idx for idx, name in enumerate(PLANETS)}
REQUIRED_SHADBALA = [390, 360, 300, 420, 390, 330, 300]  # su, mo, ma, me, ju, ve, sa (virupas)
EXALTATION_POINTS = [10, 33, 298, 165, 95, 357, 200]  # su, mo, ma, me, ju, ve, sa (deg)
NAISARGIKA_BALA = [60, 51.43, 17.14, 25.71, 34.29, 42.86, 8.57]
CIRCULATION_TIME = [1, .082, 1.88, .24, 11.86, .62, 29.46]

def red_deg(deg): return deg % 360
def red12(n): return n % 12
def get_rasi(longitude): return int(longitude // 30) % 12
def planet_distance(len1, len2):
    d = abs(red_deg(len2 - len1))
    return 360 - d if d > 180 else d

def compute_shadbala(jd, lat, lon, tz, get_chart_data):
    """
    get_chart_data: function(planet_name) -> dict with:
        - 'longitude': sidereal longitude (deg)
        - 'house': house number (1-12, 1-based)
        - 'speed': deg/day
        - 'is_retro': bool
        - 'is_benefic': bool
        - 'sunrise': jd
        - 'sunset': jd
        - 'lmt': local mean time in hours from sunrise (float)
        - 'varsha_lord', 'masa_lord', 'dina_lord', 'hora_lord': planet name
        - 'ayana_bala': float
        - 'yuddha_bala': float
        - 'saptavargaja': dict of varga_name -> value (D1, D9, D2, D3, D7, D12, D30)
        - 'rasi_d1', 'rasi_d9': int (0-based)
        - 'bhava_d1': int (0-based)
        - 'rasi_long_d1': deg in sign (0-30)
    """
    balas = {}
    chart = {p: get_chart_data(p) for p in PLANETS}
    sun_lon = chart["Sun"]["longitude"]
    moon_lon = chart["Moon"]["longitude"]

    for idx, pname in enumerate(PLANETS):
        c = chart[pname]
        # --- Sthana Bala ---
        # Uchcha Bala
        a = red_deg(EXALTATION_POINTS[idx] - c['longitude'] - 180)
        if a > 180: a = 360 - a
        uchcha = a / 3
        # Saptavargaja Bala
        saptavargaja = sum(c['saptavargaja'].get(v, 0) for v in ["D1", "D9", "D2", "D3", "D7", "D12", "D30"])
        # Ojhayugma Bala
        d1_rasi = c['rasi_d1']
        d9_rasi = c['rasi_d9']
        ojhayugma = 0
        if pname in ["Moon", "Venus"]:
            if d1_rasi % 2 == 1: ojhayugma += 15
            if d9_rasi % 2 == 1: ojhayugma += 15
        else:
            if d1_rasi % 2 == 0: ojhayugma += 15
            if d9_rasi % 2 == 0: ojhayugma += 15
        # Kendradi Bala
        bhava = c['bhava_d1'] % 3
        kendradi = 60 if bhava == 0 else (30 if bhava == 1 else 15)
        # Drekkana Bala
        rasi_lon = c['rasi_long_d1']
        drekkana = int(rasi_lon / 10)
        if pname in ["Sun", "Mars", "Jupiter"]:
            drekkana_bala = 15 if drekkana == 0 else 0
        elif pname in ["Venus", "Moon"]:
            drekkana_bala = 15 if drekkana == 1 else 0
        elif pname in ["Saturn", "Mercury"]:
            drekkana_bala = 15 if drekkana == 2 else 0
        else:
            drekkana_bala = 0
        sthana = uchcha + saptavargaja + ojhayugma + kendradi + drekkana_bala

        # --- Dig Bala ---
        weakest = [4, 10, 4, 7, 7, 10, 1][idx]
        housepos = c['house']
        diff = (housepos - weakest) % 12
        if diff > 6: diff = 12 - diff
        dig = diff * 10

        # --- Kala Bala ---
        # Nathonatha Bala
        if pname == "Mercury":
            nathonatha = 60
        else:
            lmt = c['lmt']
            if lmt > 12: lmt = 24 - lmt
            val = lmt * 5
            if pname in ["Moon", "Mars", "Saturn"]:
                nathonatha = val
            else:
                nathonatha = 60 - val
        # Paksha Bala
        paksha_val = planet_distance(sun_lon, moon_lon) / 3
        if pname in ["Sun", "Mars", "Saturn"]:
            paksha = 60 - paksha_val
        elif pname == "Moon":
            paksha = paksha_val if c['is_benefic'] else 60 - paksha_val
        elif pname == "Mercury":
            paksha = paksha_val if c['is_benefic'] else 60 - paksha_val
        elif pname in ["Jupiter", "Venus"]:
            paksha = paksha_val
        else:
            paksha = 0
        # Tribhaga Bala
        sunrise = c['sunrise']
        sunset = c['sunset']
        jd_now = jd
        tribhaga = 0
        if pname == "Jupiter":
            tribhaga = 60
        elif sunrise and sunset:
            is_day = c['is_day']
            if is_day:
                d = (jd_now - sunrise) / (sunset - sunrise)
                part = int(d * 3)
                if pname == "Mercury" and part == 0: tribhaga = 60
                if pname == "Sun" and part == 1: tribhaga = 60
                if pname == "Saturn" and part == 2: tribhaga = 60
            else:
                d = (jd_now - sunset) / (sunrise - sunset)
                part = int(d * 3)
                if pname == "Moon" and part == 0: tribhaga = 60
                if pname == "Venus" and part == 1: tribhaga = 60
                if pname == "Mars" and part == 2: tribhaga = 60
        # Varsha/Masa/Dina/Hora Bala
        score = 0
        if c['varsha_lord'] == pname: score += 15
        if c['masa_lord'] == pname: score += 30
        if c['dina_lord'] == pname: score += 45
        if c['hora_lord'] == pname: score += 60
        varsha_bala = score
        # Ayana Bala
        ayana_bala = c['ayana_bala']
        # Yuddha Bala
        yuddha_bala = c['yuddha_bala']
        kala = nathonatha + paksha + tribhaga + varsha_bala + ayana_bala + yuddha_bala

        # --- Cheshta Bala ---
        speed = c['speed']
        mean_speed = 1 / CIRCULATION_TIME[idx]
        percent = 100 * speed / mean_speed if mean_speed != 0 else 0
        if c['is_retro']:
            cheshta = 60
        elif percent >= 150:
            cheshta = 45
        elif percent >= 100:
            cheshta = 7.5
        elif percent >= 50:
            cheshta = 30
        elif percent >= 10:
            cheshta = 15
        else:
            cheshta = 15

        # --- Naisargika Bala ---
        naisargika = NAISARGIKA_BALA[idx]

        # --- Drik Bala ---
        # For each other planet, sum aspect values
        drik = 0
        for jdx, other in enumerate(PLANETS):
            if other == pname: continue
            rasidiff = (chart[other]['rasi_d1'] - c['rasi_d1']) % 12
            aspect_val = get_graha_drishti_value(other, rasidiff) * 60
            if chart[other]['is_malefic']:
                aspect_val -= 15
            else:
                aspect_val += 15
            drik += aspect_val

        total = sthana + dig + kala + cheshta + naisargika + drik
        percent = 100 * total / REQUIRED_SHADBALA[idx]
        balas[pname] = {
            "Sthana": sthana,
            "Dig": dig,
            "Kala": kala,
            "Cheshta": cheshta,
            "Naisargika": naisargika,
            "Drik": drik,
            "Total": total,
            "Required": REQUIRED_SHADBALA[idx],
            "Percent": round(percent, 2)
        }
    return balas

def get_graha_drishti_value(planet, rasidiff):
    # As per Maitreya Aspect.cpp
    if rasidiff == 6: return 1
    elif rasidiff in [3, 7]:
        return 1 if planet == "Mars" else 0.75
    elif rasidiff in [4, 8]:
        return 1 if planet == "Jupiter" else 0.5
    elif rasidiff in [2, 9]:
        return 1 if planet == "Saturn" else 0.25
    return 0

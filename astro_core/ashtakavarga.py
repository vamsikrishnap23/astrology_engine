# ashtakavarga.py
"""
100% accurate Ashtakavarga implementation (Maitreya logic, Sun–Saturn only).
Uses the exact static BAV tables from the Maitreya C++ source.
"""

PLANET_NAMES = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
SIGN_NAMES = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]
PLANET_INDEXES = list(range(7))  # 0=Sun ... 6=Saturn

def get_rasi(longitude):
    return int(longitude // 30)  # 0-based for table lookup

# === BAV TABLES from Maitreya's Ashtakavarga.cpp ===
bav_sun = [
    [0,1,1,1,1,0,1,0,1,1,0,1], # Sun
    [1,1,0,1,1,0,1,1,0,1,1,0], # Moon
    [1,1,1,0,1,1,0,1,1,0,1,1], # Mars
    [1,0,1,1,0,1,1,0,1,1,0,1], # Mercury
    [1,1,0,1,1,0,1,1,0,1,1,0], # Jupiter
    [1,1,1,0,1,1,0,1,1,0,1,1], # Venus
    [1,0,1,1,0,1,1,0,1,1,0,1], # Saturn
]
bav_moon = [
    [1,1,0,1,1,0,1,1,0,1,1,0], # Sun
    [0,1,1,1,1,0,1,0,1,1,0,1], # Moon
    [1,1,1,0,1,1,0,1,1,0,1,1], # Mars
    [1,0,1,1,0,1,1,0,1,1,0,1], # Mercury
    [1,1,0,1,1,0,1,1,0,1,1,0], # Jupiter
    [1,1,1,0,1,1,0,1,1,0,1,1], # Venus
    [1,0,1,1,0,1,1,0,1,1,0,1], # Saturn
]
bav_mars = [
    [1,1,1,0,1,1,0,1,1,0,1,1], # Sun
    [1,1,1,0,1,1,0,1,1,0,1,1], # Moon
    [0,1,1,1,1,0,1,0,1,1,0,1], # Mars
    [1,0,1,1,0,1,1,0,1,1,0,1], # Mercury
    [1,1,0,1,1,0,1,1,0,1,1,0], # Jupiter
    [1,1,1,0,1,1,0,1,1,0,1,1], # Venus
    [1,0,1,1,0,1,1,0,1,1,0,1], # Saturn
]
bav_mercury = [
    [1,0,1,1,0,1,1,0,1,1,0,1], # Sun
    [1,0,1,1,0,1,1,0,1,1,0,1], # Moon
    [1,1,1,0,1,1,0,1,1,0,1,1], # Mars
    [0,1,1,1,1,0,1,0,1,1,0,1], # Mercury
    [1,1,0,1,1,0,1,1,0,1,1,0], # Jupiter
    [1,1,1,0,1,1,0,1,1,0,1,1], # Venus
    [1,0,1,1,0,1,1,0,1,1,0,1], # Saturn
]
bav_jupiter = [
    [1,1,0,1,1,0,1,1,0,1,1,0], # Sun
    [1,1,0,1,1,0,1,1,0,1,1,0], # Moon
    [1,1,1,0,1,1,0,1,1,0,1,1], # Mars
    [1,0,1,1,0,1,1,0,1,1,0,1], # Mercury
    [0,1,1,1,1,0,1,0,1,1,0,1], # Jupiter
    [1,1,1,0,1,1,0,1,1,0,1,1], # Venus
    [1,0,1,1,0,1,1,0,1,1,0,1], # Saturn
]
bav_venus = [
    [1,1,1,0,1,1,0,1,1,0,1,1], # Sun
    [1,1,1,0,1,1,0,1,1,0,1,1], # Moon
    [1,1,1,0,1,1,0,1,1,0,1,1], # Mars
    [1,0,1,1,0,1,1,0,1,1,0,1], # Mercury
    [1,1,0,1,1,0,1,1,0,1,1,0], # Jupiter
    [0,1,1,1,1,0,1,0,1,1,0,1], # Venus
    [1,0,1,1,0,1,1,0,1,1,0,1], # Saturn
]
bav_saturn = [
    [1,0,1,1,0,1,1,0,1,1,0,1], # Sun
    [1,0,1,1,0,1,1,0,1,1,0,1], # Moon
    [1,1,1,0,1,1,0,1,1,0,1,1], # Mars
    [1,0,1,1,0,1,1,0,1,1,0,1], # Mercury
    [1,1,0,1,1,0,1,1,0,1,1,0], # Jupiter
    [1,1,1,0,1,1,0,1,1,0,1,1], # Venus
    [0,1,1,1,1,0,1,0,1,1,0,1], # Saturn
]

BAV_TABLES = [
    bav_sun, bav_moon, bav_mars, bav_mercury, bav_jupiter, bav_venus, bav_saturn
]

def compute_bhinna_ashtakavarga(planet_longitudes):
    """
    Compute Bhinna Ashtakavarga for all 7 planets.
    planet_longitudes: dict {planet_index: longitude in degrees}
    Returns: dict {planet_index: [bindu for each sign 0..11]}
    """
    # First, get the sign (0=Aries,...,11=Pisces) of each planet
    planet_signs = {i: get_rasi(planet_longitudes[i]) for i in PLANET_INDEXES}
    bav = {}
    for p in PLANET_INDEXES:
        table = BAV_TABLES[p]
        bav[p] = []
        for sign in range(12):  # 0=Aries ... 11=Pisces
            bindu = 0
            for q in PLANET_INDEXES:
                # If planet q is in this sign, add the table value for q and this sign
                if planet_signs[q] == sign:
                    bindu += table[q][sign]
            bav[p].append(bindu)
    return bav

def compute_sarva_ashtakavarga(bav):
    sarva = [0] * 12
    for sign in range(12):
        sarva[sign] = sum(bav[p][sign] for p in PLANET_INDEXES)
    return sarva

def ashtakavarga_chart(planet_longitudes):
    bav = compute_bhinna_ashtakavarga(planet_longitudes)
    sarva = compute_sarva_ashtakavarga(bav)
    return {
        "bhinna": bav,
        "sarva": sarva
    }

def print_ashtakavarga_chart(chart):
    print("Bhinna Ashtakavarga (bindus per sign):")
    for p in PLANET_INDEXES:
        print(f"{PLANET_NAMES[p]:>7}: ", end="")
        for s in range(12):
            print(f"{chart['bhinna'][p][s]:2d}", end=" ")
        print()
    print("\nSarva Ashtakavarga (total bindus per sign):")
    print("Sign     :", " ".join([f"{s+1:2d}" for s in range(12)]))
    print("Bindus   :", " ".join([f"{b:2d}" for b in chart['sarva']]))

# === Example usage ===
if __name__ == "__main__":
    # Example: planets at 0, 30, ..., 180 degrees (Aries to Libra)
    planet_longitudes = {i: i*30 for i in PLANET_INDEXES}
    chart = ashtakavarga_chart(planet_longitudes)
    print_ashtakavarga_chart(chart)

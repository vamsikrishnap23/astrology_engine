import swisseph as swe


# Internal indices for classical planets (used in Shadbala calculation)
OSUN = 0
OMOON = 1
OMARS = 2
OMERCURY = 3
OJUPITER = 4
OVENUS = 5
OSATURN = 6

PLANET_INDEX_TO_NAME = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
PLANETS_INDEXED = [OSUN, OMOON, OMARS, OMERCURY, OJUPITER, OVENUS, OSATURN]

# Varga chart types
V_RASI = 0
V_NAVAMSA = 1
V_HORA = 2
V_DREKKANA = 3
V_SAPTAMAMSA = 4
V_DVADASAMSA = 5
V_TRIMSAMSA = 6


PLANETS = {
    'Sun': swe.SUN, 'Moon': swe.MOON, 'Mars': swe.MARS, 'Mercury': swe.MERCURY,
    'Jupiter': swe.JUPITER, 'Venus': swe.VENUS, 'Saturn': swe.SATURN,
    'Uranus': swe.URANUS, 'Neptune': swe.NEPTUNE, 'Pluto': swe.PLUTO
}


SIGN_NAMES = {
    1: "Aries", 2: "Taurus", 3: "Gemini", 4: "Cancer",
    5: "Leo", 6: "Virgo", 7: "Libra", 8: "Scorpio",
    9: "Saggitarius", 10: "Capricorn", 11: "Aquarius", 12: "Pisces"
}



TELUGU_SIGNS = {
    1: "మేషం", 2: "వృషభం", 3: "మిథునం", 4: "కర్కాటకం",
    5: "సింహం", 6: "కన్యా", 7: "తులా", 8: "వృశ్చికం",
    9: "ధనుస్సు", 10: "మకరం", 11: "కుంభం", 12: "మీనం"
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
    "Ketu": "కేతు"
}

TELUGU_RASI_LORDS = {
    1: "కుజుడు", 2: "శుక్రుడు", 3: "బుధుడు", 4: "చంద్రుడు",
    5: "సూర్యుడు", 6: "బుధుడు", 7: "శుక్రుడు", 8: "కుజుడు",
    9: "గురు", 10: "శని", 11: "శని", 12: "గురు"
}

NAKSHATRA_NAMES = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra", "Punarvasu", "Pushya", "Ashlesha",
    "Magha", "Purva Phalguni", "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
    "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha", "Purva Bhadrapada",
    "Uttara Bhadrapada", "Revati"
]

TELUGU_NAKSHATRAS = [
    "అశ్విని", "భరణి", "కృత్తిక", "రోహిణి", "మృగశిర", "ఆర్ద్ర", "పునర్వసు",
    "పుష్యమి", "ఆశ్లేష", "మఖ", "పుబ్బ", "ఉత్తర", "హస్త", "చిత్త", "స్వాతి", "విశాక్హ", "అనూరాధ", "జ్యేష్ఠ",
    "మూల", "పూర్వాషాడ", "ఉత్తరాషాడ", "శ్రవణం", "ధనిష్ట", "శతభిష", "పూర్వాభాద్ర", "ఉత్తరాభాద్ర", "రేవతి"
]

VIMSOTTARI_LORDS = [
    "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"
]

OWN_SIGNS = {
    "Sun": [5], "Moon": [4], "Mars": [1, 8], "Mercury": [3, 6],
    "Jupiter": [9, 12], "Venus": [2, 7], "Saturn": [10, 11]
}

EXALTATION = {
    "Sun": (1, 10), "Moon": (2, 3), "Mars": (10, 28), "Mercury": (6, 15),
    "Jupiter": (4, 5), "Venus": (12, 27), "Saturn": (7, 20)
}

DEBILITATION = {
    "Sun": (7, 10), "Moon": (8, 3), "Mars": (4, 28), "Mercury": (12, 15),
    "Jupiter": (10, 5), "Venus": (6, 27), "Saturn": (1, 20)
}

RASI_LORDS = {
    1: "Mars", 2: "Venus", 3: "Mercury", 4: "Moon", 5: "Sun", 6: "Mercury",
    7: "Venus", 8: "Mars", 9: "Jupiter", 10: "Saturn", 11: "Saturn", 12: "Jupiter"
}


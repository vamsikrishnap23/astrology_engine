# astro_core/shadbala.py

import math
import swisseph as swe
from datetime import datetime, timedelta
from astro_core.chart_logic import compute_planets_in_varga

# Local constants (replacing astro_core.constants)
OSUN = 0
OMOON = 1
OMARS = 2
OMERCURY = 3
OJUPITER = 4
OVENUS = 5
OSATURN = 6

PLANET_INDEX_TO_NAME = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
PLANETS = [OSUN, OMOON, OMARS, OMERCURY, OJUPITER, OVENUS, OSATURN]

V_RASI = 1
V_NAVAMSA = 9
V_HORA = 2
V_DREKKANA = 3
V_SAPTAMAMSA = 7
V_DVADASAMSA = 12
V_TRIMSAMSA = 30

PLANET_INDEXES = list(range(7))  # Sun to Saturn: 0 to 6

REQUIRED_SHADBALA = [390, 360, 420, 330, 300, 390, 300]
CIRCULATION_TIME = [1, 0.082, 1.88, 0.24, 11.86, 0.62, 29.46]
EXALTATION = [10, 33, 298, 165, 95, 357, 200]
SAPTA_VARGA_NUMBERS = [1, 2, 3, 7, 9, 12, 30]
NAISARGIKA_BASE = [0, 1, 4, 2, 5, 3, 6]

PLANET_OWN_SIGNS = {
    0: [5], 1: [4], 2: [1, 8], 3: [3, 6], 4: [9, 12], 5: [2, 7], 6: [10, 11]
}
PLANET_EXALTATION_SIGNS = {
    0: 1, 1: 2, 2: 10, 3: 6, 4: 4, 5: 12, 6: 7
}
PLANET_FRIENDS = {
    0: ([1,4,5], [3,6], [2]), 1: ([0,4,5], [2,3,6], []), 2: ([0,3,4], [1,5,6], []),
    3: ([0,2,4,5,6], [1], []), 4: ([0,1,2,3], [5,6], []), 5: ([0,1,3,4,6], [2], []),
    6: ([2,4,5], [0,1,3], [])
}
HORA_LORDS = [OSATURN, OJUPITER, OMARS, OSUN, OVENUS, OMERCURY, OMOON]
REV_HORA_LORDS = [OVENUS, OSATURN, OMERCURY, OJUPITER, OMOON, OMARS, OSUN]

def red_deg(angle):
    print(f"red_deg: angle={angle}, type={type(angle)}")
    return angle % 360

def a_red(val, mod):
    print(f"a_red: val={val}, type={type(val)}, mod={mod}, type={type(mod)}")
    return val % mod

def planet_distance(lon1, lon2):
    print(f"planet_distance: lon1={lon1}, type={type(lon1)}, lon2={lon2}, type={type(lon2)}")
    diff = abs(lon1 - lon2)
    return min(diff, 360 - diff)

def get_rasi(longitude):
    print(f"get_rasi: longitude={longitude}, type={type(longitude)}")
    return int(longitude // 30) + 1

def get_graha_drishti_value(planet, rasidiff):
    print(f"get_graha_drishti_value: planet={planet}, type={type(planet)}, rasidiff={rasidiff}, type={type(rasidiff)}")
    if rasidiff == 7: return 1.0
    if planet == OMARS and rasidiff == 4: return 1.0
    if planet == OJUPITER and rasidiff == 5: return 1.0
    if planet == OSATURN and rasidiff == 3: return 1.0
    if planet == OMARS and rasidiff == 8: return 0.75
    if planet == OJUPITER and rasidiff == 9: return 0.5
    if planet == OSATURN and rasidiff == 10: return 0.25
    return 0.0

def get_lord(sign):
    print(f"get_lord: sign={sign}, type={type(sign)}")
    if sign == 1 or sign == 8: return 2
    if sign == 2 or sign == 7: return 5
    if sign == 3 or sign == 6: return 3
    if sign == 4: return 1
    if sign == 5: return 0
    if sign == 9 or sign == 12: return 4
    if sign == 10 or sign == 11: return 6
    return None

def get_natural_friendship(planet, lord):
    print(f"get_natural_friendship: planet={planet}, type={type(planet)}, lord={lord}, type={type(lord)}")
    if planet == lord: return "own"
    friends, neutrals, enemies = PLANET_FRIENDS.get(planet, ([],[],[]))
    if lord in friends: return "friend"
    if lord in neutrals: return "neutral"
    return "enemy"

def get_temporary_friendship(planet, sign, chart):
    print(f"get_temporary_friendship: planet={planet}, type={type(planet)}, sign={sign}, type={type(sign)}")
    lord_rasi = get_lord(sign)
    if planet == lord_rasi: return "own"
    return get_natural_friendship(planet, lord_rasi)

def get_sapta_vargaja_bala(planet, sign, chart):
    print(f"get_sapta_vargaja_bala: planet={planet}, type={type(planet)}, sign={sign}, type={type(sign)}")
    if sign is None: return 0
    if sign == PLANET_EXALTATION_SIGNS.get(planet): return 60
    if sign in PLANET_OWN_SIGNS.get(planet, []): return 45
    nat_friend = get_natural_friendship(planet, get_lord(sign))
    temp_friend = get_temporary_friendship(planet, sign, chart)
    if nat_friend == "friend" and temp_friend == "friend": return 30
    if (nat_friend == "friend" and temp_friend == "neutral") or (nat_friend == "neutral" and temp_friend == "friend"): return 22.5
    if nat_friend == "neutral" and temp_friend == "neutral": return 15
    if (nat_friend == "enemy" and temp_friend == "neutral") or (nat_friend == "neutral" and temp_friend == "enemy"): return 7.5
    if nat_friend == "enemy" and temp_friend == "enemy": return 0
    return 15

def get_true_obliquity(jd):
    print(f"get_true_obliquity: jd={jd}, type={type(jd)}")
    return swe.calc(jd, swe.ECL_NUT)[0]

def get_weekday(jd):
    print(f"get_weekday: jd={jd}, type={type(jd)}")
    result = int((jd + 1.5) % 7)
    print(f"get_weekday: result={result}, type={type(result)}")
    return result

def calc_next_solar_event(event_type, jd, lat, lon):
    print(f"calc_next_solar_event: event_type={event_type}, type={type(event_type)}, jd={jd}, type={type(jd)}, lat={lat}, type={type(lat)}, lon={lon}, type={type(lon)}")
    flag = swe.CALC_RISE | swe.BIT_DISC_CENTER
    try:
        if event_type == 0:
            rs = swe.rise_trans(jd, swe.SUN, lon, lat, 0, flag)[1][0]
        else:
            rs = swe.rise_trans(jd, swe.SUN, lon, lat, 0, swe.CALC_SET | swe.BIT_DISC_CENTER)[1][0]
        print(f"calc_next_solar_event: rs={rs}, type={type(rs)}")
        return rs
    except Exception as e:
        print(f"calc_next_solar_event: error={str(e)}")
        raise ValueError(f"Error in calc_next_solar_event: {str(e)}")

def get_hora_lords(jd, lat, lon):
    print(f"get_hora_lords: jd={jd}, type={type(jd)}, lat={lat}, type={type(lat)}, lon={lon}, type={type(lon)}")
    sunrise = calc_next_solar_event(0, jd, lat, lon)
    print(f"get_hora_lords: sunrise={sunrise}, type={type(sunrise)}")
    sunset = calc_next_solar_event(1, sunrise, lat, lon)
    print(f"get_hora_lords: sunset={sunset}, type={type(sunset)}")
    sunrise_next = calc_next_solar_event(0, sunset, lat, lon)
    print(f"get_hora_lords: sunrise_next={sunrise_next}, type={type(sunrise_next)}")
    weekday = get_weekday(sunrise)
    print(f"get_hora_lords: weekday={weekday}, type={type(weekday)}")
    lordseq = HORA_LORDS
    rev_lordseq = REV_HORA_LORDS
    index = rev_lordseq[int(weekday)] % 7
    print(f"get_hora_lords: index={index}, type={type(index)}")
    dina_lord = lordseq[index]
    print(f"get_hora_lords: dina_lord={dina_lord}, type={type(dina_lord)}")
    hora_lord = []
    for i in range(24):
        hora_lord.append(lordseq[(rev_lordseq[weekday] + i) % 7])
    daydur = sunset - sunrise
    nightdur = sunrise_next - sunset
    hora_start = [sunrise + i * (daydur / 12) for i in range(12)] + [sunset + i * (nightdur / 12) for i in range(13)]
    y, m, d, _ = swe.revjul(sunrise, swe.GREG_CAL)
    weekday_year = get_weekday(swe.julday(y, 1, 1, 12, swe.GREG_CAL))
    print(f"get_hora_lords: weekday_year={weekday_year}, type={type(weekday_year)}")
    varsha_lord = lordseq[rev_lordseq[weekday_year] % 7]
    print(f"get_hora_lords: varsha_lord={varsha_lord}, type={type(varsha_lord)}")
    weekday_month = get_weekday(swe.julday(y, m, 1, 12, swe.GREG_CAL))
    print(f"get_hora_lords: weekday_month={weekday_month}, type={type(weekday_month)}")
    masa_lord = lordseq[rev_lordseq[weekday_month] % 7]
    print(f"get_hora_lords: masa_lord={masa_lord}, type={type(masa_lord)}")
    return {
        "dina_lord": dina_lord,
        "varsha_lord": varsha_lord,
        "masa_lord": masa_lord,
        "hora_lord": hora_lord,
        "hora_start": hora_start
    }

class HoroscopeData:
    def __init__(self, get_chart_data_fn, date, hour, minute, second, lat, lon, tz):
        print(f"HoroscopeData.__init__: hour={hour}, type={type(hour)}, minute={minute}, type={type(minute)}, second={second}, type={type(second)}, lat={lat}, type={type(lat)}, lon={lon}, type={type(lon)}, tz={tz}, type={type(tz)}")
        self.get_chart_data_fn = get_chart_data_fn
        self.date = date
        self.hour = hour
        self.minute = minute
        self.second = second
        self.lat = lat
        self.lon = lon
        self.tz = tz

    def get_vedic_longitude(self, planet):
        print(f"get_vedic_longitude: planet={planet}, type={type(planet)}")
        return self.get_chart_data_fn(planet)["vedic_longitude"]

    def get_tropical_longitude(self, planet):
        print(f"get_tropical_longitude: planet={planet}, type={type(planet)}")
        return self.get_chart_data_fn(planet)["tropical_longitude"]

    def get_latitude(self, planet):
        print(f"get_latitude: planet={planet}, type={type(planet)}")
        return self.get_chart_data_fn(planet)["latitude"]

    def get_speed(self, planet):
        print(f"get_speed: planet={planet}, type={type(planet)}")
        return self.get_chart_data_fn(planet)["speed"]

    def get_varga_data(self, planet, varga):
        print(f"get_varga_data: planet={planet}, type={type(planet)}, varga={varga}, type={type(varga)}")
        planets_in_varga = compute_planets_in_varga(
            self.date.year, self.date.month, self.date.day,
            self.hour, self.minute, self.second,
            self.lat, self.lon, self.tz, varga
        )
        planet_name = PLANET_INDEX_TO_NAME[planet]
        print(f"get_varga_data: planet_name={planet_name}, type={type(planet_name)}")
        sign_num = None
        for sign, planets in planets_in_varga.items():
            print(f"get_varga_data: sign={sign}, type={type(sign)}, planets={planets}")
            if planet_name in planets:
                sign_num = sign
                break
        return get_sapta_vargaja_bala(planet, sign_num, self)

    def get_house4_longitude(self, longitude):
        print(f"get_house4_longitude: longitude={longitude}, type={type(longitude)}")
        return int(longitude / 30)

    def is_benefic(self, planet):
        print(f"is_benefic: planet={planet}, type={type(planet)}")
        if planet == OMOON:
            sun = self.get_vedic_longitude(OSUN)
            moon = self.get_vedic_longitude(OMOON)
            angle = red_deg(moon - sun)
            return angle < 180
        elif planet == OMERCURY:
            mpos = get_rasi(self.get_vedic_longitude(OMERCURY))
            if get_rasi(self.get_vedic_longitude(OSUN)) == mpos: return False
            if get_rasi(self.get_vedic_longitude(OMARS)) == mpos: return False
            if get_rasi(self.get_vedic_longitude(OSATURN)) == mpos: return False
            moon_benefic = self.is_benefic(OMOON)
            if not moon_benefic and get_rasi(self.get_vedic_longitude(OMOON)) == mpos: return False
            return True
        return planet in [OJUPITER, OVENUS]

    def get_jd(self):
        return self.get_chart_data_fn("meta")["jd"]

    def get_sunrise(self):
        return self.get_chart_data_fn("meta").get("sunrise", 0)

    def get_sunset(self):
        return self.get_chart_data_fn("meta").get("sunset", 0)

    def get_day_birth(self):
        return self.get_chart_data_fn("meta").get("day_birth", True)

    def get_location(self):
        return self.get_chart_data_fn("meta")["location"]

    def get_local_mean_time(self):
        return self.get_chart_data_fn("meta")["lmt"]

    def is_retrograde(self, planet):
        print(f"is_retrograde: planet={planet}, type={type(planet)}")
        return self.get_chart_data_fn(planet)["speed"] < 0

class ShadbalaCalculator:
    def __init__(self, horoscope: HoroscopeData):
        self.h = horoscope
        self.shadbala = [0.0] * 7
        self.sthaanabala = [0.0] * 7
        self.uchchabala = [0.0] * 7
        self.saptavargajabala = [0.0] * 7
        self.ojhajugmabala = [0.0] * 7
        self.kendradibala = [0.0] * 7
        self.drekkanabala = [0.0] * 7
        self.digbala = [0.0] * 7
        self.kalabala = [0.0] * 7
        self.nathonathabala = [0.0] * 7
        self.pakshabala = [0.0] * 7
        self.tribhagabala = [0.0] * 7
        self.varshamasadinahorabala = [0.0] * 7
        self.ayanabala = [0.0] * 7
        self.yudhdhabala = [0.0] * 7
        self.naisargikabala = [0.0] * 7
        self.cheshtabala = [0.0] * 7
        self.drigbala = [0.0] * 7

    def update_all_balas(self):
        print("Starting update_all_balas")
        self._update_sthaana_bala()
        self._update_dig_bala()
        self._update_kala_bala()
        self._update_naisargika_bala()
        self._update_cheshta_bala()
        self._update_drig_bala()
        for i in PLANET_INDEXES:
            print(f"update_all_balas: i={i}, type={type(i)}")
            self.sthaanabala[i] = (
                self.uchchabala[i] + self.saptavargajabala[i] + self.ojhajugmabala[i] +
                self.kendradibala[i] + self.drekkanabala[i]
            )
            self.kalabala[i] = (
                self.nathonathabala[i] + self.pakshabala[i] + self.tribhagabala[i] +
                self.varshamasadinahorabala[i] + self.ayanabala[i] + self.yudhdhabala[i]
            )
            self.shadbala[i] = (
                self.sthaanabala[i] + self.digbala[i] + self.kalabala[i] +
                self.cheshtabala[i] + self.naisargikabala[i] + self.drigbala[i]
            )

    def _update_sthaana_bala(self):
        for i in PLANET_INDEXES:
            print(f"_update_sthaana_bala (uchchabala): i={i}, type={type(i)}")
            a = red_deg(EXALTATION[i] - self.h.get_vedic_longitude(i) - 180)
            if a > 180: a = 360 - a
            self.uchchabala[i] = a / 3

        for i in PLANET_INDEXES:
            print(f"_update_sthaana_bala (saptavargajabala): i={i}, type={type(i)}")
            total = 0
            for varga_num in SAPTA_VARGA_NUMBERS:
                print(f"_update_sthaana_bala: varga_num={varga_num}, type={type(varga_num)}")
                total += self.h.get_varga_data(i, varga_num)
            self.saptavargajabala[i] = total

        for i in PLANET_INDEXES:
            print(f"_update_sthaana_bala (ojhajugmabala): i={i}, type={type(i)}")
            rasi = get_rasi(self.h.get_vedic_longitude(i))
            navamsa = get_rasi(self.h.get_vedic_longitude(i) * 9)
            if i in [OVENUS, OMOON]:
                if rasi % 2 == 1: self.ojhajugmabala[i] += 15
                if navamsa % 2 == 1: self.ojhajugmabala[i] += 15
            else:
                if rasi % 2 == 0: self.ojhajugmabala[i] += 15
                if navamsa % 2 == 0: self.ojhajugmabala[i] += 15

        for i in PLANET_INDEXES:
            print(f"_update_sthaana_bala (kendradibala): i={i}, type={type(i)}")
            bhava = get_rasi(self.h.get_vedic_longitude(i)) % 3
            if bhava == 0: self.kendradibala[i] = 60
            elif bhava == 1: self.kendradibala[i] = 30
            else: self.kendradibala[i] = 15

        for i in PLANET_INDEXES:
            print(f"_update_sthaana_bala (drekkanabala): i={i}, type={type(i)}")
            a = (self.h.get_vedic_longitude(i) % 30) / 10.0
            drekkana = int(a)
            if i in [OSUN, OMARS, OJUPITER]:
                if drekkana == 0: self.drekkanabala[i] = 15
            elif i in [OVENUS, OMOON]:
                if drekkana == 1: self.drekkanabala[i] = 15
            elif i in [OSATURN, OMERCURY]:
                if drekkana == 2: self.drekkanabala[i] = 15

    def _update_dig_bala(self):
        for i in PLANET_INDEXES:
            print(f"_update_dig_bala: i={i}, type={type(i)}")
            house = self.h.get_house4_longitude(self.h.get_vedic_longitude(i))
            weakest = {OSUN: 4, OMARS: 4, OMERCURY: 7, OJUPITER: 7, OMOON: 10, OVENUS: 10, OSATURN: 1}[i]
            bala = a_red(house - weakest, 12)
            if bala > 6: bala = 12 - bala
            self.digbala[i] = bala * 10

    def _update_kala_bala(self):
        natabala = self.h.get_local_mean_time()
        print(f"_update_kala_bala: natabala={natabala}, type={type(natabala)}")
        if natabala > 12: natabala = 24 - natabala
        natabala *= 5
        self.nathonathabala[OMERCURY] = 60
        for i in [OMOON, OMARS, OSATURN]:
            print(f"_update_kala_bala (nathonathabala malefic): i={i}, type={type(i)}")
            self.nathonathabala[i] = natabala
        for i in [OSUN, OJUPITER, OVENUS]:
            print(f"_update_kala_bala (nathonathabala benefic): i={i}, type={type(i)}")
            self.nathonathabala[i] = 60 - natabala

        paskha_value = planet_distance(self.h.get_vedic_longitude(OSUN), self.h.get_vedic_longitude(OMOON)) / 3
        self.pakshabala[OSUN] = 60 - paskha_value
        self.pakshabala[OMOON] = paskha_value if self.h.is_benefic(OMOON) else 60 - paskha_value
        self.pakshabala[OMARS] = 60 - paskha_value
        self.pakshabala[OMERCURY] = paskha_value if self.h.is_benefic(OMERCURY) else 60 - paskha_value
        self.pakshabala[OJUPITER] = paskha_value
        self.pakshabala[OVENUS] = paskha_value
        self.pakshabala[OSATURN] = 60 - paskha_value

        sunrise = self.h.get_sunrise()
        sunset = self.h.get_sunset()
        jd = self.h.get_jd()
        daybirth = self.h.get_day_birth()
        print(f"_update_kala_bala: sunrise={sunrise}, type={type(sunrise)}, sunset={sunset}, type={type(sunset)}, jd={jd}, type={type(jd)}, daybirth={daybirth}, type={type(daybirth)}")
        if sunrise and sunset:
            if daybirth:
                d = (jd - sunrise) / (sunset - sunrise)
                daypart = int(d * 3)
                print(f"_update_kala_bala (tribhagabala day): daypart={daypart}, type={type(daypart)}")
                if daypart == 0: self.tribhagabala[OMERCURY] = 60
                elif daypart == 1: self.tribhagabala[OSUN] = 60
                elif daypart == 2: self.tribhagabala[OSATURN] = 60
            else:
                d = (jd - sunset) / (sunrise - sunset)
                nightpart = int(d * 3)
                print(f"_update_kala_bala (tribhagabala night): nightpart={nightpart}, type={type(nightpart)}")
                if nightpart == 0: self.tribhagabala[OMOON] = 60
                elif nightpart == 1: self.tribhagabala[OVENUS] = 60
                elif nightpart == 2: self.tribhagabala[OMARS] = 60

        hora_data = get_hora_lords(jd, self.h.lat, self.h.lon)
        print(f"_update_kala_bala: hora_data varsha_lord={hora_data['varsha_lord']}, type={type(hora_data['varsha_lord'])}, masa_lord={hora_data['masa_lord']}, type={type(hora_data['masa_lord'])}, dina_lord={hora_data['dina_lord']}, type={type(hora_data['dina_lord'])}")
        self.varshamasadinahorabala[hora_data["varsha_lord"]] += 15
        self.varshamasadinahorabala[hora_data["masa_lord"]] += 30
        self.varshamasadinahorabala[hora_data["dina_lord"]] += 45
        current_hora_lord = hora_data["hora_lord"][0]
        for hidx, hstart in enumerate(hora_data["hora_start"][:-1]):
            print(f"_update_kala_bala: hidx={hidx}, type={type(hidx)}, hstart={hstart}, type={type(hstart)}")
            if jd >= hstart and jd < hora_data["hora_start"][hidx+1]:
                current_hora_lord = hora_data["hora_lord"][hidx]
                break
        print(f"_update_kala_bala: current_hora_lord={current_hora_lord}, type={type(current_hora_lord)}")
        self.varshamasadinahorabala[current_hora_lord] += 60

        eps = get_true_obliquity(self.h.get_jd())
        for i in PLANET_INDEXES:
            print(f"_update_kala_bala (ayanabala): i={i}, type={type(i)}")
            tlen = self.h.get_tropical_longitude(i)
            lat = self.h.get_latitude(i)
            kranti = lat + eps * math.sin(math.radians(tlen))
            if i == OMERCURY:
                self.ayanabala[i] = eps + abs(kranti)
            elif i in [OMOON, OSATURN]:
                self.ayanabala[i] = eps - kranti
            else:
                self.ayanabala[i] = eps + kranti
            self.ayanabala[i] *= 1.2793
            self.ayanabala[i] = max(self.ayanabala[i], 0)

        for i in PLANET_INDEXES:
            print(f"_update_kala_bala (yudhdhabala): i={i}, type={type(i)}")
            self.yudhdhabala[i] = 0

    def _update_naisargika_bala(self):
        for i in PLANET_INDEXES:
            print(f"_update_naisargika_bala: i={i}, type={type(i)}")
            self.naisargikabala[i] = (7 - NAISARGIKA_BASE[i]) * 60.0 / 7.0

    def _update_cheshta_bala(self):
        for i in PLANET_INDEXES:
            print(f"_update_cheshta_bala: i={i}, type={type(i)}")
            if i == OSUN:
                self.cheshtabala[i] = self.ayanabala[i]
            elif i == OMOON:
                self.cheshtabala[i] = self.pakshabala[i]
            else:
                speed = self.h.get_speed(i)
                print(f"_update_cheshta_bala: speed={speed}, type={type(speed)}")
                avg = 1 / CIRCULATION_TIME[i]
                percentual_speed = 100 * speed / avg if avg != 0 else 0
                if speed > 0:
                    if abs(percentual_speed) < 10: self.cheshtabala[i] = 15
                    elif percentual_speed < 50: self.cheshtabala[i] = 15
                    elif percentual_speed < 100: self.cheshtabala[i] = 30
                    elif percentual_speed < 150: self.cheshtabala[i] = 7.5
                    else: self.cheshtabala[i] = 45
                else:
                    self.cheshtabala[i] = 60  # Vakra

    def _update_drig_bala(self):
        for aspected in PLANET_INDEXES:
            print(f"_update_drig_bala: aspected={aspected}, type={type(aspected)}")
            total = 0
            for aspecting in PLANET_INDEXES:
                print(f"_update_drig_bala: aspecting={aspecting}, type={type(aspecting)}")
                if aspected == aspecting: continue
                rasidiff = a_red(get_rasi(self.h.get_vedic_longitude(aspected)) - get_rasi(self.h.get_vedic_longitude(aspecting)), 12)
                val = 60.0 * get_graha_drishti_value(aspecting, rasidiff)
                if val > 0:
                    malefic = (aspecting == OSUN or
                               (aspecting == OMOON and not self.h.is_benefic(OMOON)) or
                               aspecting == OMARS or
                               (aspecting == OMERCURY and not self.h.is_benefic(OMERCURY)) or
                               aspecting == OSATURN)
                    if malefic: val -= 15
                    else: val += 15
                total += val
            self.drigbala[aspected] = total

    def get_result(self):
        result = {}
        names = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
        for i, name in enumerate(names):
            print(f"get_result: i={i}, type={type(i)}, name={name}")
            result[name] = {
                "Sthana": self.sthaanabala[i],
                "Dig": self.digbala[i],
                "Kala": self.kalabala[i],
                "Cheshta": self.cheshtabala[i],
                "Naisargika": self.naisargikabala[i],
                "Drik": self.drigbala[i],
                "Total": self.shadbala[i],
                "Required": REQUIRED_SHADBALA[i],
                "Percent": round(self.shadbala[i] * 100.0 / REQUIRED_SHADBALA[i], 2)
            }
        return result

def compute_shadbala(jd, lat, lon, tz, get_chart_data_fn, date=None, hour=0, minute=0, second=0):
    print(f"compute_shadbala: jd={jd}, type={type(jd)}, lat={lat}, type={type(lat)}, lon={lon}, type={type(lon)}, tz={tz}, type={type(tz)}, hour={hour}, type={type(hour)}, minute={minute}, type={type(minute)}, second={second}, type={type(second)}")
    h = HoroscopeData(get_chart_data_fn, date, hour, minute, second, lat, lon, tz)
    c = ShadbalaCalculator(h)
    c.update_all_balas()
    return c.get_result()


# ui usage
 # st.markdown("## 🔯 శడ్బల పట్టిక (Shadbala Table)")

    # def get_chart_data(planet_name):
    #     # Handle metadata request
    #     if planet_name == "meta":
    #         return {
    #             "jd": jd_birth,
    #             "sunrise": panchang.get("sunrise", 0),
    #             "sunset": panchang.get("sunset", 0),
    #             "day_birth": True,
    #             "lmt": (jd_birth - int(jd_birth)) * 24,
    #             "location": (lat, lon)
    #         }

    #     # Define planet index to name mapping
    #     planet_names = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]

    #     # Convert planet_name to integer if it's a number
    #     if isinstance(planet_name, (int, float)):
    #         idx = int(planet_name)  # Explicitly convert to int
    #         if 0 <= idx < len(planet_names):
    #             planet_str = planet_names[idx]
    #         else:
    #             raise ValueError(f"Invalid planet index: {planet_name}")
    #     else:
    #         planet_str = planet_name

    #     # Fetch matching planet data
    #     for p in planetary_info:
    #         if p["planet"] == planet_str:
    #             return {
    #                 "vedic_longitude": float(p["degrees"]),
    #                 "tropical_longitude": float(p["degrees"]),
    #                 "latitude": 0.0,
    #                 "speed": 1.0 if p["retrogration"] == "No" else -1.0,  # Use retrogration info
    #                 "varga": {}  # Not used in Shadbala
    #             }

    #     # Fallback for unmatched planets
    #     raise ValueError(f"Planet {planet_str} not found in planetary_info")

    # # Compute and display the Shadbala table
    # try:
    #     shadbala_data = compute_shadbala(jd_birth, lat, lon, tz, get_chart_data, date, hour, minute, second)

    #     # Convert result to DataFrame
    #     shadbala_df = pd.DataFrame([
    #         {
    #             "Planet": planet,
    #             "Sthana": round(data["Sthana"], 2),
    #             "Dig": round(data["Dig"], 2),
    #             "Kala": round(data["Kala"], 2),
    #             "Cheshta": round(data["Cheshtabala"], 2) if "Cheshtabala" in data else round(data["Cheshta"], 2),
    #             "Naisargika": round(data["Naisargika"], 2),
    #             "Drik": round(data["Drik"], 2),
    #             "Total": round(data["Total"], 2),
    #             "Required": round(data["Required"], 2),
    #             "Percent": f'{data["Percent"]}%'
    #         }
    #         for planet, data in shadbala_data.items()
    #     ])

    #     st.dataframe(shadbala_df)

    #     # Plotting
    #     st.markdown("### 📊 Shadbala Total vs Required (Virupa Strength)")
    #     plt.figure(figsize=(10, 5))
    #     sns.barplot(data=shadbala_df, x="Planet", y="Total", color='green', label="Total Bala")
    #     sns.barplot(data=shadbala_df, x="Planet", y="Required", color='red', alpha=0.5, label="Required Bala")
    #     plt.ylabel("Virupas")
    #     plt.title("Shadbala Total vs Required")
    #     plt.legend()
    #     st.pyplot(plt.gcf())

    # except Exception as e:
    #     st.warning("Shadbala not computed: " + str(e))



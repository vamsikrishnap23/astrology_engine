# ashtakavarga.py

OSUN, OMOON, OMERCURY, OVENUS, OMARS, OJUPITER, OSATURN, OASCENDANT = range(8)
R_ARIES, R_TAURUS, R_GEMINI, R_CANCER, R_LEO, R_VIRGO, R_LIBRA, R_SCORPIO, R_SAGITTARIUS, R_CAPRICORN, R_AQUARIUS, R_PISCES = range(12)

REKHA, TRIKONA, EKADHI = 0, 1, 2
GRAHAPINDA, RASIPINDA, YOGAPINDA = 0, 1, 2

def red12(x):
    return x % 12

def Min(a, b):
    return min(a, b)

REKHA_MAP = [
    # Sun
    [
        [1, 1, 0, 1, 0, 0, 1, 1, 1, 1, 1, 0], # Sun
        [0, 0, 1, 0, 0, 1, 0, 0, 0, 1, 1, 0], # Moon
        [0, 0, 1, 0, 1, 1, 0, 0, 1, 1, 1, 1], # Mercury
        [0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 1], # Venus
        [1, 1, 0, 1, 0, 0, 1, 1, 1, 1, 1, 0], # Mars
        [0, 0, 0, 0, 1, 1, 0, 0, 1, 0, 1, 0], # Jupiter
        [1, 1, 0, 1, 0, 0, 1, 1, 1, 1, 1, 0], # Saturn
        [0, 0, 1, 1, 0, 1, 0, 0, 0, 1, 1, 1], # Ascendant
    ],
    # Moon
    [
        [0, 0, 1, 0, 0, 1, 1, 1, 0, 1, 1, 0], # Sun
        [1, 0, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0], # Moon
        [1, 0, 1, 1, 1, 0, 1, 1, 0, 1, 1, 0], # Mercury
        [0, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0], # Venus
        [0, 1, 1, 0, 1, 1, 0, 0, 1, 1, 1, 0], # Mars
        [1, 1, 0, 1, 0, 0, 1, 1, 0, 1, 1, 0], # Jupiter
        [0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 1, 0], # Saturn
        [0, 0, 1, 0, 0, 1, 0, 0, 0, 1, 1, 0], # Ascendant
    ],
    # Mercury
    [
        [0, 0, 0, 0, 1, 1, 0, 0, 1, 0, 1, 1], # Sun
        [0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 0], # Moon
        [1, 0, 1, 0, 1, 1, 0, 0, 1, 1, 1, 1], # Mercury
        [1, 1, 1, 1, 1, 0, 0, 1, 1, 0, 1, 0], # Venus
        [1, 1, 0, 1, 0, 0, 1, 1, 1, 1, 1, 0], # Mars
        [0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 1, 1], # Jupiter
        [1, 1, 0, 1, 0, 0, 1, 1, 1, 1, 1, 0], # Saturn
        [1, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 0], # Ascendant
    ],
    # Venus
    [
        [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1], # Sun
        [1, 1, 1, 1, 1, 0, 0, 1, 1, 0, 1, 1], # Moon
        [0, 0, 1, 0, 1, 1, 0, 0, 1, 0, 1, 0], # Mercury
        [1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 0], # Venus
        [0, 0, 1, 1, 0, 1, 0, 0, 1, 0, 1, 1], # Mars
        [0, 0, 0, 0, 1, 0, 0, 1, 1, 1, 1, 0], # Jupiter
        [0, 0, 1, 1, 1, 0, 0, 1, 1, 1, 1, 0], # Saturn
        [1, 1, 1, 1, 1, 0, 0, 1, 1, 0, 1, 0], # Ascendant
    ],
    # Mars
    [
        [0, 0, 1, 0, 1, 1, 0, 0, 0, 1, 1, 0], # Sun
        [0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0], # Moon
        [0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 1, 0], # Mercury
        [0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 1, 1], # Venus
        [1, 1, 0, 1, 0, 0, 1, 1, 0, 1, 1, 0], # Mars
        [0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 1], # Jupiter
        [1, 0, 0, 1, 0, 0, 1, 1, 1, 1, 1, 0], # Saturn
        [1, 0, 1, 0, 0, 1, 0, 0, 0, 1, 1, 0], # Ascendant
    ],
    # Jupiter
    [
        [1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 0], # Sun
        [0, 1, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0], # Moon
        [1, 1, 0, 1, 1, 1, 0, 0, 1, 1, 1, 0], # Mercury
        [0, 1, 0, 0, 1, 1, 0, 0, 1, 1, 1, 0], # Venus
        [1, 1, 0, 1, 0, 0, 1, 1, 0, 1, 1, 0], # Mars
        [1, 1, 1, 1, 0, 0, 1, 1, 0, 1, 1, 0], # Jupiter
        [0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 0, 1], # Saturn
        [1, 1, 0, 1, 1, 1, 1, 0, 1, 1, 1, 0], # Ascendant
    ],
    # Saturn
    [
        [1, 1, 0, 1, 0, 0, 1, 1, 0, 1, 1, 0], # Sun
        [0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0], # Moon
        [0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 1, 1], # Mercury
        [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 1], # Venus
        [1, 1, 0, 1, 0, 0, 1, 1, 0, 1, 1, 0], # Mars
        [0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 1], # Jupiter
        [1, 0, 0, 1, 0, 0, 1, 1, 1, 1, 1, 0], # Saturn
        [1, 0, 1, 0, 0, 1, 0, 0, 0, 1, 1, 0], # Ascendant
    ],
    # Ascendant
    [
        [1, 1, 0, 1, 0, 0, 1, 1, 1, 1, 1, 0], # Sun
        [0, 0, 1, 0, 0, 1, 0, 0, 0, 1, 1, 0], # Moon
        [1, 1, 0, 1, 0, 0, 1, 1, 1, 1, 1, 0], # Mercury
        [1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 0], # Venus
        [1, 0, 0, 1, 0, 0, 1, 1, 1, 1, 1, 0], # Mars
        [1, 1, 0, 1, 0, 0, 1, 1, 1, 1, 1, 0], # Jupiter
        [0, 0, 1, 1, 0, 1, 0, 0, 0, 1, 1, 1], # Saturn
        [1, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 0], # Ascendant
    ],
]

class Ashtakavarga:
    def __init__(self, get_rasi_func):
        self.get_rasi = get_rasi_func
        self.rekha = [[0]*12 for _ in range(8)]
        self.trikona = [[0]*12 for _ in range(8)]
        self.ekadhi = [[0]*12 for _ in range(8)]
        self.sarvaRekha = [0]*12
        self.sarvaTrikona = [0]*12
        self.sarvaEkadhi = [0]*12
        self.psarvaRekha = [0]*8
        self.psarvaTrikona = [0]*8
        self.psarvaEkadhi = [0]*8
        self.grahaPinda = [0]*8
        self.rasiPinda = [0]*8
        self.yogaPinda = [0]*8
        self.planetNumber = [0]*12

    def update(self):
        for i in range(8):
            for j in range(12):
                self.rekha[i][j] = self.trikona[i][j] = self.ekadhi[i][j] = 0
        for j in range(12):
            self.planetNumber[j] = 0
        self.calcRekha()
        self.calcTrikonaShodana()
        self.calcEkadhipatyaShodana()
        self.calcSarva()
        self.calcPinda()

    def getSingleRekha(self, i, j, k):
        return REKHA_MAP[i][j][k]

    def calcRekha(self):
        for i in range(8):
            for j in range(8):
                p2_rasi = self.get_rasi(j if j < 7 else OASCENDANT)
                for k in range(12):
                    house = red12(p2_rasi + k)
                    if self.getSingleRekha(i, j, k):
                        self.rekha[i][house] += 1

    def calcTrikonaShodana(self):
        for i in range(8):
            for j in range(4):
                minrekha = min(self.rekha[i][j], self.rekha[i][j+4], self.rekha[i][j+8])
                for k in range(3):
                    self.trikona[i][j + 4*k] = self.rekha[i][j + 4*k] - minrekha

    def calcEkadhipatyaPair(self, rasi1, rasi2):
        for p in range(8):
            if not self.planetNumber[rasi1] and not self.planetNumber[rasi2] and self.trikona[p][rasi1] != self.trikona[p][rasi2]:
                val = Min(self.trikona[p][rasi1], self.trikona[p][rasi2])
                self.ekadhi[p][rasi1] = self.ekadhi[p][rasi2] = val
            elif self.planetNumber[rasi1] and self.planetNumber[rasi2]:
                pass
            elif self.planetNumber[rasi1] and not self.planetNumber[rasi2] and self.trikona[p][rasi1] < self.trikona[p][rasi2]:
                self.ekadhi[p][rasi2] -= self.trikona[p][rasi1]
            elif self.planetNumber[rasi2] and not self.planetNumber[rasi1] and self.trikona[p][rasi2] < self.trikona[p][rasi1]:
                self.ekadhi[p][rasi1] -= self.trikona[p][rasi2]
            elif self.planetNumber[rasi1] and not self.planetNumber[rasi2] and self.trikona[p][rasi1] > self.trikona[p][rasi2]:
                self.ekadhi[p][rasi2] = 0
            elif self.planetNumber[rasi2] and not self.planetNumber[rasi1] and self.trikona[p][rasi2] > self.trikona[p][rasi1]:
                self.ekadhi[p][rasi1] = 0
            elif not self.planetNumber[rasi1] and not self.planetNumber[rasi2] and self.trikona[p][rasi1] == self.trikona[p][rasi2]:
                self.ekadhi[p][rasi1] = self.ekadhi[p][rasi2] = 0
            elif self.planetNumber[rasi1] and not self.planetNumber[rasi2]:
                self.ekadhi[p][rasi2] = 0
            elif self.planetNumber[rasi2] and not self.planetNumber[rasi1]:
                self.ekadhi[p][rasi1] = 0

    def calcEkadhipatyaShodana(self):
        for i in range(7):
            rasi = self.get_rasi(i)
            self.planetNumber[rasi] += 1
        for i in range(8):
            for j in range(12):
                self.ekadhi[i][j] = self.trikona[i][j]
        self.calcEkadhipatyaPair(R_ARIES, R_SCORPIO)
        self.calcEkadhipatyaPair(R_TAURUS, R_LIBRA)
        self.calcEkadhipatyaPair(R_GEMINI, R_VIRGO)
        self.calcEkadhipatyaPair(R_SAGITTARIUS, R_PISCES)
        self.calcEkadhipatyaPair(R_CAPRICORN, R_AQUARIUS)

    def calcSarva(self):
        for i in range(12):
            self.sarvaRekha[i] = self.sarvaTrikona[i] = self.sarvaEkadhi[i] = 0
        for i in range(8):
            self.psarvaRekha[i] = self.psarvaTrikona[i] = self.psarvaEkadhi[i] = 0
        for i in range(12):
            for j in range(8):
                self.sarvaRekha[i] += self.rekha[j][i]
                self.sarvaTrikona[i] += self.trikona[j][i]
                self.sarvaEkadhi[i] += self.ekadhi[j][i]
                self.psarvaRekha[j] += self.rekha[j][i]
                self.psarvaTrikona[j] += self.trikona[j][i]
                self.psarvaEkadhi[j] += self.ekadhi[j][i]

    def calcPinda(self):
        k_rasimana = [7, 10, 8, 4, 10, 6, 7, 8, 9, 5, 11, 12]
        k_grahamana = [5, 5, 5, 7, 8, 10, 5]
        for planet in range(8):
            self.rasiPinda[planet] = self.grahaPinda[planet] = self.yogaPinda[planet] = 0
            for rasi in range(12):
                self.rasiPinda[planet] += self.ekadhi[planet][rasi] * k_rasimana[rasi]
                self.yogaPinda[planet] += self.ekadhi[planet][rasi]  # if sodhya pinda mode == 1
            for p in range(7):
                rasi = self.get_rasi(p)
                self.grahaPinda[planet] += self.ekadhi[planet][rasi] * k_grahamana[p]
            # If sodhya pinda mode != 1
            self.yogaPinda[planet] = self.grahaPinda[planet] + self.rasiPinda[planet]

    def getItem(self, typ, planet, rasi):
        if typ == REKHA:
            return self.rekha[planet][rasi]
        elif typ == TRIKONA:
            return self.trikona[planet][rasi]
        elif typ == EKADHI:
            return self.ekadhi[planet][rasi]
        else:
            raise ValueError("Unknown type")

    def getPinda(self, typ, i):
        if typ == GRAHAPINDA:
            return self.grahaPinda[i]
        elif typ == RASIPINDA:
            return self.rasiPinda[i]
        elif typ == YOGAPINDA:
            return self.yogaPinda[i]
        else:
            raise ValueError("Unknown pinda type")

    def getSarva(self, typ, rasi):
        if typ == REKHA:
            return self.sarvaRekha[rasi]
        elif typ == TRIKONA:
            return self.sarvaTrikona[rasi]
        elif typ == EKADHI:
            return self.sarvaEkadhi[rasi]
        else:
            raise ValueError("Unknown sarva type")

    def getPlanetSarva(self, typ, planet):
        if typ == REKHA:
            return self.psarvaRekha[planet]
        elif typ == TRIKONA:
            return self.psarvaTrikona[planet]
        elif typ == EKADHI:
            return self.psarvaEkadhi[planet]
        else:
            raise ValueError("Unknown planet sarva type")

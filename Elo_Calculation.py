def Elo_Cal(rating1, rating2, result):
    if (rating1 > 2400):
        k = 10
    elif rating1 <= 2400 and rating1 > 2000:
        k = 15
    elif rating1 <= 2000 and rating1 > 1600:
        k = 20
    else:
        k = 25
    Qa, Qb = 10 ** (rating1 / 400), 10 ** (rating2 / 400)
    Ea = Qa / (Qa + Qb)
    Eb = Qb / (Qa + Qb)
    if result is True:
        return rating1 + k * (1 - Ea)
    else:
        return rating1 + k * (0 - Eb)

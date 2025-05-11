def Elo_Cal(rating1, rating2, result):
    rate1 = float(rating1)
    if (rate1 > 2400):
        k = 10
    elif rate1 <= 2400 and rate1 > 2000:
        k = 15
    elif rate1 <= 2000 and rate1 > 1600:
        k = 20
    else:
        k = 25
    rate2 = float(rating2)
    Qa, Qb = 10 ** (rate1 / 400), 10 ** (rate2 / 400)
    Ea = Qa / (Qa + Qb)
    Eb = Qb / (Qa + Qb)
    if result == 0:
        return "{:.2f}".format(rate1 + k * (1 - Ea))

    else:
        return "{:.2f}".format(rate1 + k * (0 - Ea))
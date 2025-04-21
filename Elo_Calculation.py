def Elo_Calculation(rating1, rating2, result):
    def get_k(rating):
        if rating > 2400:
            return 10
        elif 2000 <= rating <= 2400:
            return 15
        elif 1600 <= rating < 2000:
            return 20
        return 25

    k1, k2 = get_k(rating1), get_k(rating2)
    Qa, Qb = 10 ** (rating1 / 400), 10 ** (rating2 / 400)
    Ea = Qa / (Qa + Qb)
    Eb = Qb / (Qa + Qb)
    if result is True:
        return rating1 + k1 * (1 - Ea)
    else:
        return rating2 + k2 * (0 - Eb)
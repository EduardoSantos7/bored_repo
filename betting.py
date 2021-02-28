from sympy import symbols, Eq, solve


def find_surebet(*odds):
    if not odds:
        return False

    sum_odds = sum([1 / odd for odd in odds])

    return sum_odds < 1


def beat_bookies(odds1, odds2, total_stake):
    x, y = symbols('x y')
    eq1 = Eq(x + y - total_stake, 0)  # total_stake = x + y
    eq2 = Eq((odds2*y) - odds1*x, 0)  # odds1*x = odds2*y
    stakes = solve((eq1, eq2), (x, y))
    total_investment = stakes[x] + stakes[y]
    profit1 = odds1*stakes[x] - total_stake
    profit2 = odds2*stakes[y] - total_stake
    benefit1 = f'{profit1 / total_investment * 100:.2f}%'
    benefit2 = f'{profit2 / total_investment * 100:.2f}%'
    dict_gabmling = {'Stake1': stakes[x], 'Stake2': stakes[y],
                     'Profit1': profit1, 'Profit2': profit2,
                     'Benefit1': benefit1, 'Benefit2': benefit2}
    return dict_gabmling


# print(beat_bookies([2, 2.1], 100))
print(find_surebet(1.53, 2.4))

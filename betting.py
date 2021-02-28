
def find_surebet(*odds):
    if not odds:
        return False

    sum_odds = sum([1 / odd for odd in odds])

    return sum_odds < 1

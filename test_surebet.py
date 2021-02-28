from  betting import find_surebet


def test_safebet():
    assert find_surebet(2, 2.1) == True
    assert find_surebet(2, 2) == False
    assert find_surebet(2, 2.1, 5) == False

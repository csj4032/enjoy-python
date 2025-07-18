def large_sequence():
    for i in range(100000000):
        yield i


def test_next():
    gen = large_sequence()
    assert next(gen) == 0
    assert next(gen) == 1
    assert next(gen) == 2

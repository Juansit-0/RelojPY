PI = 3.141592653589793


def sine(x):
    x = x % (2 * PI)
    if x > PI:
        x -= 2 * PI
    term = x
    total = x
    for n in range(1, 12):
        term *= -x * x / ((2 * n) * (2 * n + 1))
        total += term
    return total


def cosine(x):
    return sine(x + PI / 2)


def close(a, b):
    return abs(a - b) < 1e-9


def self_test():
    assert close(sine(0), 0)
    assert close(sine(PI / 2), 1)
    assert close(sine(PI), 0)
    assert close(sine(-PI / 2), -1)
    assert close(cosine(0), 1)
    assert close(cosine(PI), -1)
    assert close(sine(13 * PI / 6), 0.5)


if __name__ == "__main__":
    self_test()

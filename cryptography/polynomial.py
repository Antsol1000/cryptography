from itertools import zip_longest

import numpy as np


def gcd(a, b):
    r, r_ = b, a
    t, t_ = 0, 1

    while r_ != 0:
        q, _ = divmod(r, r_)
        r, r_ = r_, r - q * r_
        t, t_ = t_, t - q * t_

    return r, t


class Polynomial:

    def __init__(self, coefficients):
        self.coefficients = coefficients
        self._normalize()

    def _normalize(self):
        while len(self.coefficients) > 1 and self.coefficients[-1] == 0:
            self.coefficients.pop()

    def __getitem__(self, item):
        return self.coefficients[item]

    def __add__(self, other):
        coefficients = [a + b for a, b in zip_longest(self.coefficients, other.coefficients, fillvalue=0)]
        return Polynomial(coefficients)

    def __sub__(self, other):
        coefficients = [a - b for a, b in zip_longest(self.coefficients, other.coefficients, fillvalue=0)]
        return Polynomial(coefficients)

    def __mul__(self, other):
        if isinstance(other, int):
            coefficients = [c * other for c in self.coefficients]
        else:
            coefficients = np.convolve(self.coefficients, other.coefficients).tolist()
        return Polynomial(coefficients)

    def __mod__(self, other):
        coefficients = [c % other for c in self.coefficients]
        return Polynomial(coefficients)

    def __eq__(self, other):
        if isinstance(other, int):
            return self.coefficients == [other]
        return self.coefficients == other.coefficients

    def center(self, q):
        return Polynomial([t - q if t > q // 2 else t for t in self.coefficients])

    @property
    def degree(self):
        return len(self.coefficients)

    @staticmethod
    def divmod(a, b, mod):
        quotient = Polynomial([0])
        remainder = Polynomial(a.coefficients.copy())

        while remainder != 0 and remainder.degree >= b.degree:
            leading_coefficient = remainder[-1] * gcd(b[-1], mod)[1]
            term = Polynomial([0] * (remainder.degree - b.degree) + [leading_coefficient])
            quotient = (quotient + term) % mod
            remainder = (remainder - term * b) % mod

        return quotient, remainder

    @staticmethod
    def gcd(a, b, mod, debug=False):
        old_r, r = a % mod, b % mod
        old_t, t = Polynomial([0]), Polynomial([1])

        while r != 0:
            q, _ = Polynomial.divmod(old_r, r, mod)
            old_r, r = r, (old_r - q * r) % mod
            old_t, t = t, (old_t - q * t) % mod
            if debug:
                print("*" * 100)
                print(f"q: {q}")
                print(f"old_r, r: {old_r}, {r}")
                print(f"old_t, t: {old_t}, {t}")

        # if constant other than 1 scaling is needed
        if old_r != 1:
            scale = gcd(old_r[0], mod)[1]
            old_r = (old_r * scale) % mod
            old_t = (old_t * scale) % mod

        return old_r, old_t

    @staticmethod
    def invert_p_to_r(a, modulus, p, r):
        q = p
        b = Polynomial.gcd(modulus, a, p)[1]
        while q < p ** r:
            q = q ** 2
            b = (b * (Polynomial([2]) - (a * b))) % q

        return b

    def __repr__(self):
        r, pow = "", 0
        if all(c == 0 for c in self.coefficients):
            return "0"
        for n in self.coefficients:
            if n != 0:
                if r:
                    r += " + "
                if n != 1 or pow == 0:
                    r += f"{n}"
                if pow != 0:
                    r += "x"
                if pow > 1:
                    r += f"^{pow}"
            pow += 1
        return r


class RandomPolynomialGenerator:
    def __init__(self, N):
        self.N = N

    def __call__(self, d1, d2):
        coefficients = [1] * d1 + [-1] * d2 + [0] * (self.N - d1 - d2 + 1)
        np.random.shuffle(coefficients)
        return Polynomial(coefficients)


class TestPolynomialGenerator:
    def __init__(self, test_data):
        self.counter = -1
        self.test_data = test_data

    def __call__(self, *args, **kwargs):
        self.counter += 1
        return Polynomial(self.test_data[self.counter])


if __name__ == '__main__':
    q = 3
    N = 5
    f = Polynomial([1, -1, 0, 1])
    print(f)
    _mod = Polynomial([-1] + [0] * (N - 1) + [1])
    print(_mod)

    print(Polynomial.divmod(_mod, f, q))

    print(Polynomial.gcd(_mod, f, q, True))

    print("*" * 100)

    _, t = Polynomial.gcd(_mod, f, q)

    print(t * f)

    print(Polynomial.divmod(t * f, _mod, q)[1])

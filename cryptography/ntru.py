import dataclasses

from cryptography.polynomial import Polynomial


def modulus(N):
    return Polynomial([-1] + [0] * (N - 1) + [1])


def norm_in_ring(a: Polynomial, N, q):
    return Polynomial.divmod(a, modulus(N), q)[1]


def log_2(x):
    return x.bit_length() - 1


@dataclasses.dataclass
class NtruParams:
    N: int
    p: int
    q: int
    d_f: int
    d_g: int


class NtruKeyGenerator:

    def __init__(self, params: NtruParams, random_polynomial_generator, debug=False):
        self.params = params
        self.random_polynomial_generator = random_polynomial_generator
        self.debug = debug
        self.f, self.g, self.h = self._key_generation()

    def _key_generation(self):
        _mod = modulus(self.params.N)
        gcd_p, gcd_q, f, fp_inv, fq_inv = Polynomial([0, 1]), Polynomial([0, 1]), None, None, None
        while gcd_p.degree != 1 or gcd_q.degree != 1:
            f = self.random_polynomial_generator(self.params.d_f + 1, self.params.d_f)

            gcd_p, fp_inv = Polynomial.gcd(_mod, f, self.params.p)

            # we assume that q is a power of 2
            fq_inv = Polynomial.invert_p_to_r(f, _mod, 2, log_2(self.params.q))
            fq_inv = norm_in_ring(fq_inv, self.params.N, self.params.q)
            fq_inv = fq_inv.center(self.params.q)
            gcd_q = Polynomial.gcd(_mod, f * fq_inv, self.params.q)[0]

        fp_inv = fp_inv.center(self.params.p)
        fq_inv = fq_inv.center(self.params.q)

        g = self.random_polynomial_generator(self.params.d_g, self.params.d_g)
        h = norm_in_ring(g * self.params.p * fq_inv, self.params.N, self.params.q)
        h = h.center(self.params.q)

        if self.debug:
            self._log_params(f, fp_inv, fq_inv, g, h)

        return f, g, h

    @property
    def public_key(self):
        return self.h.coefficients

    @property
    def private_key(self):
        return self.f.coefficients, self.g.coefficients

    def _log_params(self, f, fp_inv, fq_inv, g, h):
        print(f"N, p, q: {self.params.N, self.params.p, self.params.q}")
        print(f"f: {f}")
        print(f"g: {g}")
        print(f"fp: {fp_inv}")
        print(f"fq: {fq_inv}")
        print(f"h: {h}")


class NtruEncryptor:

    def __init__(self, params: NtruParams, public_key, random_polynomial_generator, debug=False):
        self.params = params
        self.random_polynomial_generator = random_polynomial_generator
        self.debug = debug
        self.h = Polynomial(public_key)

    def encrypt(self, message, d_r):
        m = Polynomial(message)
        if self.debug:
            print(f"m: {m}")
        r = self.random_polynomial_generator(d_r, d_r)
        if self.debug:
            print(f"r: {r}")
        c = norm_in_ring(r * self.h + m, self.params.N, self.params.q)
        if self.debug:
            print(f"c: {c}")
        c = c.center(self.params.q)
        if self.debug:
            print(f"c: {c}")
        return c.coefficients


class NtruDecryptor:

    def __init__(self, params: NtruParams, private_key, debug=False):
        self.params = params
        self.debug = debug
        self.f, self.g = (Polynomial(x) for x in private_key)
        _, fp_inv = Polynomial.gcd(modulus(self.params.N), self.f, self.params.p)
        self.fp_inv = fp_inv.center(self.params.p)

    def decrypt(self, encrypted):
        c = Polynomial(encrypted)
        if self.debug:
            print(f"c: {c}")
        a = norm_in_ring(self.f * c, self.params.N, self.params.q)
        if self.debug:
            print(f"a: {a}")
        a = a.center(self.params.q)
        if self.debug:
            print(f"a: {a}")
        m = norm_in_ring(self.fp_inv * a, self.params.N, self.params.p)
        if self.debug:
            print(f"m: {m}")
        m = m.center(self.params.p)
        if self.debug:
            print(f"m: {m}")
        return m.coefficients

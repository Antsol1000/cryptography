from cryptography.ntru import (
    NtruDecryptor,
    NtruEncryptor,
    NtruKeyGenerator,
    NtruParams
)
from cryptography.polynomial import RandomPolynomialGenerator, TestPolynomialGenerator

if __name__ == '__main__':
    print("NTRU demo")
    print("-" * 80)

    N, p, q, d_f, d_g, d_r = 4, 3, 16, 1, 1, 1
    # N, p, q, d_f, d_g, d_r = 107, 3, 64, 14, 12, 5
    # N, p, q, d_f, d_g, d_r = 509, 3, 2048, 11, 11, 11

    params = NtruParams(N=N, p=p, q=q, d_f=d_f, d_g=d_g)

    print("Firstly, let's generate the keys:")

    # rpg = TestPolynomialGenerator(test_data=[
    #     [1, 0, -1, 1],
    #     [1, 0, -1, 0],
    #     [1, 0, 0, -1],
    # ])
    rpg = RandomPolynomialGenerator(N=N)

    ntru = NtruKeyGenerator(params, rpg, debug=True)

    print()
    print("Let's print the keys:")

    pkey = ntru.public_key
    print(f"Public key: {pkey}")

    sec = ntru.private_key
    print(f"Private key: {sec}")

    print("-" * 80)
    print("Now, let's encrypt and decrypt the message.")

    print()
    msg = [1, -1, -1]
    print(f"Message: {msg}")
    print()

    print("Encrypting the message using the public key:")

    ntru_enc = NtruEncryptor(params, pkey, rpg, debug=True)
    encrypted = ntru_enc.encrypt(msg, d_r=d_r)
    print()
    print(f"Encrypted: {encrypted}")
    print()

    print("Decrypting the message using the private key:")

    ntru_dec = NtruDecryptor(params, sec, debug=True)
    decrypted = ntru_dec.decrypt(encrypted)
    print()
    print(f"Decrypted: {decrypted}")

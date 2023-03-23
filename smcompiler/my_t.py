from expression import Secret, Addition, AbstractOperator, Scalar
from test_integration import suite


def main():
    alice_secret = Secret()
    bob_secret = Secret()
    charlie_secret = Secret()

    parties = {
        "Alice": {alice_secret: 3},
        "Bob": {bob_secret: 14},
        "Charlie": {charlie_secret: 2}
    }

    expr = (alice_secret + bob_secret + charlie_secret)
    expected = 3 + 14 + 2
    suite(parties, expr, expected)


def main_suite2():
    aa = Secret()
    bb = Secret()
    cc = aa + bb
    print(isinstance(cc, AbstractOperator))


def main3():
    """
    f(a, b, c) = (a + b + c) ∗ K
    """
    alice_secret = Secret()
    bob_secret = Secret()
    charlie_secret = Secret()

    parties = {
        "Alice": {alice_secret: 3},
        "Bob": {bob_secret: 14},
        "Charlie": {charlie_secret: 2}
    }

    expr = ((alice_secret + bob_secret + charlie_secret) * Scalar(5))
    expected = (3 + 14 + 2) * 5
    suite(parties, expr, expected)


def suit_7():
    """
        f(a, b, c) = (a ∗ b) + (b ∗ c) + (c ∗ a)
        """
    alice_secret = Secret()
    bob_secret = Secret()
    charlie_secret = Secret()

    parties = {
        "Alice": {alice_secret: 3},
        "Bob": {bob_secret: 14},
        "Charlie": {charlie_secret: 2}
    }

    # expr = (
    #         (alice_secret * bob_secret) +
    #         (bob_secret * charlie_secret) +
    #         (charlie_secret * alice_secret)
    # )
    # expected = ((3 * 14) + (14 * 2) + (2 * 3))

    expr = (
            (alice_secret * bob_secret)
    )
    expected = (3 * 14)
    suite(parties, expr, expected)


def suit_8():
    """
    f(a1, a2, a3, b) = a1 + a2 + a3 + b
    """
    alice_secrets = [Secret(), Secret(), Secret()]
    bob_secret = Secret()

    parties = {
        "Alice": {alice_secrets[0]: 3, alice_secrets[1]: 14, alice_secrets[2]: 2},
        "Bob": {bob_secret: 5},
    }

    expr = alice_secrets[0] + alice_secrets[1] + alice_secrets[2] + bob_secret
    expected = 3 + 14 + 2 + 5
    suite(parties, expr, expected)


if __name__ == '__main__':
    suit_8()

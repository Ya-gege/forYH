from smcompiler.expression import Secret, Addition, AbstractOperator
from smcompiler.test_integration import suite


def test_main():
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


def main2():
    aa = Secret()
    bb = Secret()
    cc = aa + bb
    print(isinstance(cc, AbstractOperator))


if __name__ == '__main__':
    main2()

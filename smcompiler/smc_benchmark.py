from expression import Secret
from protocol import ProtocolSpec
from test_integration import suite, run_processes


def run(participants, *clients):
    results = run_processes(participants, *clients)
    return results


def test_benchmark_suite_1(benchmark):
    """
        f(a, b, c) = a + b + c
        """

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

    participants = list(parties.keys())

    prot = ProtocolSpec(expr=expr, participant_ids=participants)
    clients = [(name, prot, value_dict) for name, value_dict in parties.items()]

    results = benchmark(run, participants, *clients)
    for res in results:
        assert res == 19

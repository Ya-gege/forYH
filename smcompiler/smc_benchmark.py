import math

from pytest_benchmark.plugin import benchmark

from expression import Secret
from protocol import ProtocolSpec
from test_integration import run_processes

FIXED_VAL = 2
CLIENT_NAME_PREFIX = "party_"


def run(participants, *clients):
    results = run_processes(participants, *clients)
    return results


def secret_generator(num_party: int) -> dict:
    party_dict = dict()
    for num in range(0, num_party):
        party_dict[CLIENT_NAME_PREFIX + str(num)] = Secret()
    return party_dict


def party_generator(secret_dict):
    parties = dict()
    key_list = secret_dict.keys()
    for key in key_list:
        val = dict()
        val[secret_dict[key]] = FIXED_VAL
        parties[key] = val
    return parties


def expr_generator_add(num_party: int, num_add: int):
    secret_dict = secret_generator(num_party)
    parties = party_generator(secret_dict)
    secret_list = list(secret_dict.values())
    expr = secret_list[0]
    for i in range(0, num_add - 1):
        expr = expr + secret_list[i % num_party]
    return parties, expr


def expr_generator_mul(num_party: int, num_mul: int):
    secret_dict = secret_generator(num_party)
    parties = party_generator(secret_dict)
    secret_list = list(secret_dict.values())
    expr = secret_list[0]
    for i in range(0, num_mul - 1):
        expr = expr * secret_list[i % num_party]
    return parties, expr


def generator_parameters_add(num_party, num_add):
    parties, expr = expr_generator_add(num_party, num_add)
    prot = ProtocolSpec(expr=expr, participant_ids=list(parties.keys()))
    clients = [(name, prot, value_dict) for name, value_dict in parties.items()]
    return parties, clients


def generator_parameters_mul(num_party, num_add):
    parties, expr = expr_generator_mul(num_party, num_add)
    prot = ProtocolSpec(expr=expr, participant_ids=list(parties.keys()))
    clients = [(name, prot, value_dict) for name, value_dict in parties.items()]
    return parties, clients


def test_party_3_add_50(benchmark):
    num_party = 3
    num_operator = 50
    parties, clients = generator_parameters_add(num_party, num_operator)
    results = benchmark(run, list(parties.keys()), *clients)
    # results = run(list(parties.keys()), *clients)
    for res in results:
        assert res == num_operator * FIXED_VAL


def test_party_10_add_50(benchmark):
    num_party = 10
    num_operator = 50
    parties, clients = generator_parameters_add(num_party, num_operator)
    results = benchmark(run, list(parties.keys()), *clients)
    # results = run(list(parties.keys()), *clients)
    for res in results:
        assert res == num_operator * FIXED_VAL


def test_party_10_add_100(benchmark):
    num_party = 10
    num_operator = 100
    parties, clients = generator_parameters_add(num_party, num_operator)
    results = benchmark(run, list(parties.keys()), *clients)
    # results = run(list(parties.keys()), *clients)
    for res in results:
        assert res == num_operator * FIXED_VAL


def test_party_10_add_500(benchmark):
    num_party = 10
    num_operator = 500
    parties, clients = generator_parameters_add(num_party, num_operator)
    results = benchmark(run, list(parties.keys()), *clients)
    # results = run(list(parties.keys()), *clients)
    for res in results:
        assert res == num_operator * FIXED_VAL


def test_party_3_mul_10():
    num_party = 3
    num_operator = 10
    parties, clients = generator_parameters_mul(num_party, num_operator)
    # results = benchmark(run, list(parties.keys()), *clients)
    results = run(list(parties.keys()), *clients)
    # results = run(list(parties.keys()), *clients)
    for res in results:
        assert res == math.pow(FIXED_VAL, num_operator)


# if __name__ == '__main__':
#     party_3_mul_20()

from pytest_benchmark.plugin import benchmark

from smcompiler.expression import Expression, Secret
from smcompiler.protocol import ProtocolSpec

FIXED_VAL = 20
CLIENT_NAME_PREFIX = "party_"


def secret_generator(num_party: int) -> dict:
    party_dict = dict()
    for num in range(0, num_party):
        party_dict[CLIENT_NAME_PREFIX + str(num)] = Secret()
    return party_dict


def party_generator(secret_dict):
    parties = dict()
    key_list = secret_dict.keys()
    for key in key_list:
        parties[key] = {secret_dict[key], FIXED_VAL}
    return parties


def expr_generator_add(num_party: int, num_add: int):
    secret_dict = secret_generator(num_party)
    parties = party_generator(secret_dict)
    secret_list = list(secret_dict.keys())
    expr = secret_list[0]
    for i in range(0, num_add):
        expr = expr + secret_list[i % num_party]
    return parties, expr


def test_party_3_add_50():
    parties, expr = expr_generator_add(3, 50)
    prot = ProtocolSpec(expr=expr, participant_ids=list(parties.keys()))
    clients = [(name, prot, value_dict) for name, value_dict in parties.items()]

    results = benchmark(run, participants, *clients)
    for res in results:
        assert res == 19
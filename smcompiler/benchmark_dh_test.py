from expression import Secret, Expression
from protocol import ProtocolSpec
from test_integration import run_processes

SECRET_FIXED_VAL = 2
PARTY_PREFIX = "party_"


def run(server_args, *client_args):
    return run_processes(server_args, *client_args)


def generate_client_secret(party_num: int) -> dict:
    res = dict()
    for client_idx in range(0, party_num):
        res[PARTY_PREFIX + str(client_idx)] = Secret()
    return res


def generate_parties(client_secret_dict: dict) -> dict:
    parties = dict()
    for client_name in list(client_secret_dict.keys()):
        secret_val_dict = dict()
        secret_val_dict[client_secret_dict[client_name]] = SECRET_FIXED_VAL
        parties[client_name] = secret_val_dict
    return parties


def generate_expr_add(num_operator: int, client_secret_dict: dict) -> Expression:
    secret_list = list(client_secret_dict.values())
    expr = secret_list[0]
    for i in range(1, num_operator):
        expr = expr + secret_list[i % len(secret_list)]
    return expr


def run_benchmark(num_party, num_operator, benchmark):
    client_secret_dict = generate_client_secret(num_party)
    parties = generate_parties(client_secret_dict)
    expr = generate_expr_add(num_operator, client_secret_dict)

    participants = list(parties.keys())
    prot = ProtocolSpec(expr=expr, participant_ids=participants)
    clients = [(name, prot, value_dict) for name, value_dict in parties.items()]
    results = benchmark(run, participants, *clients)
    # results = run(participants, *clients)
    for result in results:
        assert result == num_operator * SECRET_FIXED_VAL


def test_party_3_add_50(benchmark):
    run_benchmark(3, 50, benchmark)

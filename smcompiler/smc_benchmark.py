import math
import time
from multiprocessing import Process, Queue

import requests
from pytest_benchmark.plugin import benchmark

from expression import Secret
from protocol import ProtocolSpec
from test_integration import smc_server, smc_client

FIXED_VAL = 2
CLIENT_NAME_PREFIX = "party_"


def get_comm_cost(comm_type: str):
    url = f"http://localhost:5000/count/bytes/{comm_type}"
    return requests.get(url).content


# def smc_client(client_id, prot, value_dict, queue):
#     cli = SMCParty(
#         client_id,
#         "localhost",
#         5000,
#         protocol_spec=prot,
#         value_dict=value_dict
#     )
#     res = cli.run()
#     queue.put(res)
#     print(f"{client_id} has finished!")
#
#
# def smc_server(args):
#     run("localhost", 5000, args)


def run_processes(server_args, *client_args):
    queue = Queue()

    server = Process(target=smc_server, args=(server_args,))
    clients = [Process(target=smc_client, args=(*args, queue)) for args in client_args]

    server.start()
    time.sleep(3)
    for client in clients:
        client.start()

    results = list()
    for client in clients:
        client.join()

    for client in clients:
        results.append(queue.get())

    # 打印通信传输字节数
    request_cost = get_comm_cost("request")
    response_cost = get_comm_cost("response")

    server.terminate()
    server.join()

    # To "ensure" the workers are dead.
    time.sleep(2)

    print("Server stopped.")

    return results, request_cost, response_cost


def run(participants, *clients):
    return run_processes(participants, *clients)


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


def generator_local_file(num_party, num_operator, request_cost, response_cost):
    file_name = f"party_{num_party}_op_{num_operator}.txt"
    with open(file_name, 'w+') as f:
        f.write("Comm_request_cost: {} bytes".format(str(request_cost)[2:-1]))
        f.write('\n')
        f.write("Comm_response_cost: {} bytes".format(str(response_cost)[2:-1]))


def benchmark_cms_add(num_party, num_operator, benchmark):
    parties, clients = generator_parameters_add(num_party, num_operator)
    results, request_cost, response_cost = benchmark(run, list(parties.keys()), *clients)
    # results, request_cost, response_cost = run(list(parties.keys()), *clients)
    generator_local_file(num_party, num_operator, request_cost, response_cost)
    for res in results:
        assert res == num_operator * FIXED_VAL


def test_party_3_add_50(benchmark):
    benchmark_cms_add(3, 50, benchmark)


def test_party_10_add_50(benchmark):
    num_party = 10
    num_operator = 50
    parties, clients = generator_parameters_add(num_party, num_operator)
    results, request_cost, response_cost = benchmark(run, list(parties.keys()), *clients)
    generator_local_file(num_party, num_operator, request_cost, response_cost)
    # results = run(list(parties.keys()), *clients)
    for res in results:
        assert res == num_operator * FIXED_VAL


def test_party_10_add_100(benchmark):
    num_party = 10
    num_operator = 100
    parties, clients = generator_parameters_add(num_party, num_operator)
    results, request_cost, response_cost = benchmark(run, list(parties.keys()), *clients)
    generator_local_file(num_party, num_operator, request_cost, response_cost)
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


def test_party_3_mul_10(benchmark):
    num_party = 3
    num_operator = 10
    parties, clients = generator_parameters_mul(num_party, num_operator)
    results = benchmark(run, list(parties.keys()), *clients)
    # results = run(list(parties.keys()), *clients)
    for res in results:
        assert res == math.pow(FIXED_VAL, num_operator)


if __name__ == '__main__':
    test_party_3_add_50()

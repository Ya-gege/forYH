import math
import time
from multiprocessing import Process, Queue

import requests

from expression import Secret, Scalar
from protocol import ProtocolSpec
from test_integration import smc_server, smc_client

FIXED_VAL = 2
CLIENT_NAME_PREFIX = "party_"

FIXED_SCALAR_VAL = 5


def get_comm_cost(comm_type: str):
    url = f"http://localhost:5000/count/bytes/{comm_type}"
    return requests.get(url).content


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

    # 获取通信传输字节数
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
    # 生成parties 和 expr
    parties, expr = expr_generator_add(num_party, num_add)
    prot = ProtocolSpec(expr=expr, participant_ids=list(parties.keys()))
    clients = [(name, prot, value_dict) for name, value_dict in parties.items()]
    return parties, clients


def generator_parameters_mul(num_party, num_add):
    parties, expr = expr_generator_mul(num_party, num_add)
    prot = ProtocolSpec(expr=expr, participant_ids=list(parties.keys()))
    clients = [(name, prot, value_dict) for name, value_dict in parties.items()]
    return parties, clients


def generator_local_file(num_party, num_operator, request_cost, response_cost, type):
    file_name = "communication_cost_benchmark.txt"
    with open(file_name, 'a') as f:
        f.write("party_{}_op_{}_type_{}:\n".format(num_party, num_operator, type))
        f.write("   Comm_request_cost: {} bytes\n".format(str(request_cost)[2:-1]))
        f.write("   Comm_response_cost: {} bytes\n".format(str(response_cost)[2:-1]))
        f.write('')


def generator_local_file_with_scalar(num_party, num_operator, num_scalar, request_cost, response_cost, type):
    file_name = "communication_cost_benchmark.txt"
    with open(file_name, 'a') as f:
        f.write("party_{}_op_{}_type_{}_scalar_{}:\n".format(num_party, num_operator, type, num_scalar))
        f.write("   Comm_request_cost: {} bytes\n".format(str(request_cost)[2:-1]))
        f.write("   Comm_response_cost: {} bytes\n".format(str(response_cost)[2:-1]))
        f.write('')


def benchmark_cms_add(num_party, num_operator, benchmark):
    # 生成parties， clients
    parties, clients = generator_parameters_add(num_party, num_operator)
    results, request_cost, response_cost = benchmark(run, list(parties.keys()), *clients)
    # results, request_cost, response_cost = run(list(parties.keys()), *clients)
    # 生成通信开销文件
    generator_local_file(num_party, num_operator, request_cost, response_cost, "add")
    for res in results:
        assert res == num_operator * FIXED_VAL


def benchmark_cms_mul(num_party, num_operator, benchmark):
    parties, clients = generator_parameters_mul(num_party, num_operator)
    results, request_cost, response_cost = benchmark(run, list(parties.keys()), *clients)
    # results, request_cost, response_cost = run(list(parties.keys()), *clients)
    # 生成通信开销文件
    generator_local_file(num_party, num_operator, request_cost, response_cost, "mul")
    for res in results:
        assert res == math.pow(FIXED_VAL, num_operator)


def add_scalar(expr, num_scalar_operator):
    for _ in range(0, num_scalar_operator):
        expr = expr + Scalar(FIXED_SCALAR_VAL)
    return expr


def generator_parameters_add_scalar(num_party, num_add_operator, num_scalar_operator):
    parties, expr = expr_generator_add(num_party, num_add_operator)
    expr = add_scalar(expr, num_scalar_operator)
    prot = ProtocolSpec(expr=expr, participant_ids=list(parties.keys()))
    clients = [(name, prot, value_dict) for name, value_dict in parties.items()]
    return parties, clients


def benchmark_cms_add_scalar(num_party, num_add_operator, num_scalar_operator, benchmark):
    # secret + secret + scalar
    parties, clients = generator_parameters_add_scalar(num_party, num_add_operator, num_scalar_operator)
    results, request_cost, response_cost = benchmark(run, list(parties.keys()), *clients)
    # results, request_cost, response_cost = run(list(parties.keys()), *clients)
    # 生成通信开销文件
    generator_local_file_with_scalar(num_party, num_add_operator, num_scalar_operator, request_cost, response_cost,
                                     "add")
    for res in results:
        assert res == FIXED_VAL * num_add_operator + num_scalar_operator * FIXED_SCALAR_VAL


'''
                    for test
'''


def test_party_3_add_50(benchmark):
    benchmark_cms_add(3, 50, benchmark)


def test_party_10_add_50(benchmark):
    benchmark_cms_add(10, 50, benchmark)


def test_party_10_add_100(benchmark):
    benchmark_cms_add(10, 100, benchmark)


def test_party_10_add_500(benchmark):
    benchmark_cms_add(10, 500, benchmark)


def test_party_3_mul_5(benchmark):
    benchmark_cms_mul(3, 5, benchmark)


def test_party_3_add_10_scalar_10(benchmark):
    benchmark_cms_add_scalar(3, 10, 10, benchmark)


'''
            for actual report
'''


def test_actual_party_5_add_50(benchmark):
    benchmark_cms_add(5, 50, benchmark)


def test_actual_party_10_add_50(benchmark):
    benchmark_cms_add(10, 50, benchmark)


def test_actual_party_15_add_50(benchmark):
    benchmark_cms_add(15, 50, benchmark)


def test_actual_party_20_add_50(benchmark):
    benchmark_cms_add(20, 50, benchmark)


def test_actual_party_25_add_50(benchmark):
    benchmark_cms_add(25, 50, benchmark)


def test_actual_party_30_add_50(benchmark):
    benchmark_cms_add(30, 50, benchmark)

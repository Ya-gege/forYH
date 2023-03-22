import time
from multiprocessing import Process

from smcompiler.communication import Communication
from smcompiler.server import run


def smc_serve(args):
    run("localhost", 5000, args)


def smc_client_wang():
    comm = Communication("localhost", 5000, "Wang")

    # 私发消息给client_huang
    comm.send_private_message("Huang", "test_to_Huang", "serialized object")


def smc_client_huang():
    comm = Communication("localhost", 5000, "Huang")

    # 接受私发消息
    print(comm.retrieve_private_message("test_to_Huang"))


def test_main():
    serve = Process(target=smc_serve, args=("test_smc",))
    client_wang = Process(target=smc_client_wang)
    client_huang = Process(target=smc_client_huang)
    serve.start()
    time.sleep(3)

    client_wang.start()
    client_huang.start()

    client_wang.join()
    client_huang.join()

    serve.terminate()
    serve.join()


# if __name__ == '__main__':
#     main()

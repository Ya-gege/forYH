import time
from multiprocessing import Process


def cli(arg):
    print(arg)
    time.sleep(2)


def test_process():
    leng = 5
    cs = [Process(target=cli, args=(j,)) for j in range(leng)]
    for h in cs:
        h.start()

    for h in cs:
        h.join()

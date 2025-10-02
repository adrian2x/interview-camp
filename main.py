from os import getpid
from multiprocessing import Pool, get_context
from time import sleep


def squared(x):
    sleep(1)
    print('started process:', getpid())
    return x ** 2


if __name__ == '__main__':
  with get_context('spawn').Pool() as pool:
    result = pool.map(squared, [1, 3, 5, 8, 13])
    print(result)

'''
The simplest implementation uses per-process counters, which are then aggregated in the main process.
'''

from __future__ import annotations
from multiprocessing import Pool

class Counter:
    def __init__(self):
        self.__counter: int = 0

    def increase(self, value):
        self.__counter += value

    def __add__(self, obj: Counter) -> Counter:
        cnt = Counter()
        cnt.__counter = self.__counter + obj.__counter
        return cnt

    @property
    def value(self) -> int:
        return self.__counter


def worker(name: str) -> Counter:
    cnt = Counter()
    cnt.increase(10)
    print(f"I am {name} and doing some kind of important work in parallel")

    return cnt

if __name__ == "__main__":
    main_cnt = Counter()

    with Pool(5) as p:
        for cnt in p.map(worker, ["w-1", "w-2", "w-3"]):
            main_cnt += cnt

    print(main_cnt.value)

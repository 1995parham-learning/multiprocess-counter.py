'''
Shared memory approach using multiprocessing.Value with a Lock.
All worker processes directly increment a shared counter protected by a lock.
This is the idiomatic Python way to share a simple counter across processes.
'''

from multiprocessing import Pool, Value, Lock
import random

counter: Value
lock: Lock


def init_worker(shared_counter: Value, shared_lock: Lock):
    global counter, lock
    counter = shared_counter
    lock = shared_lock


def worker(name: str):
    for _ in range(random.randint(1, 10)):
        with lock:
            counter.value += 10
    print(f"I am {name} and doing some kind of important work in parallel")


if __name__ == "__main__":
    counter = Value('i', 0)
    lock = Lock()

    with Pool(5, initializer=init_worker, initargs=(counter, lock)) as p:
        p.map(worker, ["w-1", "w-2", "w-3"])

    print(counter.value)

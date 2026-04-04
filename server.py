'''
Client-server approach using UDP sockets.
The main process runs a UDP server that listens for increment commands.
Worker processes send increment requests over UDP to the server.

Downsides:
- UDP is unreliable — messages can be silently dropped under load, losing increments.
- No synchronization guarantee — a sleep is needed before reading the final value,
  which is fragile and doesn't guarantee all messages have been processed.
- Hardcoded host/port makes it impossible to run multiple instances concurrently.
- Overly complex for a shared counter — sockets, threads, selectors, and a custom
  protocol are unnecessary when multiprocessing.Value + Lock solves this in a few lines.

See shared.py for a more Pythonic approach using multiprocessing.Value.
'''

from __future__ import annotations
from multiprocessing import Pool
import socket
import threading
import selectors
import random
import time

class Counter:
    HOST: str = "127.0.0.1"
    PORT: int = 1378

    def __init__(self, name: str | None = None):
        self.__counter: int = 0
        self.__is_client: bool = False
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        if name is None:
            self.__is_running = threading.Event()
            self.__is_running.set()
            self.socket.bind((self.HOST, self.PORT))
            threading.Thread(target=self.__listen, daemon=False).start()
        else:
            self.__is_client = True

    def __listen(self):
        sel = selectors.DefaultSelector()
        sel.register(self.socket, selectors.EVENT_READ)

        while self.__is_running.is_set():
            events = sel.select(timeout=1)
            for _ in events:
                data, _ = self.socket.recvfrom(1024)
                if not data:
                    continue
                match data.decode().split():
                    case ["INC", value]:
                        self.__counter += int(value)
                    case _:
                        print("Invalid command")
        sel.close()
        self.socket.close()


    def increase(self, value):
        if self.__is_client:
            self.socket.sendto(f'INC {value}'.encode(), (self.HOST, self.PORT))
        else:
            self.__counter += value

    def close(self):
        self.__is_running.clear()

    @property
    def value(self) -> int:
        if self.__is_client:
            return 0
        return self.__counter


def worker(name: str):
    cnt = Counter(name)
    for _ in range(random.randint(1, 10)):
        cnt.increase(10)
    cnt.socket.close()
    print(f"I am {name} and doing some kind of important work in parallel")

if __name__ == "__main__":
    main_cnt = Counter()

    with Pool(5) as p:
        p.map(worker, ["w-1", "w-2", "w-3"])

    # Allow time for the server thread to process remaining UDP messages
    time.sleep(0.5)
    print(main_cnt.value)
    main_cnt.close()

# test.py

import time

from multithreading import Caller, multi_threaded_call

def slow_function(number: int, delay: float) -> dict[str, int | float]:

    for i in range(number):
        time.sleep(delay)

    return dict(number=number, delay=delay)

CALLS = 50
DELAY = 0.01
NUMBER = 100

def main() -> None:

    callers = [
        Caller(
            target=slow_function,
            kwargs=dict(delay=DELAY, number=NUMBER)
        ) for _ in range(CALLS)
    ]

    s = time.time()

    multi_threaded_call(callers)

    e = time.time()

    print(e - s)

    s = e

    all(slow_function(*caller.args, **caller.kwargs) for caller in callers)

    e = time.time()

    print(e - s)

if __name__ == '__main__':
    main()

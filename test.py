# test.py

import random
import time

from multithreading import Caller, multi_threaded_call

data = []

def slow_function(minimum: int, maximum: int) -> int:
    """
    A function to generate a random int and wait for that amount of seconds.

    :param minimum: The minimum limit for the generation.
    :param maximum: The maximum limit for the generation.

    :return: The random number.
    """

    number = random.randint(minimum, maximum)

    for i in range(number):
        time.sleep(random.randint(0, 10) / 100)

        data.append(number)
        data.sort()
    # end for

    return number
# end slow_function

CALLS = 50
MIN = 10
MAX = 100

def main() -> None:
    """A function to run the main test."""

    callers = [
        Caller(
            target=slow_function,
            kwargs=dict(minimum=MIN, maximum=MAX)
        ) for _ in range(CALLS)
    ]

    results = multi_threaded_call(callers=callers)

    for result in sorted(
        [result for result in results.results.values()],
        key=lambda res: res.time.time
    ):
        print(result)
    # end for

    print(results.time)
# end main

if __name__ == "__main__":
    main()
# end if
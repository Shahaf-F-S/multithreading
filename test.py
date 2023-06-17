# test.py

import random
import time

from multithreading import Caller, multi_threaded_call

def slow_function(minimum: int, maximum: int) -> int:
    """
    A function to generate a random int and wait for that amount of seconds.

    :param minimum: The minimum limit for the generation.
    :param maximum: The maximum limit for the generation.

    :return: The random number.
    """

    number = random.randint(minimum, maximum)

    time.sleep(number)

    return number
# end slow_function

CALLS = 1
MIN = 1
MAX = 2

def main() -> None:
    """A function to run the main test."""

    callers = [
        Caller(
            target=slow_function,
            kwargs=dict(minimum=MIN, maximum=MAX)
        )
        for _ in range(CALLS)
    ]

    results = multi_threaded_call(callers=callers)

    print(results)
# end main

if __name__ == "__main__":
    main()
# end if
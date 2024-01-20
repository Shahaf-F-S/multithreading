# test.py

import random
import time

from multithreading import Caller, multi_threaded_call

data = []

def slow_function(
        minimum: int = None,
        maximum: int = None,
        number: int = None,
        delay: float = None
) -> dict[str, int | float]:
    """
    A function to generate a random int and wait for that amount of seconds.

    :param minimum: The minimum limit for the generation.
    :param maximum: The maximum limit for the generation.
    :param number: a random number.
    :param delay: A random delay.

    :return: The random number.
    """

    if number is None:
        if None in (minimum, maximum):
            raise ValueError(
                "minimum and maximum must be defined when number is not."
            )
        # end if

        number = random.randint(minimum, maximum)
    # end if

    for i in range(number):
        if delay is None:
            delay = random.randint(0, 10) / 100
        # end if

        time.sleep(delay)

        data.append(number)
        data.sort()
    # end for

    return dict(
        minimum=minimum, maximum=maximum,
        number=number, delay=delay
    )
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
# end main

if __name__ == "__main__":
    main()
# end if
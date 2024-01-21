# multithreading

> A python module for creating multithreading processes easily, in a more Pythonic way.

## Installation
```
pip install python-multithreading
```

## example

```python
import time

from multithreading import Caller, multi_threaded_call

def slow_function(number: int, delay: float) -> dict[str, int | float]:

    for i in range(number):
        time.sleep(delay)

    return dict(number=number, delay=delay)

CALLS = 50
DELAY = 0.01
NUMBER = 100

callers = [
    Caller(
        target=slow_function,
        kwargs=dict(delay=DELAY, number=NUMBER)
    ) for _ in range(CALLS)
]

s = time.time()

multi_threaded_call(callers)

e = time.time()

print("multi-threading: ", e - s)

s = e

all(slow_function(*caller.args, **caller.kwargs) for caller in callers)

e = time.time()

print("single-threading: ", e - s)
```

output
```
multi-threading: 1.0473840236663818
single-threading: 52.53497314453125
```
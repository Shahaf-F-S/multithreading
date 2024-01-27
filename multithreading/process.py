# process.py

import datetime as dt
import threading
import time
from typing import Callable, Iterable, ParamSpec
from dataclasses import dataclass

__all__ = [
    "Caller",
    "CallDefinition",
    "CallsResults",
    "multi_threaded_call",
    "multi_threaded_defined_call",
    "await_completion",
    "ProcessTime",
    "find_caller",
    "CallResult"
]

@dataclass(slots=True, frozen=True)
class ProcessTime:
    """A class to contain the info of a call to the results."""

    start: dt.datetime
    end: dt.datetime

    @property
    def time(self) -> dt.timedelta:
        """
        Returns the time duration of the call.

        :return: The call time.
        """

        return self.end - self.start

_P = ParamSpec("_P")

class CallResult[R]:
    """A class to represent a container for the call result."""

    __slots__ = ('_returns', '_thread', '_time')

    # noinspection PyShadowingNames
    def __init__(
            self,
            returns: R = None,
            thread: threading.Thread = None,
            time: ProcessTime = None,
    ) -> None:

        self._returns = returns
        self._thread = thread
        self._time = time

    @property
    def returns(self) -> R:

        return self._returns

    @property
    def thread(self) -> threading.Thread:

        return self._thread

    @property
    def time(self) -> ProcessTime:

        return self._time

class Caller[R]:
    """A class to represent a function caller object."""

    __slots__ = (
        "target", "identifier", "args", "kwargs",
        "_thread", "_result", "complete", "called"
    )

    def __init__(
            self,
            target: Callable[_P, R],
            identifier: ... = None,
            args: _P.args = None,
            kwargs: _P.kwargs = None
    ) -> None:
        """
        Defines the class attributes.

        :param target: The function to call.
        :param identifier: The identifier of the call.
        :param args: The positional arguments.
        :param kwargs: The keyword arguments.
        """

        self.target = target
        self.args = args or ()
        self.kwargs = kwargs or {}
        self.identifier = identifier or self.target

        self.complete = False
        self.called = False

        self._thread: threading.Thread | None = None
        self._result: CallResult[R] | None = None

    def __call__(self, *args: _P.args, **kwargs: _P.kwargs) -> CallResult[R]:
        """
        Calls the function and saves the response.

        :param args: The positional arguments.
        :param kwargs: The keyword arguments.

        :return: The returned response.
        """

        start = dt.datetime.now()

        self.args = args or self.args
        self.kwargs = kwargs or self.kwargs

        self.called = True

        returns: R = self.target(*self.args, **self.kwargs)

        self.complete = True

        end = dt.datetime.now()

        self._result = CallResult[R](
            time=ProcessTime(start=start, end=end),
            thread=self.thread, returns=returns
        )

        return self.result

    @property
    def thread(self) -> threading.Thread:
        """
        Returns the thread object.

        :return: The thread of the caller.
        """

        return self._thread

    @property
    def result(self) -> CallResult[R]:
        """
        Returns the result object.

        :return: The result of the caller.
        """

        return self._result

    def start(self) -> None:
        """Starts the process."""

        self._thread = threading.Thread(target=self)

        self.thread.start()

    def reset(self) -> None:
        """Rests the values from the calls."""

        self.called = False
        self.complete = False

    def clean(self) -> None:
        """Cleans the caller."""

        self._thread = None
        self._result = None

def find_caller(callers: Iterable[Caller], identifier: ...) -> Caller:
    """
    Finds the caller object by its identifier

    :param callers: The results in which to search.
    :param identifier: The identifier of the caller to return.

    :return: The matching caller object.
    """

    for caller in callers:
        if caller.identifier == identifier:
            return caller

    raise ValueError(
        f"Cannot find a caller object with the identifier: "
        f"{identifier}. valid identifiers are: "
        f"{', '.join(str(caller.identifier) for caller in callers)}"
    )

def find_results(callers: Iterable[Caller], identifier: ...) -> Caller:
    """
    Finds the caller object by its identifier

    :param callers: The results in which to search.
    :param identifier: The identifier of the caller to return.

    :return: The matching caller object.
    """

    for caller in callers:
        if caller.identifier == identifier:
            return caller

    raise ValueError(
        f"Cannot find a caller object with the identifier: "
        f"{identifier}. valid identifiers are: "
        f"{', '.join(str(caller.identifier) for caller in callers)}"
    )

class CallDefinition:
    """A class to represent the call definition."""

    WAIT = True
    RESET_BEFORE = True
    RESET_AFTER = False
    CLEAN_BEFORE = True
    CLEAN_AFTER = False
    DYNAMIC = False

    SLEEP = 0.0001

    __slots__ = (
        "wait", "reset_before", "reset_after", "sleep",
        "clean_before", "clean_after", "dynamic"
    )

    def __init__(
            self,
            wait: bool = None,
            reset_before: bool = None,
            reset_after: bool = None,
            clean_before: bool = None,
            clean_after: bool = None,
            dynamic: bool = None,
            sleep: int | float | dt.timedelta = None
    ) -> None:
        """
        Defines the class attributes.

        :param wait: The value to wait.
        :param reset_before: The value to reset before running.
        :param reset_after: The value to reset after running.
        :param clean_before: The value to clean before running.
        :param clean_after: The value to clean after running.
        :param dynamic: The value to enable dynamic sleep time.
        :param sleep: The time for sleeping.
        """

        if wait is None:
            wait = self.WAIT

        if sleep is None:
            sleep = self.SLEEP

        if dynamic is None:
            dynamic = self.DYNAMIC

        if reset_before is None:
            reset_before = self.RESET_BEFORE

        if reset_after is None:
            reset_after = self.RESET_AFTER

        if clean_after is None:
            clean_after = self.CLEAN_AFTER

        if clean_before is None:
            clean_before = self.CLEAN_BEFORE

        self.wait = wait
        self.reset_before = reset_before
        self.reset_after = reset_after
        self.clean_after = clean_after
        self.clean_before = clean_before
        self.dynamic = dynamic
        self.sleep = sleep

class CallsResults[R]:
    """A class to contain the info of a call to the results."""

    __slots__ = ("_results", "_time", "_waiting", "_definition")

    # noinspection PyShadowingNames
    def __init__(
            self,
            results: dict[Caller[R], CallResult[R]],
            time: ProcessTime,
            waiting: ProcessTime,
            definition: CallDefinition
    ) -> None:

        self._results = results
        self._time = time
        self._waiting = waiting
        self._definition = definition

    @property
    def results(self) -> dict[Caller[R], CallResult[R]]:

        return self._results

    @property
    def time(self) -> ProcessTime:

        return self._time

    @property
    def waiting(self) -> ProcessTime:

        return self._waiting

    @property
    def definition(self) -> CallDefinition:

        return self._definition

    def caller(self, identifier: ...) -> Caller[R]:
        """
        Finds the caller object by its identifier

        :param identifier: The identifier of the caller to return.

        :return: The matching caller object.
        """

        for caller in self.results:
            if caller.identifier == identifier:
                return caller

        raise ValueError(
            f"Cannot find a caller object with the identifier: "
            f"{identifier}. valid identifiers are: "
            f"{', '.join(str(caller.identifier) for caller in self.results)}"
        )

    def result(self, identifier: ...) -> CallResult[R]:
        """
        Finds the caller object by its identifier

        :param identifier: The identifier of the caller to return.

        :return: The matching caller object.
        """

        for caller, result in self.results.items():
            if caller.identifier == identifier:
                return result
            # end if
        # end for

        raise ValueError(
            f"Cannot find a caller object with the identifier: "
            f"{identifier}. valid identifiers are: "
            f"{', '.join(str(caller.identifier) for caller in self.results)}"
        )

def await_completion(
        callers: Iterable[Caller], definition: CallDefinition
) -> ProcessTime:
    """
    Waits for the calls to complete.

    :param callers: The call objects for the functions.
    :param definition: The call definition object.

    :return: The waiting result.
    """

    start = dt.datetime.now()

    if isinstance(definition.sleep, dt.timedelta):
        sleep = definition.sleep.total_seconds()

    else:
        sleep = definition.sleep

    while True:
        current = time.time()

        if not (
            definition.wait and
            not all(caller.complete for caller in callers)
        ):
            break

        if definition.dynamic:
            if isinstance(definition.sleep, dt.timedelta):
                sleep = definition.sleep.total_seconds()

            else:
                sleep = definition.sleep

        time.sleep(max((0, sleep - (time.time() - current))))

    end = dt.datetime.now()

    return ProcessTime(start=start, end=end)

def multi_threaded_defined_call[R](
        callers: Iterable[Caller[R]], definition: CallDefinition = None
) -> CallsResults[R]:
    """
    Calls the functions with the results.

    :param callers: The call objects for the functions.
    :param definition: The call definition object.

    :return: The call result.
    """

    start = dt.datetime.now()

    if definition is None:
        definition = CallDefinition()

    if definition.clean_before:
        [caller.clean() for caller in callers]

    if definition.reset_before:
        [caller.reset() for caller in callers]

    [caller.start() for caller in callers]

    waiting = await_completion(
        callers=callers, definition=definition
    )

    results = {caller: caller.result for caller in callers}

    if definition.reset_after:
        [caller.reset() for caller in callers]

    if definition.clean_after:
        [caller.clean() for caller in callers]

    end = dt.datetime.now()

    return CallsResults[R](
        results=results,
        time=ProcessTime(start=start, end=end),
        definition=definition,
        waiting=waiting
    )

def multi_threaded_call[R](
        callers: Iterable[Caller[R]],
        wait: bool = None,
        reset_before: bool = None,
        reset_after: bool = None,
        clean_before: bool = None,
        clean_after: bool = None,
        dynamic: bool = None,
        sleep: int | float | dt.timedelta = None
) -> CallsResults[R]:
    """
    Calls the functions with the results.

    :param callers: The call objects for the functions.
    :param wait: The value to wait.
    :param reset_before: The value to reset before running.
    :param reset_after: The value to reset after running.
    :param clean_before: The value to clean before running.
    :param clean_after: The value to clean after running.
    :param dynamic: The value to enable dynamic sleep time.
    :param sleep: The time for sleeping.

    :return: The call result.
    """

    return multi_threaded_defined_call(
        callers=callers,
        definition=CallDefinition(
            wait=wait, reset_after=reset_after,
            reset_before=reset_before, sleep=sleep,
            clean_before=clean_before, dynamic=dynamic,
            clean_after=clean_after
        )
    )

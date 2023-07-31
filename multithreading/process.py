# process.py

import datetime as dt
import threading
import time
from typing import (
    Any, Optional, Dict, Callable, ClassVar,
    Iterable, Union, TypeVar, Generic
)

from attrs import define

from represent import represent, Modifiers

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

@define(repr=False, frozen=True)
@represent
class ProcessTime:
    """A class to contain the info of a call to the results."""

    start: dt.datetime
    end: dt.datetime

    __modifiers__: ClassVar[Modifiers] = Modifiers(properties=['time'])

    @property
    def time(self) -> dt.timedelta:
        """
        Returns the time duration of the call.

        :return: The call time.
        """

        return self.end - self.start
    # end time
# end ProcessTime

_RT = TypeVar("_RT")

@define(repr=False, frozen=True)
@represent
class CallResult(Generic[_RT]):
    """A class to represent a container for the call result."""

    returns: Optional[_RT] = None
    thread: Optional[threading.Thread] = None
    time: Optional[ProcessTime] = None

    __modifiers__: ClassVar[Modifiers] = Modifiers(excluded=['thread'])
# end CallResult

@represent
class Caller(Generic[_RT]):
    """A class to represent a function caller object."""

    __modifiers__ = Modifiers(properties=['result'])

    __slots__ = (
        "target", "identifier", "args", "kwargs",
        "_thread", "_result", "complete", "called"
    )

    def __init__(
            self,
            target: Callable[..., _RT],
            identifier: Optional[Any] = None,
            args: Optional[Iterable[Any]] = None,
            kwargs: Optional[Dict[str, Any]] = None
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

        self._thread: Optional[threading.Thread] = None
        self._result: Optional[CallResult[_RT]] = None
    # end __init__

    def __call__(self, *args: Any, **kwargs: Any) -> CallResult[_RT]:
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

        returns: _RT = self.target(*self.args, **self.kwargs)

        self.complete = True

        end = dt.datetime.now()

        self._result = CallResult[_RT](
            time=ProcessTime(start=start, end=end),
            thread=self.thread, returns=returns
        )

        return self.result
    # end __call__

    @property
    def thread(self) -> Optional[threading.Thread]:
        """
        Returns the thread object.

        :return: The thread of the caller.
        """

        return self._thread
    # end thread

    @property
    def result(self) -> Optional[CallResult[_RT]]:
        """
        Returns the result object.

        :return: The result of the caller.
        """

        return self._result
    # end result

    def start(self) -> None:
        """Starts the process."""

        self._thread = threading.Thread(target=self)

        self.thread.start()
    # end start

    def reset(self) -> None:
        """Rests the values from the calls."""

        self.called = False
        self.complete = False
    # end reset

    def clean(self) -> None:
        """Cleans the caller."""

        self._thread = None
        self._result = None
    # end clean
# end Caller

def find_caller(callers: Iterable[Caller], identifier: Any) -> Caller:
    """
    Finds the caller object by its identifier

    :param callers: The results in which to search.
    :param identifier: The identifier of the caller to return.

    :return: The matching caller object.
    """

    for caller in callers:
        if caller.identifier == identifier:
            return caller
        # end if
    # end for

    raise ValueError(
        f"Cannot find a caller object with the identifier: "
        f"{identifier}. valid identifiers are: "
        f"{', '.join(str(caller.identifier) for caller in callers)}"
    )
# end find_caller

def find_results(callers: Iterable[Caller], identifier: Any) -> Caller:
    """
    Finds the caller object by its identifier

    :param callers: The results in which to search.
    :param identifier: The identifier of the caller to return.

    :return: The matching caller object.
    """

    for caller in callers:
        if caller.identifier == identifier:
            return caller
        # end if
    # end for

    raise ValueError(
        f"Cannot find a caller object with the identifier: "
        f"{identifier}. valid identifiers are: "
        f"{', '.join(str(caller.identifier) for caller in callers)}"
    )
# end find_results

@represent
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
            wait: Optional[bool] = None,
            reset_before: Optional[bool] = None,
            reset_after: Optional[bool] = None,
            clean_before: Optional[bool] = None,
            clean_after: Optional[bool] = None,
            dynamic: Optional[bool] = None,
            sleep: Optional[Union[int, float, dt.timedelta]] = None
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
        # end if

        if sleep is None:
            sleep = self.SLEEP
        # end if

        if dynamic is None:
            dynamic = self.DYNAMIC
        # end if

        if reset_before is None:
            reset_before = self.RESET_BEFORE
        # end if

        if reset_after is None:
            reset_after = self.RESET_AFTER
        # end if

        if clean_after is None:
            clean_after = self.CLEAN_AFTER
        # end if

        if clean_before is None:
            clean_before = self.CLEAN_BEFORE
        # end if

        self.wait = wait
        self.reset_before = reset_before
        self.reset_after = reset_after
        self.clean_after = clean_after
        self.clean_before = clean_before
        self.dynamic = dynamic
        self.sleep = sleep
    # end __init__
# end CallDefinition

@define(repr=False, frozen=True)
@represent
class CallsResults:
    """A class to contain the info of a call to the results."""

    results: Dict[Caller, CallResult]
    time: ProcessTime
    waiting: ProcessTime
    definition: CallDefinition

    __modifiers__ = Modifiers(excluded=['waiting'])

    def caller(self, identifier: Any) -> Caller:
        """
        Finds the caller object by its identifier

        :param identifier: The identifier of the caller to return.

        :return: The matching caller object.
        """

        for caller in self.results:
            if caller.identifier == identifier:
                return caller
            # end if
        # end for

        raise ValueError(
            f"Cannot find a caller object with the identifier: "
            f"{identifier}. valid identifiers are: "
            f"{', '.join(str(caller.identifier) for caller in self.results)}"
        )
    # end caller

    def result(self, identifier: Any) -> CallResult:
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
    # end result
# end CallsResults

def validate_callers(data: Any) -> Iterable[Caller]:
    """
    Validates the data as results.

    :param data: The data to validate.

    :return: The valid results data.
    """

    try:
        if not all(isinstance(value, Caller) for value in data):
            raise ValueError
        # end if

        return data

    except (TypeError, ValueError) as e:
        raise type(e)(
            f"Callers must be an iterable of "
            f"{Caller} objects, not: {data}."
        ) from e
    # end try
# end validate_callers

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
    # end if

    while True:
        current = time.time()

        if not (
            definition.wait and
            not all(caller.complete for caller in callers)
        ):
            break
        # end if

        if definition.dynamic:
            if isinstance(definition.sleep, dt.timedelta):
                sleep = definition.sleep.total_seconds()

            else:
                sleep = definition.sleep
            # end if
        # end if

        time.sleep(max((0, sleep - (time.time() - current))))
    # end while

    end = dt.datetime.now()

    return ProcessTime(start=start, end=end)
# end await_completion

def multi_threaded_defined_call(
        callers: Iterable[Caller],
        definition: Optional[CallDefinition] = None
) -> CallsResults:
    """
    Calls the functions with the results.

    :param callers: The call objects for the functions.
    :param definition: The call definition object.

    :return: The call result.
    """

    start = dt.datetime.now()

    callers = validate_callers(data=callers)

    if definition is None:
        definition = CallDefinition()
    # end if

    if definition.clean_before:
        [caller.clean() for caller in callers]
    # end if

    if definition.reset_before:
        [caller.reset() for caller in callers]
    # end if

    [caller.start() for caller in callers]

    waiting = await_completion(
        callers=callers, definition=definition
    )

    results = {caller: caller.result for caller in callers}

    if definition.reset_after:
        [caller.reset() for caller in callers]
    # end if

    if definition.clean_after:
        [caller.clean() for caller in callers]
    # end if

    end = dt.datetime.now()

    return CallsResults(
        results=results,
        time=ProcessTime(start=start, end=end),
        definition=definition,
        waiting=waiting
    )
# end multi_threaded_defined_call

def multi_threaded_call(
        callers: Iterable[Caller],
        wait: Optional[bool] = None,
        reset_before: Optional[bool] = None,
        reset_after: Optional[bool] = None,
        clean_before: Optional[bool] = None,
        clean_after: Optional[bool] = None,
        dynamic: Optional[bool] = None,
        sleep: Optional[Union[int, float, dt.timedelta]] = None
) -> CallsResults:
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
# end multi_threaded_call
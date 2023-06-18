# process.py

import datetime as dt
import threading
import time
from abc import ABCMeta
from typing import (
    Any, Optional, Dict, Callable, Iterable, Union
)

from represent import BaseModel, Modifiers

__all__ = [
    "Caller",
    "CallDefinition",
    "CallsResults",
    "multi_threaded_call",
    "multi_threaded_defined_call",
    "wait_call_completion",
    "ProcessTime",
    "ProcessInfo",
    "find_caller",
    "CallerInfo",
    "CallResults"
]

class ProcessInfo(BaseModel, metaclass=ABCMeta):
    """A class to contain the info of a call to the callers."""

    modifiers = Modifiers(properties=True)

    __slots__ = 'start', 'end'

    def __init__(
            self,
            start: dt.datetime,
            end: dt.datetime,
    ) -> None:
        """
        Defines the class attributes.

        :param start: The starting time for the call.
        :param end: The ending time for the call.
        """

        self.start = start
        self.end = end
    # end __init__

    @property
    def time(self) -> dt.timedelta:
        """
        Returns the time duration of the call.

        :return: The call time.
        """

        return self.end - self.start
    # end time
# end CallInfo


class ProcessTime(ProcessInfo):
    """A class to contain the info of a call to the callers."""
# end ProcessTime

class CallerInfo(ProcessInfo):
    """A class to represent a function caller object."""

    modifiers = Modifiers(excluded=["thread"], force=True)

    __slots__ = "returns", "thread"

    def __init__(
            self,
            returns: Optional[Any] = None,
            thread: Optional[threading.Thread] = None,
            start: Optional[dt.datetime] = None,
            end: Optional[dt.datetime] = None,

    ) -> None:
        """
        Defines the class attributes.

        :param returns: The returned response.
        """

        super().__init__(start=start, end=end)

        self.returns = returns
        self.thread = thread
    # end __init__
# end Caller

class CallResults(CallerInfo):
    """A class to represent a container for the call results."""
# end CallResults

class Caller(BaseModel):
    """A class to represent a function caller object."""

    modifiers = Modifiers(excluded=["thread", "results"])

    __slots__ = (
        "target", "identifier", "args", "kwargs",
        "thread", "results", "complete", "called"
    )

    def __init__(
            self,
            target: Callable,
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

        self.thread: Optional[threading.Thread] = None
        self.results: Optional[CallResults] = None
    # end __init__

    def __call__(self, *args: Any, **kwargs: Any) -> CallResults:
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

        returns = self.target(*self.args, **self.kwargs)

        self.complete = True

        end = dt.datetime.now()

        self.results = CallResults(
            start=start, end=end,
            thread=self.thread, returns=returns
        )

        return self.results
    # end __call__

    def reset(self) -> None:
        """Rests the values from the calls."""

        self.called = False
        self.complete = False
    # end reset
# end Caller

def find_caller(callers: Iterable[Caller], identifier: Any) -> Caller:
    """
    Finds the caller object by its identifier

    :param callers: The callers in which to search.
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

    :param callers: The callers in which to search.
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

class CallDefinition(BaseModel):
    """A class to represent the call definition."""

    WAIT = True
    RESET_BEFORE = True
    RESET_AFTER = False

    SLEEP = 0.005

    __slots__ = "wait", "reset_before", "reset_after", "sleep"

    def __init__(
            self,
            wait: Optional[bool] = None,
            reset_before: Optional[bool] = None,
            reset_after: Optional[bool] = None,
            sleep: Optional[Union[int, float, dt.timedelta]] = None
    ) -> None:
        """
        Defines the class attributes.

        :param wait: The value to wait.
        :param reset_before: The value to reset before running.
        :param reset_after: The value to reset after running.
        :param sleep: The time for sleeping.
        """

        if wait is None:
            wait = self.WAIT
        # end if

        if sleep is None:
            sleep = self.SLEEP
        # end if

        if reset_before is None:
            reset_before = self.RESET_BEFORE
        # end if

        if reset_after is None:
            reset_after = self.RESET_AFTER
        # end if

        self.wait = wait
        self.reset_before = reset_before
        self.reset_after = reset_after
        self.sleep = sleep
    # end __init__
# end CallDefinition

class CallsResults(BaseModel):
    """A class to contain the info of a call to the callers."""

    __slots__ = "waiting", "callers", "definition", "total"

    def __init__(
            self,
            callers: Dict[Caller, CallResults],
            total: ProcessTime,
            waiting: ProcessTime,
            definition: CallDefinition
    ) -> None:
        """
        Defines the class attributes.

        :param callers: The callers object.
        :param total: The time object for the call.
        :param definition: The call definition object.
        """

        self.callers = callers
        self.definition = definition
        self.total = total
        self.waiting = waiting
    # end __init__

    def caller(self, identifier: Any) -> Caller:
        """
        Finds the caller object by its identifier

        :param identifier: The identifier of the caller to return.

        :return: The matching caller object.
        """

        for caller in self.callers:
            if caller.identifier == identifier:
                return caller
            # end if
        # end for

        raise ValueError(
            f"Cannot find a caller object with the identifier: "
            f"{identifier}. valid identifiers are: "
            f"{', '.join(str(caller.identifier) for caller in self.callers)}"
        )
    # end caller

    def results(self, identifier: Any) -> CallResults:
        """
        Finds the caller object by its identifier

        :param identifier: The identifier of the caller to return.

        :return: The matching caller object.
        """

        for caller, results in self.callers.items():
            if caller.identifier == identifier:
                return results
            # end if
        # end for

        raise ValueError(
            f"Cannot find a caller object with the identifier: "
            f"{identifier}. valid identifiers are: "
            f"{', '.join(str(caller.identifier) for caller in self.callers)}"
        )
    # end results
# end CallsResults

def validate_callers(data: Any) -> Iterable[Caller]:
    """
    Validates the data as callers.

    :param data: The data to validate.

    :return: The valid callers data.
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

def wait_call_completion(
        callers: Iterable[Caller], definition: CallDefinition
) -> ProcessTime:
    """
    Waits for the calls to complete.

    :param callers: The call objects for the functions.
    :param definition: The call definition object.

    :return: The waiting results.
    """

    start = dt.datetime.now()

    while (
        definition.wait and
        not all(caller.complete for caller in callers)
    ):
        if isinstance(definition.sleep, dt.timedelta):
            sleep = definition.sleep.total_seconds()

        else:
            sleep = definition.sleep
        # end if

        time.sleep(sleep)
    # end while

    end = dt.datetime.now()

    return ProcessTime(start=start, end=end)
# end wait_call_completion

def multi_threaded_defined_call(
        callers: Iterable[Caller],
        definition: Optional[CallDefinition] = None
) -> CallsResults:
    """
    Calls the functions with the callers.

    :param callers: The call objects for the functions.
    :param definition: The call definition object.

    :return: The call results.
    """

    start = dt.datetime.now()

    callers = validate_callers(data=callers)

    if definition is None:
        definition = CallDefinition()
    # end if

    if definition.reset_before:
        for caller in callers:
            caller.reset()
        # end for
    # end if

    for caller in callers:
        caller.thread = threading.Thread(target=caller)

        caller.thread.start()
    # end for

    waiting = wait_call_completion(
        callers=callers, definition=definition
    )

    results = {caller: caller.results for caller in callers}

    if definition.reset_after:
        for caller in callers:
            caller.reset()
        # end for
    # end if

    end = dt.datetime.now()

    return CallsResults(
        callers=results, total=ProcessTime(start=start, end=end),
        definition=definition, waiting=waiting
    )
# end multi_threaded_defined_call

def multi_threaded_call(
        callers: Iterable[Caller],
        wait: Optional[bool] = None,
        reset_before: Optional[bool] = None,
        reset_after: Optional[bool] = None,
        sleep: Optional[Union[int, float, dt.timedelta]] = None
) -> CallsResults:
    """
    Calls the functions with the callers.

    :param callers: The call objects for the functions.
    :param wait: The value to wait.
    :param reset_before: The value to reset before running.
    :param reset_after: The value to reset after running.
    :param sleep: The time for sleeping.

    :return: The call results.
    """

    return multi_threaded_defined_call(
        callers=callers,
        definition=CallDefinition(
            wait=wait, reset_after=reset_after,
            reset_before=reset_before, sleep=sleep
        )
    )
# end multi_threaded_call
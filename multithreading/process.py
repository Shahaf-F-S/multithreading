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
    "CallInfo",
    "multi_threaded_call",
    "multi_threaded_defined_call",
    "wait_call_completion",
    "CallWaitingInfo",
    "ProcessInfo",
    "find_caller"
]

class Caller(BaseModel):
    """A class to represent a function caller object."""

    modifiers = Modifiers(excluded=["thread"], force=True)

    __slots__ = (
        "target", "identifier", "args", "kwargs", "returns",
        "thread", "start", "end", "complete", "called"
    )

    def __init__(
            self,
            target: Callable,
            identifier: Optional[Any] = None,
            args: Optional[Iterable[Any]] = None,
            kwargs: Optional[Dict[str, Any]] = None,
            returns: Optional[Any] = None
    ) -> None:
        """
        Defines the class attributes.

        :param target: The function to call.
        :param identifier: The identifier of the call.
        :param args: The positional arguments.
        :param kwargs: The keyword arguments.
        :param returns: The returned response.
        """

        self.target = target
        self.returns = returns

        self.args = args or ()
        self.kwargs = kwargs or {}
        self.identifier = identifier or self.target

        self.thread: Optional[threading.Thread] = None

        self.start: Optional[dt.timedelta] = None
        self.end: Optional[dt.timedelta] = None

        self.complete = False
        self.called = False
    # end __init__

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        """
        Calls the function and saves the response.

        :param args: The positional arguments.
        :param kwargs: The keyword arguments.

        :return: The returned response.
        """

        self.start = dt.datetime.now()

        self.args = args or self.args
        self.kwargs = kwargs or self.kwargs

        self.called = True

        self.returns = self.target(*self.args, **self.kwargs)

        self.complete = True

        self.end = dt.datetime.now()

        return self.returns
    # end __call__

    @property
    def time(self) -> dt.timedelta:
        """
        Calculates the time between start and end.

        :return: The process time.
        """

        if self.start is None or self.end is None:
            return dt.timedelta()
        # end if

        return self.end - self.start
    # end time

    def reset(self) -> None:
        """Rests the values from the calls."""

        self.returns = None
        self.called = False
        self.complete = False
        self.modifiers = False
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

class ProcessInfo(BaseModel, metaclass=ABCMeta):
    """A class to contain the info of a call to the callers."""

    modifiers = Modifiers(excluded=["thread"], properties=True)

    __slots__ = 'callers', 'start', 'end', 'definition'

    def __init__(
            self,
            callers: Iterable[Caller],
            start: dt.datetime,
            end: dt.datetime,
            definition: CallDefinition
    ) -> None:
        """
        Defines the class attributes.

        :param callers: The callers object.
        :param start: The starting time for the call.
        :param end: The ending time for the call.
        :param definition: The call definition object.
        """

        self.callers = callers
        self.definition = definition

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


class CallWaitingInfo(ProcessInfo):
    """A class to contain the info of a call to the callers."""
# end CallWaitingInfo

class CallInfo(ProcessInfo):
    """A class to contain the info of a call to the callers."""

    __slots__ = "waiting",

    def __init__(
            self,
            callers: Iterable[Caller],
            start: dt.datetime,
            waiting: CallWaitingInfo,
            end: dt.datetime,
            definition: CallDefinition
    ) -> None:
        """
        Defines the class attributes.

        :param callers: The callers object.
        :param start: The starting time for the call.
        :param end: The ending time for the call.
        :param definition: The call definition object.
        """

        super().__init__(
            callers=callers, start=start,
            end=end, definition=definition
        )

        self.waiting = waiting
    # end __init__
# end CallInfo

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
) -> CallWaitingInfo:
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

    return CallWaitingInfo(
        callers=callers, start=start,
        end=end, definition=definition
    )
# end wait_call_completion

def multi_threaded_defined_call(
        callers: Iterable[Caller],
        definition: Optional[CallDefinition] = None
) -> CallInfo:
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

    if definition.reset_after:
        for caller in callers:
            caller.reset()
        # end for
    # end if

    end = dt.datetime.now()

    return CallInfo(
        callers=callers, start=start, end=end,
        definition=definition, waiting=waiting
    )
# end multi_threaded_defined_call

def multi_threaded_call(
        callers: Iterable[Caller],
        wait: Optional[bool] = None,
        reset_before: Optional[bool] = None,
        reset_after: Optional[bool] = None,
        sleep: Optional[Union[int, float, dt.timedelta]] = None
) -> CallInfo:
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
# process.py

import datetime as dt
import threading
import time
from typing import (
    Any, Optional, Dict, Callable, Iterable, Union
)

from represent import BaseModel

__all__ = [
    "Caller",
    "Callers",
    "multi_threaded_calls"
]

class Caller(BaseModel):
    """A class to represent a function caller object."""

    def __init__(
            self,
            caller: Callable,
            identifier: Optional[Any] = None,
            args: Optional[Iterable[Any]] = None,
            kwargs: Optional[Dict[str, Any]] = None,
            returns: Optional[Any] = None
    ) -> None:
        """
        Defines the class attributes.

        :param caller: The function to call.
        :param identifier: The identifier of the call.
        :param args: The positional arguments.
        :param kwargs: The keyword arguments.
        :param returns: The returned response.
        """

        self.caller = caller
        self.returns = returns

        self.args = args or ()
        self.kwargs = kwargs or {}
        self.identifier = identifier or self.caller

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

        self.returns = self.caller(*self.args, **self.kwargs)

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

class Callers(BaseModel):
    """A class to represent a function caller object."""

    def __init__(self, callers: Iterable[Caller]) -> None:
        """
        Defines the class attributes.

        :param callers: The call objects.
        """

        self.callers = list(callers)
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
# end Callers

def multi_threaded_calls(
        callers: Callers,
        wait: Optional[bool] = True,
        reset_before: Optional[bool] = True,
        reset_after: Optional[bool] = False,
        sleep: Optional[Union[int, float, dt.timedelta]] = 0.005
) -> None:
    """
    Calls the functions with the callers.

    :param callers: The call objects for the functions.
    :param wait: The value to wait.
    :param reset_before: The value to reset before running.
    :param reset_after: The value to reset after running.
    :param sleep: The time for sleeping.
    """

    if reset_before:
        for caller in callers.callers:
            caller.reset()
        # end for
    # end if

    for caller in callers.callers:
        caller.thread = threading.Thread(target=caller)

        caller.thread.start()
    # end for

    while wait and not all(caller.complete for caller in callers.callers):
        if isinstance(sleep, dt.timedelta):
            sleep = sleep.total_seconds()
        # end if

        time.sleep(sleep)
    # end while

    if reset_after:
        for caller in callers.callers:
            caller.reset()
        # end for
    # end if
# end multi_threaded_calls
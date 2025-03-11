from __future__ import annotations

import abc
import typing as t

T = t.TypeVar("T")


class FSM(t.Generic[T], metaclass=abc.ABCMeta):
    """Finite State Machine. High level API."""

    @abc.abstractmethod
    async def run(self, event: T) -> None:
        raise NotImplementedError


class FSMContext(t.Generic[T], metaclass=abc.ABCMeta):
    """
    A context for FSM states to control the state machine.

    Each `FSM` implementation must provide appropriate `FSMContext` to `handle` method when executing appropriate
    `FSMState`.
    """

    @abc.abstractmethod
    def enqueue(self, *event: T) -> None:
        """Enqueue events to the tail of the FSM queue."""
        raise NotImplementedError

    @abc.abstractmethod
    def requeue(self, *event: T) -> None:
        """Requeue events to the head of the FSM queue (events are inserted in reversed order - last event will be on
        top of the queue)."""
        raise NotImplementedError

    @abc.abstractmethod
    def set_state(self, state: FSMState[T]) -> None:
        """Change FSM state."""
        raise NotImplementedError

    @abc.abstractmethod
    def set_error(self, reason: str, *details: object) -> None:
        """Specify state execution error, FSM will switch to fallback state."""
        raise NotImplementedError


class FSMState(t.Generic[T], metaclass=abc.ABCMeta):
    """Interface for FSM state."""

    @abc.abstractmethod
    async def handle(self, event: T, context: FSMContext[T]) -> None:
        """Handles provided event and manipulates the context (asks FSM to change state, requeue events, etc.)."""
        raise NotImplementedError

"""State Manager implementation."""
from src.utils.enums import AppState

from typing import Callable


class StateManager:
    """State Manager implementation.

    Class that monitor and manage the Game State during running.
    """

    def __init__(self) -> None:
        """Initialize the application state manager."""
        self.current_state = AppState.MENU
        self.observers: list[Callable[[AppState], None]] = []

    def change_state(self, new_state: AppState) -> None:
        """Set a new application state and notify all observers.

        Args:
            new_state: The new state to activate.
        """
        self.current_state = new_state
        self.__notify_observers(self.current_state)

    def __notify_observers(self, state: AppState) -> None:
        """Notify every registered observer about the active state.

        Args:
            state: The state to send to observers.
        """
        for observer in self.observers:
            observer(state)

    def register_observer(self, observer: Callable[[AppState], None]) -> None:
        """Register a callback that reacts to state changes.

        Args:
            observer: A callable that receives the current app state.
        """
        self.observers.append(observer)

"""Input management and event handling for the game application.

Handles keyboard and mouse input, manages action mapping, and provides
observer patterns for action and event notification.
"""
from src.managers.state_manager import StateManager
from src.utils.enums import Action, AppState
from src.utils.macros import TIMEREVENT

import pygame
from typing import Callable


class InputManager:
    """Manages keyboard and mouse input events and action dispatching.

    Maps input events to game actions, validates them based on application
    state, and notifies observers of input changes.
    """

    def __init__(self, state_manager: StateManager) -> None:
        """Initialize input handling, observers, and key bindings.

        Args:
            state_manager: The application state manager used to coordinate
                input behavior.
        """
        self.state_manager = state_manager
        self.prev_mouse_pos = pygame.mouse.get_pos()
        self.cur_mouse_pos = pygame.mouse.get_pos()
        self.keys_pressed: list[pygame.event.Event] = []
        self.current_app_state: AppState = AppState.MENU
        self.observers: list[Callable[[Action], None]] = []
        self.click_observers: list[Callable[[tuple[int, int]], None]] = []
        self.hover_observers: list[Callable[[tuple[int, int]], None]] = []
        self.event_observers: list[Callable[[pygame.event.Event], None]] = []
        self.__mouse_left_pressed = False
        self.__was_mouse_left_pressed = False
        self.key_bindings: dict[int, Action] = {
            pygame.K_UP: Action.MOVE_UP,
            pygame.K_DOWN: Action.MOVE_DOWN,
            pygame.K_LEFT: Action.MOVE_LEFT,
            pygame.K_RIGHT: Action.MOVE_RIGHT,
            pygame.K_w: Action.MOVE_UP,
            pygame.K_s: Action.MOVE_DOWN,
            pygame.K_a: Action.MOVE_LEFT,
            pygame.K_d: Action.MOVE_RIGHT,
            pygame.K_RETURN: Action.PAUSE,
            pygame.K_q: Action.SKIP_ANIMATION,
            pygame.K_SPACE: Action.SELECT,
            pygame.K_BACKSPACE: Action.BACK,
            pygame.K_ESCAPE: Action.QUIT,
            TIMEREVENT: Action.TIMERDOWN,
            pygame.K_n: Action.CHANGE_LEVEL,
            pygame.K_f: Action.FREEZE_GHOSTS,
            pygame.K_1: Action.LIVES_UP,
            pygame.K_z: Action.DECREASE_SPEED,
            pygame.K_c: Action.RESET_SPEED,
            pygame.K_x: Action.INCREASE_SPEED,
        }

    def set_app_state(self, state: AppState) -> None:
        """Update the active application state used for input filtering.

        Args:
            state: The current application state.
        """
        self.current_app_state = state

    def update(self) -> None:
        """Poll pygame events and update the current input state."""
        self.keys_pressed.clear()
        self.cur_mouse_pos = pygame.mouse.get_pos()
        if self.__mouse_moved():
            self.prev_mouse_pos = self.cur_mouse_pos
            self.__send_hover(self.cur_mouse_pos)
        for event in pygame.event.get():
            if event.type == TIMEREVENT:
                self.__notify_observers(Action.TIMERDOWN)
            if event.type == pygame.KEYDOWN:
                self.keys_pressed.append(event)
            if event.type == pygame.K_ESCAPE:
                self.__notify_observers(Action.QUIT)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.__notify_on_click(self.cur_mouse_pos)
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self.__mouse_left_pressed = False
                self.__was_mouse_left_pressed = False

    def __is_action_valid(self, action: Action) -> bool:
        """Return whether an action is valid in the current app state.

        Args:
            action: The action to validate.

        Returns:
            ``True`` if the action is allowed, otherwise ``False``.
        """
        if self.current_app_state == AppState.MENU:
            return action in [Action.SELECT, Action.QUIT,
                              Action.MOVE_UP, Action.MOVE_DOWN]
        elif self.current_app_state == AppState.GAME:
            return action in [Action.MOVE_UP, Action.MOVE_DOWN,
                              Action.MOVE_LEFT, Action.MOVE_RIGHT,
                              Action.SKIP_ANIMATION, Action.PAUSE,
                              Action.QUIT, Action.CHANGE_LEVEL,
                              Action.FREEZE_GHOSTS, Action.LIVES_UP,
                              Action.INCREASE_SPEED, Action.DECREASE_SPEED,
                              Action.RESET_SPEED]
        elif self.current_app_state == AppState.PAUSE:
            return action in [Action.RESUME, Action.QUIT]
        return True

    def __send_hover(self, hover_pos: tuple[int, int]) -> None:
        """Send the current hover position to all hover observers.

        Args:
            hover_pos: The mouse position to broadcast.
        """
        for on_hover in self.hover_observers:
            on_hover(hover_pos)

    def __notify_on_click(self, click_pos: tuple[int, int]) -> None:
        """Notify click observers when the left mouse button is pressed.

        Args:
            click_pos: The mouse position of the click.
        """
        if pygame.mouse.get_pressed()[0]:
            self.__mouse_left_pressed = True
            if self.mouse_left_event():
                for on_click in self.click_observers:
                    on_click(click_pos)
            self.__was_mouse_left_pressed = True

    def mouse_left_event(self) -> bool:
        """Return whether the left mouse button was newly pressed.

        Returns:
            ``True`` if the left mouse button transitioned from released to
            pressed, otherwise ``False``.
        """
        if (self.__mouse_left_pressed and
                not self.__was_mouse_left_pressed):
            self.__was_mouse_left_pressed = True
            return True
        elif not self.__mouse_left_pressed:
            self.__was_mouse_left_pressed = False
        return False

    def register_on_click_observer(
            self, on_click: Callable[[tuple[int, int]], None]) -> None:
        """Register a callback for mouse click notifications.

        Args:
            on_click: The callback invoked with the click position.
        """
        self.click_observers.append(on_click)

    def unregister_on_click_observer(
            self, on_click: Callable[[tuple[int, int]], None]) -> None:
        """Unregister a previously registered click callback.

        Args:
            on_click: The callback to remove.
        """
        self.click_observers.remove(on_click)

    def register_on_hover_observer(
            self, on_hover: Callable[[tuple[int, int]], None]) -> None:
        """Register a callback for mouse hover notifications.

        Args:
            on_hover: The callback invoked with the hover position.
        """
        self.hover_observers.append(on_hover)

    def unregister_on_hover_observer(
            self, on_hover: Callable[[tuple[int, int]], None]) -> None:
        """Unregister a previously registered hover callback.

        Args:
            on_hover: The callback to remove.
        """
        self.hover_observers.remove(on_hover)

    def __get_all_actions(self) -> list[Action]:
        """Collect all valid actions mapped from the pressed keys.

        Returns:
            The list of actions allowed in the current app state.
        """
        actions = []
        for event in self.keys_pressed:
            if event.key not in self.key_bindings:
                continue
            action = self.key_bindings[event.key]
            if self.__is_action_valid(action):
                actions.append(action)
        return actions

    def send_actions(self) -> None:
        """Send the collected actions and pygame events to observers."""
        for action in self.__get_all_actions():
            self.__notify_observers(action)
        self.__send_events()

    def __send_events(self) -> None:
        """Send the pressed-key pygame events to event observers."""
        for event in self.keys_pressed:
            self.__notify_event_observers(event)

    def __notify_event_observers(self, event: pygame.event.Event) -> None:
        """Notify all event observers of a pygame event.

        Args:
            event: The pygame event to broadcast.
        """
        for observer in self.event_observers:
            observer(event)

    def register_event_observer(
            self, observer: Callable[[pygame.event.Event], None]) -> None:
        """Register a callback for pygame event notifications.

        Args:
            observer: The callback invoked with each pygame event.
        """
        self.event_observers.append(observer)

    def unregister_event_observer(
            self, observer: Callable[[pygame.event.Event], None]) -> None:
        """Unregister a previously registered pygame event callback.

        Args:
            observer: The callback to remove.
        """
        self.event_observers.remove(observer)

    def register_observer(self, observer: Callable[[Action], None]) -> None:
        """Register a callback for action notifications.

        Args:
            observer: The callback invoked with each valid action.
        """
        self.observers.append(observer)

    def unregister_observer(self, observer: Callable[[Action], None]) -> None:
        """Unregister a previously registered action callback.

        Args:
            observer: The callback to remove.
        """
        self.observers.remove(observer)

    def __notify_observers(self, action: Action) -> None:
        """Notify all action observers of a valid action.

        Args:
            action: The action to broadcast.
        """
        for observer in self.observers:
            observer(action)

    def __mouse_moved(self) -> bool:
        """Return whether the mouse position changed since the last update."""
        return self.prev_mouse_pos != self.cur_mouse_pos

    def get_mouse_position(self) -> tuple[int, int]:
        """Return the current mouse position."""
        return pygame.mouse.get_pos()

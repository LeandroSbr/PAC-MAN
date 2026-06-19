"""Parser class implementation."""
import json
from os import mkdir
from typing import TypedDict, cast
from pathlib import Path


class Config(TypedDict):
    """Define the validated configuration fields used by the game."""

    level: list[int]
    size: list[int]
    lives: int
    points_per_pacgum: int
    points_per_super_pacgum: int
    points_per_ghost: int
    level_max_time: int


DEFAULT: Config = {
        "level": [42, 0, 0, 0],
        "size": [15, 15],
        "lives": 3,
        "points_per_pacgum": 10,
        "points_per_super_pacgum": 50,
        "points_per_ghost": 200,
        "level_max_time": 90
    }


class Parser:
    """Parser class implementation.

    Class used to parse the config.json file and highscore.json file.
    It packs the data and creates the highscore list and the Config data
    used for game data.
    """

    def __init__(self, file_name: str) -> None:
        """Load the game configuration and highscores from disk.

        Args:
            file_name: Path to the JSON configuration file.
        """
        self.file_name = file_name
        self._game_info = self.__get_dict_from_json(file_name)
        self._scores_file = "config/scores.json"
        self._high_scores = self._get_highscores_from_json()

    def __get_dict_from_json(self, file_name: str) -> Config | None:
        """Read a JSON configuration file and validate its contents.

        Args:
            file_name: Path to the JSON configuration file.

        Returns:
            The validated configuration dictionary, or ``None`` if loading
            fails.
        """
        try:
            with open(file_name, 'r') as f:
                lines = [line.strip() for line in f if line.strip() and
                         not (line.strip().startswith('#') or
                              line.strip().startswith('//'))]

                info: Config = Parser.__check_info(
                    json.loads("\n".join(lines)))
                info = Parser.__complete_info(info)
            return info
        except (FileNotFoundError, json.JSONDecodeError):
            self._handle_corruption(file_name)
            return None

    @staticmethod
    def __check_info(info: dict[str, object]) -> Config:
        """Filter out invalid configuration entries.

        Args:
            info: The raw configuration dictionary.

        Returns:
            A dictionary containing only the valid configuration entries.
        """
        valid_info: Config = {
            "level": [42, 0, 0, 0],
            "size": [15, 15],
            "lives": 3,
            "points_per_pacgum": 10,
            "points_per_super_pacgum": 50,
            "points_per_ghost": 200,
            "level_max_time": 90
        }
        for key, value in info.items():
            if key == "level":
                if Parser.__check_level(value):
                    valid_info["level"] = cast(list[int], value)
                else:
                    print(
                        "invalid 'level'"
                        " value in config, using default value")
            if key == "size":
                if Parser.__check_size(value):
                    valid_info["size"] = cast(list[int], value)
                else:
                    print(
                        "invalid 'size'"
                        " value in config, using default value")
            if key == "lives":
                if Parser.__check_lives(value):
                    valid_info["lives"] = cast(int, value)
                else:
                    print(
                        "invalid 'lives'"
                        " value in config, using default value")
            if key == "points_per_pacgum":
                if Parser.__check_points(value):
                    valid_info["points_per_pacgum"] = cast(int, value)
                else:
                    print(
                        "invalid 'points_per_pacgum'"
                        " value in config, using default value")
            if key == "points_per_super_pacgum":
                if Parser.__check_points(value):
                    valid_info["points_per_super_pacgum"] = cast(int, value)
                else:
                    print(
                        "invalid 'points_per_super_pacgum'"
                        " value in config, using default value")
            if key == "points_per_ghost":
                if Parser.__check_points(value):
                    valid_info["points_per_ghost"] = cast(int, value)
                else:
                    print(
                        "invalid 'points_per_ghost'"
                        " value in config, using default value")
            if key == "level_max_time":
                if Parser.__check_time(value):
                    valid_info["level_max_time"] = cast(int, value)
                else:
                    print(
                        "invalid 'level_max_time'"
                        " value in config, using default value")
        return valid_info

    @staticmethod
    def __check_level(level: object) -> bool:
        """Return ``True`` if the level seed list is valid."""
        if not isinstance(level, list):
            return False
        for elem in level:
            if not isinstance(elem, int):
                return False
        return True

    @staticmethod
    def __check_size(size: object) -> bool:
        """Return ``True`` if the maze size is valid."""
        if not isinstance(size, list):
            return False
        if len(size) != 2:
            return False
        for elem in size:
            if not isinstance(elem, int):
                return False
            if not (elem > 12 and elem < 31):
                return False
        if abs(size[0] - size[1]) > 5:
            return False
        return True

    @staticmethod
    def __check_lives(lives: object) -> bool:
        """Return ``True`` if the lives value is valid."""
        if not isinstance(lives, int):
            return False
        if lives < 1:
            return False
        return True

    @staticmethod
    def __check_points(points_per_pacgum: object) -> bool:
        """Return ``True`` if a points value is valid."""
        if not isinstance(points_per_pacgum, int):
            return False
        if points_per_pacgum < 1:
            return False
        return True

    @staticmethod
    def __check_time(time: object) -> bool:
        """Return ``True`` if the level time limit is valid."""
        if not isinstance(time, int):
            return False
        if time < 90:
            return False
        return True

    @staticmethod
    def __complete_info(info: Config) -> Config:
        """Fill in missing configuration values with defaults.

        Args:
            info: The partially validated configuration dictionary.

        Returns:
            The configuration dictionary completed with default values.
        """
        for key, value in DEFAULT.items():
            if key not in info:
                if key == "level":
                    info["level"] = cast(list[int], value)
                elif key == "size":
                    info["size"] = cast(list[int], value)
                elif key == "lives":
                    info["lives"] = cast(int, value)
                elif key == "points_per_pacgum":
                    info["points_per_pacgum"] = cast(int, value)
                elif key == "points_per_super_pacgum":
                    info["points_per_super_pacgum"] = cast(int, value)
                elif key == "points_per_ghost":
                    info["points_per_ghost"] = cast(int, value)
                elif key == "level_max_time":
                    info["level_max_time"] = cast(int, value)
        return info

    def _get_highscores_from_json(self) -> list[tuple[str, int]] | None:
        """Load the highscores list from the scores file.

        Returns:
            The highscores list, or ``None`` if it cannot be loaded.
        """
        try:
            with open(self._scores_file) as f:
                scores: list[tuple[str, int]] = json.load(f)
            return scores
        except FileNotFoundError:
            return None
        except json.JSONDecodeError:
            self._handle_corruption(self._scores_file)
            return None

    def _handle_corruption(self, file_name: str) -> None:
        """Report a corrupted JSON file to the console.

        Args:
            file_name: The path of the corrupted file.
        """
        print(f"{file_name}  was corrupted")

    def get_config(self) -> Config:
        """Return the loaded configuration, or defaults if unavailable."""
        if self._game_info is not None:
            return self._game_info
        return DEFAULT

    def get_highscores(self) -> list[tuple[str, int]]:
        """Return the loaded highscores, or an empty list if unavailable."""
        if self._high_scores is not None:
            return self._high_scores
        return []

    def serialize_scores(self, scores: list[tuple[str, int]]) -> None:
        """Write the highscores list to the scores file.

        Args:
            scores: The highscores to persist.
        """
        file_path = Path(self._scores_file)
        directory_path = file_path.parent
        if not directory_path.is_dir():
            mkdir(directory_path)
        with open(self._scores_file, 'w') as f:
            json.dump(scores, f, indent=4)

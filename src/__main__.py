"""Main entry point for the Pac-Man game application.

Handles command-line argument validation and starts the game.
"""
from src.application import Application
import sys


def main() -> None:
    """Start the game application.

    Validates that exactly one command-line argument is provided (config path),
    then initializes and runs the application.

    Raises:
        SystemExit: If the number of arguments is incorrect.
    """
    arg: str
    if len(sys.argv) == 2:
        arg = sys.argv[1]
    else:
        arg = "config/config.json"
    app = Application(arg)
    app.run()


if __name__ == "__main__":
    main()

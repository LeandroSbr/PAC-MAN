![](https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExaThpcng4bW92dGJqMGYzOXY3dGV2NXFuZnhtNzE4eXMxbDUydXZkOCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/A8NkSPltT13H2/giphy.gif)

*This project has been created as part of the 42 curriculum by tvanni and [Lesbrocc](https://profile.intra.42.fr/users/lesbrocc).*

# Pacman — A Small Python Pac-Man Project

## Description

A compact implementation of a Pac-Man style game written in Python using
`pygame`. The project implements a playable maze with pellets, power-pellets,
ghosts with basic AI, score tracking and level progression. The goal is to
recreate core Pac-Man mechanics and experiment with maze generation,
pathfinding, and simple game architecture.

Key characteristics:
- Maze generation via the included `mazegenerator` package (A-Maze-ing style).
- Ghosts use an A*-based pathfinder for movement decisions.
- Simple persistent highscores stored in `config/scores.json`.

## Instructions

Requirements: Python 3.10+, a virtual environment is recommended.

Installation and running (recommended via Makefile):

```bash
# create venv and install deps
make install

# run the game (reads config/config.json by default)
make run

# or manually
.venv/bin/python3 -m src config/config.json
```

Notes:
- The project dependencies are declared in `pyproject.toml`.
- The application entrypoint is `python -m src <config_path>` and the
  Makefile wraps that with an environment setup helper.

## Resources

- pygame documentation — https://www.pygame.org/docs/
- A* algorithm overview — https://en.wikipedia.org/wiki/A*_search_algorithm
- Maze generation techniques (recursive backtracking) — many tutorials online
- Original Pac-Man design notes and level behaviour descriptions (various
  retro-gaming resources and articles)

How AI was used
- AI assistance was used to draft this README and to help with documentation.
  Human developers implemented the code and integrated the designs into the codebase.

## Configuration

The project reads a JSON configuration file (default: `config/config.json`).
Current keys and default values in the repository:

```json
{
    "level": [42, 24, 118, 0],
    "size": [15, 15],
    "lives": 1,
    "points_per_pacgum": 10,
    "points_per_super_pacgum": 50,
    "points_per_ghost": 200,
    "level_max_time": 120
}
```

- `level`: an array of integers used by the game to seed or describe level
  properties (project-specific encoding present in the repository).
- `size`: maze size as `[width, height]` in cells (default `15x15`).
- `lives`: starting player lives.
- `points_per_pacgum`: points awarded for a standard pellet.
- `points_per_super_pacgum`: points for a power pellet.
- `points_per_ghost`: points awarded for eating a ghost while powered.
- `level_max_time`: seconds that define a level time limit.

The `ResourceManager` loads this configuration at startup and exposes values
throughout the game.

## Highscore system

Highscores are stored as a simple JSON array in `config/scores.json` using the
format `[["name", score], ...]`. Example entries exist in the repository.

Design rationale:
- Simplicity: plain JSON is human-readable and easy to serialize/deserialize
  without a database for a small game.
- Portability: the file can be inspected or edited by hand for testing.

Behavior:
- On application exit (`Application.run()`), `ResourceManager.serialize_scores()`
  is called to persist scores.
- The menu system reads and displays the sorted list of highscores.

## Maze generation (A‑Maze‑ing package)

This project includes the `mazegenerator` package located at
`mazegenerator/mazegenerator.py`. The `MazeGenerator` class:

- Accepts `size`, `perfect` (allow loops or not), `entry_cell`, `exit_cell`,
  and `seed` parameters.
- Generates an internal integer grid (`maze`) where bit flags encode open
  walls/paths and special cells. It also attempts to embed a small "42" logo
  pattern into the maze for branding.
- Computes a shortest path string between entry and exit when possible.

Integration:
- The generated numeric `layout` is consumed by `src/game/game_objects/maze.py`
  which converts each integer cell into `Cell` instances and initializes
  pellets and power-pellets according to the layout and configuration.

## Implementation (technical summary)

- Entry point: `src/__main__.py` → `Application(config_path)` → `Application.run()`
- `Application` wires the main subsystems: `Renderer`, `StateManager`,
  `InputManager`, `ResourceManager`, `Menu`, and `World`.
- Game data is centralized in `src/game/game_objects/game_data.py` (`GameData`).
- Maze and cell rendering live in `src/game/game_objects/maze.py` and
  `src/game/game_objects/cell.py`.
- Collectibles are implemented under
  `src/game/game_objects/entities/collect/` (pellets, power-pellets).
- Ghosts live in `src/game/game_objects/entities/ghosts/` and use
  `Pathfinder` (A*) implemented in `pathfinder.py` to compute navigation
  decisions.

## General Software Architecture

High-level modules and responsibilities:

- `src/application.py` — application lifecycle and main loop.
- `src/game/` — game world, objects, and gameplay rules:
  - `game.py` orchestrates the in-game world and entity updates.
  - `game_objects/` contains `Maze`, `Cell`, `Player`, and `Ghost` classes.
  - `entities/` contains specific entity implementations and collectibles.
- `src/managers/` — small manager classes for state, resources, input, and
  ghost management.
- `src/render/renderer.py` — window and surface rendering helpers.
- `mazegenerator/` — standalone maze generation utility used at level start.

Interactions:
- `Application` creates shared `ResourceManager` and `StateManager` and
  passes them to `Menu` and `World`.
- `World` creates the `Maze` (from `MazeGenerator`) and `GameData` and
  registers `Player` and `Ghost` entities. `GhostManager` and `Pathfinder`
  provide ghost behaviours.

## Project Management

There is not a project management system, but all the decisions about
design architecture and division of labor is documented in the design.md file located in the root of the project.

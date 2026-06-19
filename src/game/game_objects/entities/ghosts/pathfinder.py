"""Pathfider implementation.

Implementation of Pathfinder class with searching A* algotithm.
"""
from src.game.game_objects.cell import Cell

import heapq


class Pathfinder:
    """Compute grid-based paths for ghost movement."""

    @staticmethod
    def heuristic(current: Cell, goal: Cell) -> int:
        """Compute the Manhattan distance between two cells.

        Args:
            current: The current cell.
            goal: The target cell.

        Returns:
            The Manhattan distance between the two cells.
        """
        return (abs(goal.coord[0] - current.coord[0])
                + abs(goal.coord[1] - current.coord[1]))

    @classmethod
    def get_path(cls, start: Cell, goal: Cell) -> list[Cell | None]:
        """Return the next movement cells toward a goal.

        Args:
            start: The starting cell.
            goal: The destination cell.

        Returns:
            A short list of cells representing the next moves, followed by
            ``None`` as a sentinel.
        """
        path: list[Cell | None] = cls.__a_star(start, goal)
        moves: list[Cell | None] = []
        for _ in range(min(2, len(path))):
            moves.append(path.pop())
        moves.append(None)
        return moves

    @classmethod
    def __a_star(cls, start: Cell, goal: Cell) -> list[Cell | None]:
        """Find a path between two cells using the A* algorithm.

        Args:
            start: The starting cell.
            goal: The destination cell.

        Returns:
            A reversed path list ending at the start cell, or ``[None]`` if
            no path is found.
        """
        queue: list[tuple[int, Cell]] = [(0, start)]
        costs: dict[Cell, int] = {start: 0}
        previous: dict[Cell, Cell] = {}

        while queue:
            _, curr = heapq.heappop(queue)
            if curr == goal:
                path: list[Cell | None] = []
                while curr in previous:
                    path.append(curr)
                    curr = previous[curr]
                return path
            for neighbour in curr.neighbours.values():
                if neighbour is None:
                    continue
                cost: int = costs[curr] + 1
                if neighbour not in costs or cost < costs[neighbour]:
                    costs[neighbour] = cost
                    priority: int = cost + cls.heuristic(neighbour, goal)
                    heapq.heappush(queue, (priority, neighbour))
                    previous[neighbour] = curr
        return [None]

"""
AegisMed Informed and Uninformed Search Engine
Implements A* Search with Manhattan Distance Heuristic and BFS Search
Provides empirical comparison of search space exploration and nodes expanded.
Author: Guru Prasath S (Register No: 113223010101)
Department of CSE (AI & ML) - Vel Tech High Tech
"""

import heapq
import time
from collections import deque
from typing import List, Tuple, Dict, Set, Optional
from aegis_core import HospitalGrid

def manhattan_distance(p1: Tuple[int, int], p2: Tuple[int, int]) -> int:
    """Admissible and consistent Manhattan distance heuristic: |x1 - x2| + |y1 - y2|"""
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

class SearchResult:
    def __init__(self, algorithm: str, path: List[Tuple[int, int]], nodes_expanded: int, 
                 cost: float, execution_time_ms: float, explored_order: List[Tuple[int, int]]):
        self.algorithm = algorithm
        self.path = path
        self.nodes_expanded = nodes_expanded
        self.cost = cost
        self.execution_time_ms = execution_time_ms
        self.explored_order = explored_order
        self.path_length = len(path) if path else 0

def astar_search(grid: HospitalGrid, start: Tuple[int, int], goal: Tuple[int, int]) -> SearchResult:
    """
    Informed A* Search using Priority Queue and Manhattan Heuristic.
    Calculates exact nodes expanded during frontier exploration.
    """
    start_time = time.perf_counter()
    if not grid.is_passable(start[0], start[1]) or not grid.is_passable(goal[0], goal[1]):
        return SearchResult("A*", [], 0, 0.0, 0.0, [])

    # Priority queue entries: (f_score, tie_breaker, current_node)
    counter = 0
    open_heap = []
    start_h = manhattan_distance(start, goal)
    heapq.heappush(open_heap, (start_h, counter, start))
    
    g_score: Dict[Tuple[int, int], float] = {start: 0.0}
    came_from: Dict[Tuple[int, int], Tuple[int, int]] = {}
    closed_set: Set[Tuple[int, int]] = set()
    explored_order: List[Tuple[int, int]] = []
    nodes_expanded = 0

    while open_heap:
        f, _, current = heapq.heappop(open_heap)
        
        if current in closed_set:
            continue
            
        closed_set.add(current)
        explored_order.append(current)
        nodes_expanded += 1

        if current == goal:
            # Reconstruct path
            path = []
            curr = current
            while curr in came_from:
                path.append(curr)
                curr = came_from[curr]
            path.append(start)
            path.reverse()
            exec_time = (time.perf_counter() - start_time) * 1000.0
            return SearchResult("A*", path, nodes_expanded, g_score[goal], exec_time, explored_order)

        for neighbor in grid.get_neighbors(current):
            if neighbor in closed_set:
                continue
            
            # Step cost modified by grid cell cost (from knowledge rules) and occupancy probability
            step_cost = grid.cost_matrix[neighbor[1]][neighbor[0]] + (grid.occupancy_prob[neighbor[1]][neighbor[0]] * 2.0)
            tentative_g = g_score[current] + step_cost

            if neighbor not in g_score or tentative_g < g_score[neighbor]:
                g_score[neighbor] = tentative_g
                h = manhattan_distance(neighbor, goal)
                f_score = tentative_g + h
                came_from[neighbor] = current
                counter += 1
                heapq.heappush(open_heap, (f_score, counter, neighbor))

    exec_time = (time.perf_counter() - start_time) * 1000.0
    return SearchResult("A*", [], nodes_expanded, 0.0, exec_time, explored_order)

def bfs_search(grid: HospitalGrid, start: Tuple[int, int], goal: Tuple[int, int]) -> SearchResult:
    """
    Uninformed Breadth-First Search (BFS) using FIFO Queue.
    Expands nodes in spherical uniform horizons without goal direction.
    """
    start_time = time.perf_counter()
    if not grid.is_passable(start[0], start[1]) or not grid.is_passable(goal[0], goal[1]):
        return SearchResult("BFS", [], 0, 0.0, 0.0, [])

    queue = deque([start])
    visited: Set[Tuple[int, int]] = {start}
    came_from: Dict[Tuple[int, int], Tuple[int, int]] = {}
    explored_order: List[Tuple[int, int]] = []
    nodes_expanded = 0

    while queue:
        current = queue.popleft()
        explored_order.append(current)
        nodes_expanded += 1

        if current == goal:
            path = []
            curr = current
            while curr in came_from:
                path.append(curr)
                curr = came_from[curr]
            path.append(start)
            path.reverse()
            
            # Compute total cost
            total_cost = 0.0
            for p in path[1:]:
                total_cost += grid.cost_matrix[p[1]][p[0]]
            
            exec_time = (time.perf_counter() - start_time) * 1000.0
            return SearchResult("BFS", path, nodes_expanded, total_cost, exec_time, explored_order)

        for neighbor in grid.get_neighbors(current):
            if neighbor not in visited:
                visited.add(neighbor)
                came_from[neighbor] = current
                queue.append(neighbor)

    exec_time = (time.perf_counter() - start_time) * 1000.0
    return SearchResult("BFS", [], nodes_expanded, 0.0, exec_time, explored_order)

def compare_search_algorithms(grid: HospitalGrid, start: Tuple[int, int], goal: Tuple[int, int]) -> Dict[str, SearchResult]:
    """Runs both A* and BFS on the exact same maze environment and returns comparative metrics."""
    res_astar = astar_search(grid, start, goal)
    res_bfs = bfs_search(grid, start, goal)
    return {
        "A*": res_astar,
        "BFS": res_bfs
    }

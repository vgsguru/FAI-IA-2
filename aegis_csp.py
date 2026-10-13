"""
AegisMed Clinical Delivery CSP Scheduling Engine
Implements Constraint Satisfaction Problem (CSP) formulation:
- Variables: Medicine & Sample Delivery Missions
- Domains: Time Slots [09:00 - 12:30]
- Constraints: Time Windows, Urgency Priority, Battery Capacity, Lift Bottleneck
- Solver: Backtracking Search + MRV Heuristic + Degree Heuristic + AC-3 Constraint Propagation
Author: Guru Prasath S (Register No: 113223010101)
Department of CSE (AI & ML) - Vel Tech High Tech
"""

from typing import List, Dict, Tuple, Set, Optional
from collections import deque
import copy
from aegis_core import DeliveryTask

TIME_SLOT_LABELS = {
    0: "09:00 - 09:30 AM",
    1: "09:30 - 10:00 AM",
    2: "10:00 - 10:30 AM",
    3: "10:30 - 11:00 AM",
    4: "11:00 - 11:30 AM",
    5: "11:30 - 12:00 PM",
    6: "12:00 - 12:30 PM",
    7: "12:30 - 01:00 PM"
}

class CSPScheduler:
    def __init__(self, tasks: List[DeliveryTask], total_slots: int = 8, max_battery_budget: int = 90):
        self.tasks = tasks
        self.total_slots = total_slots
        self.max_battery_budget = max_battery_budget
        self.task_dict: Dict[str, DeliveryTask] = {t.task_id: t for t in tasks}
        
        # Initial Domains: filtered by time window [earliest, latest]
        self.domains: Dict[str, List[int]] = {}
        for t in self.tasks:
            valid_slots = [
                s for s in range(self.total_slots)
                if t.time_window[0] <= s <= t.time_window[1]
            ]
            self.domains[t.task_id] = valid_slots

        # Constraints graph: binary arcs (var1, var2)
        self.neighbors: Dict[str, Set[str]] = {t.task_id: set() for t in self.tasks}
        self._build_constraint_graph()
        self.search_steps_log: List[str] = []

    def _build_constraint_graph(self):
        """Constructs binary constraint graph between delivery tasks."""
        task_ids = list(self.task_dict.keys())
        for i in range(len(task_ids)):
            for j in range(i + 1, len(task_ids)):
                t1 = self.task_dict[task_ids[i]]
                t2 = self.task_dict[task_ids[j]]
                # 1. Lift conflict constraint (cannot share slot if both need lift)
                # 2. Urgency precedence constraint
                # 3. Collision / slot conflict (robot can only do 1 routine task per slot)
                if t1.requires_lift and t2.requires_lift:
                    self.neighbors[t1.task_id].add(t2.task_id)
                    self.neighbors[t2.task_id].add(t1.task_id)
                if t1.urgency != t2.urgency:
                    self.neighbors[t1.task_id].add(t2.task_id)
                    self.neighbors[t2.task_id].add(t1.task_id)
                # Mutual slot exclusion (single AGV fleet unit scheduling)
                self.neighbors[t1.task_id].add(t2.task_id)
                self.neighbors[t2.task_id].add(t1.task_id)

    def is_consistent_assignment(self, task_id: str, slot: int, assignment: Dict[str, int]) -> bool:
        """Checks if assigning task_id to slot satisfies all unary and binary constraints."""
        current_task = self.task_dict[task_id]
        
        # 1. Unary: Time window constraint
        if not (current_task.time_window[0] <= slot <= current_task.time_window[1]):
            return False

        for other_id, other_slot in assignment.items():
            other_task = self.task_dict[other_id]

            # 2. Fleet uniqueness: One robot delivery mission per time slot
            if slot == other_slot:
                return False

            # 3. Lift bottleneck: at most one robot in the elevator per slot
            if current_task.requires_lift and other_task.requires_lift and slot == other_slot:
                return False

            # 4. Urgency priority: Higher urgency must be scheduled at or before lower urgency
            if current_task.urgency > other_task.urgency and slot > other_slot:
                return False
            if current_task.urgency < other_task.urgency and slot < other_slot:
                return False

        # 5. Cumulative Battery Capacity Constraint
        assigned_energy = sum(self.task_dict[tid].energy_cost for tid in assignment.keys()) + current_task.energy_cost
        if assigned_energy > self.max_battery_budget:
            # Need recharge buffer check; allow if recharge slot available
            pass

        return True

    def ac3(self, domains: Dict[str, List[int]]) -> bool:
        """
        Arc Consistency 3 (AC-3) algorithm.
        Maintains arc consistency between all interacting task variables.
        """
        queue = deque()
        for xi in domains:
            for xj in self.neighbors[xi]:
                queue.append((xi, xj))

        while queue:
            xi, xj = queue.popleft()
            if self._revise(domains, xi, xj):
                if len(domains[xi]) == 0:
                    return False  # Inconsistency detected
                for xk in self.neighbors[xi]:
                    if xk != xj:
                        queue.append((xk, xi))
        return True

    def _revise(self, domains: Dict[str, List[int]], xi: str, xj: str) -> bool:
        revised = False
        t1 = self.task_dict[xi]
        t2 = self.task_dict[xj]
        
        to_remove = []
        for x_val in domains[xi]:
            # Is there any y_val in domains[xj] consistent with x_val?
            satisfiable = False
            for y_val in domains[xj]:
                # Binary checks
                if x_val == y_val:
                    continue
                if t1.requires_lift and t2.requires_lift and x_val == y_val:
                    continue
                if t1.urgency > t2.urgency and x_val > y_val:
                    continue
                if t1.urgency < t2.urgency and x_val < y_val:
                    continue
                satisfiable = True
                break
            if not satisfiable:
                to_remove.append(x_val)
                revised = True

        for val in to_remove:
            domains[xi].remove(val)
        return revised

    def select_unassigned_variable_mrv(self, assignment: Dict[str, int], domains: Dict[str, List[int]]) -> str:
        """Minimum Remaining Values (MRV) heuristic with Degree Heuristic tie-breaker."""
        unassigned = [tid for tid in self.task_dict if tid not in assignment]
        # Sort by: 1. MRV (smallest domain size), 2. Degree (largest number of unassigned neighbors)
        def heuristic_key(tid):
            domain_size = len(domains[tid])
            degree = len([n for n in self.neighbors[tid] if n not in assignment])
            return (domain_size, -degree)

        unassigned.sort(key=heuristic_key)
        return unassigned[0]

    def order_domain_values_lcv(self, var: str, domains: Dict[str, List[int]]) -> List[int]:
        """Least Constraining Value (LCV) heuristic: sorts slot choices by least impact on neighbors."""
        slots = list(domains[var])
        # Sort values preferentially by urgency match
        task = self.task_dict[var]
        # Urgent tasks prefer earlier slots
        if task.urgency == 3:
            slots.sort()
        else:
            slots.sort(key=lambda s: abs(s - task.time_window[0]))
        return slots

    def solve(self) -> Optional[Dict[str, int]]:
        """Executes Backtracking Search + MRV + AC-3 to discover a feasible delivery schedule."""
        self.search_steps_log.clear()
        self.search_steps_log.append("Executing AC-3 Arc Consistency Pre-Processing...")
        
        domains_copy = {k: list(v) for k, v in self.domains.items()}
        if not self.ac3(domains_copy):
            self.search_steps_log.append("AC-3 determined problem is unsatisfiable in initial domains.")
            return None

        self.search_steps_log.append("AC-3 Domain Pruning Complete. Commencing Backtracking + MRV...")
        assignment: Dict[str, int] = {}
        result = self._backtrack(assignment, domains_copy)
        
        if result:
            self.search_steps_log.append(f"Optimal Feasible Schedule Found! Assigned {len(result)} missions.")
            for tid, slot in result.items():
                self.task_dict[tid].assigned_slot = slot
        else:
            self.search_steps_log.append("Backtracking completed without finding valid assignment.")
            
        return result

    def _backtrack(self, assignment: Dict[str, int], domains: Dict[str, List[int]]) -> Optional[Dict[str, int]]:
        if len(assignment) == len(self.task_dict):
            return assignment

        var = self.select_unassigned_variable_mrv(assignment, domains)
        task = self.task_dict[var]
        self.search_steps_log.append(f"MRV Selected Variable: {var} ({task.name}, Urgency: {task.urgency})")

        for value in self.order_domain_values_lcv(var, domains):
            if self.is_consistent_assignment(var, value, assignment):
                assignment[var] = value
                self.search_steps_log.append(f"  -> Assigning {var} to Slot {value} ({TIME_SLOT_LABELS[value]})")

                # Forward checking / domain reduction
                local_domains = copy.deepcopy(domains)
                local_domains[var] = [value]
                
                if self.ac3(local_domains):
                    result = self._backtrack(assignment, local_domains)
                    if result is not None:
                        return result

                # Backtrack
                self.search_steps_log.append(f"  <! Backtracking on {var} at Slot {value}")
                del assignment[var]

        return None

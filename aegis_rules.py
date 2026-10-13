"""
AegisMed Knowledge and Clinical Reasoning Engine
Implements Rule-Based Expert System for Hospital Operational Regulations
Forward Chaining Rule Base:
- Rule 1: Zone(z, ICU) -> RequiresSterile(robot)
- Rule 2: Corridor(c) ^ Busy(c, t) -> AvoidOrSlow(c)
- Rule 3: HazardSpill(c) -> Block(c)
- Rule 4: CodeBlue(z) -> PriorityOverride(z)
- Rule 5: QuietHours(t) -> SilentZoneCost(c)
Author: Guru Prasath S (Register No: 113223010101)
Department of CSE (AI & ML) - Vel Tech High Tech
"""

from typing import List, Dict, Tuple, Set
from aegis_core import HospitalGrid, CellType

class RuleInferenceResult:
    def __init__(self, fired_rules: List[str], modified_cells: int, explanations: List[str]):
        self.fired_rules = fired_rules
        self.modified_cells = modified_cells
        self.explanations = explanations

class HospitalRuleEngine:
    def __init__(self, grid: HospitalGrid):
        self.grid = grid

    def reset_grid_modifiers(self):
        """Restores base traversability and cost baseline."""
        for y in range(self.grid.height):
            for x in range(self.grid.width):
                if self.grid.grid[y][x] == CellType.HAZARD:
                    self.grid.grid[y][x] = CellType.EMPTY
                self.grid.cost_matrix[y][x] = 1.0

    def evaluate_and_apply_rules(
        self,
        robot_is_sterile: bool = True,
        is_busy_visiting_hours: bool = True,
        hazard_spill_locations: List[Tuple[int, int]] = None,
        code_blue_active: bool = False,
        quiet_hours_active: bool = False
    ) -> RuleInferenceResult:
        """
        Executes forward chaining on knowledge base rules and updates grid before planning.
        """
        self.reset_grid_modifiers()
        fired_rules = []
        explanations = []
        modified_cells_count = 0

        # Rule 1: Zone(z, ICU) -> RequiresSterile(robot)
        if not robot_is_sterile:
            fired_rules.append("RULE_1_STERILITY_GUARD")
            explanations.append("Rule 1 Fired: Robot lacks Level-4 Decontamination certification. ICU doors locked.")
            for (x, y) in self.grid.zones["ICU"]:
                self.grid.grid[y][x] = CellType.WALL
                modified_cells_count += 1
        else:
            explanations.append("Rule 1 Verified: Robot is certified sterile for ICU and Surgical suites.")

        # Rule 2: Corridor(c) ^ Busy(c, t) -> AvoidOrSlow(c)
        if is_busy_visiting_hours:
            fired_rules.append("RULE_2_BUSY_CORRIDOR_THROTTLE")
            explanations.append("Rule 2 Fired: Peak visiting hours active (10:00-11:30 AM). Central corridors cost multiplier = 3.5x to favor perimeter routes.")
            # Central corridor lines (y=6..7, x=6..18)
            for y in range(5, 8):
                for x in range(6, 18):
                    if self.grid.grid[y][x] == CellType.EMPTY:
                        self.grid.cost_matrix[y][x] = 3.5
                        modified_cells_count += 1

        # Rule 3: HazardSpill(c) -> Block(c)
        if hazard_spill_locations:
            fired_rules.append("RULE_3_BIOHAZARD_CONTAINMENT")
            for pos in hazard_spill_locations:
                x, y = pos
                if 0 <= x < self.grid.width and 0 <= y < self.grid.height:
                    self.grid.grid[y][x] = CellType.HAZARD
                    modified_cells_count += 1
            explanations.append(f"Rule 3 Fired: Sanitation alert! Biohazard/chemical spills sealed at {hazard_spill_locations}.")

        # Rule 4: CodeBlue(z) -> PriorityOverride(z)
        if code_blue_active:
            fired_rules.append("RULE_4_CODE_BLUE_PRIORITY")
            explanations.append("Rule 4 Fired: Code Blue Emergency declared in Triage & ICU! Clearing priority transit corridor.")
            for y in range(11, 14):
                for x in range(6, 13):
                    if self.grid.grid[y][x] == CellType.EMPTY:
                        self.grid.cost_matrix[y][x] = 0.5  # Green transit highway
                        modified_cells_count += 1

        # Rule 5: QuietHours(t) -> SilentZoneCost(c)
        if quiet_hours_active:
            fired_rules.append("RULE_5_ACOUSTIC_DECIBEL_LIMIT")
            explanations.append("Rule 5 Fired: Acoustic decibel threshold enabled near General Ward. Speed throttled.")
            for (x, y) in self.grid.zones["GENERAL_WARD"]:
                self.grid.cost_matrix[y][x] = 2.0
                modified_cells_count += 1

        return RuleInferenceResult(fired_rules, modified_cells_count, explanations)

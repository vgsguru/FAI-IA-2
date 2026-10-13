"""
AegisMed Autonomous Hospital Fleet Commander
Core Domain Models and Hospital Environment Layout
Author: Guru Prasath S (Register No: 113223010101)
Department of CSE (AI & ML) - Vel Tech High Tech
"""

from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Set, Optional
from enum import Enum

class CellType(Enum):
    EMPTY = 0
    WALL = 1
    PHARMACY = 2
    ICU = 3
    LAB = 4
    GENERAL_WARD = 5
    SURGERY = 6
    LIFT = 7
    TRIAGE = 8
    HAZARD = 9

@dataclass
class DeliveryTask:
    task_id: str
    name: str
    item: str
    origin: Tuple[int, int]
    destination: Tuple[int, int]
    time_window: Tuple[int, int]  # (earliest_slot, deadline_slot)
    urgency: int  # 3: STAT/Emergency, 2: Urgent, 1: Routine
    energy_cost: int  # battery units (e.g., 15%)
    requires_lift: bool = False
    requires_sterile: bool = False
    assigned_slot: Optional[int] = None

class HospitalGrid:
    """
    Hospital Floor Matrix: 24 columns x 18 rows.
    Contains specialized medical zones, corridors, walls, and lift access points.
    """
    def __init__(self, width: int = 24, height: int = 18):
        self.width = width
        self.height = height
        self.grid = [[CellType.EMPTY for _ in range(width)] for _ in range(height)]
        self.cost_matrix = [[1.0 for _ in range(width)] for _ in range(height)]
        self.occupancy_prob = [[0.05 for _ in range(width)] for _ in range(height)]
        self.zones: Dict[str, Set[Tuple[int, int]]] = {
            "PHARMACY": set(),
            "ICU": set(),
            "LAB": set(),
            "GENERAL_WARD": set(),
            "SURGERY": set(),
            "LIFT": set(),
            "TRIAGE": set()
        }
        self._build_hospital_layout()

    def _build_hospital_layout(self):
        # Outer boundary walls
        for x in range(self.width):
            self.grid[0][x] = CellType.WALL
            self.grid[self.height - 1][x] = CellType.WALL
        for y in range(self.height):
            self.grid[y][0] = CellType.WALL
            self.grid[y][self.width - 1] = CellType.WALL

        # Internal Architecture: Ward Rooms, Corridors, Partitions
        # Pharmacy Station (Top-Left: x 1..5, y 1..4)
        self._create_room(1, 5, 1, 4, CellType.PHARMACY, "PHARMACY", door=(5, 3))

        # Central Diagnostic Lab (Top-Center: x 9..14, y 1..4)
        self._create_room(9, 14, 1, 4, CellType.LAB, "LAB", door=(11, 4))

        # Operation Theatres / Surgery (Top-Right: x 17..22, y 1..5)
        self._create_room(17, 22, 1, 5, CellType.SURGERY, "SURGERY", door=(17, 3))

        # Central Elevator / Lift Bank (Center: x 11..13, y 8..10)
        self._create_room(11, 13, 8, 10, CellType.LIFT, "LIFT", door=(11, 8))

        # Emergency Triage (Bottom-Left: x 1..6, y 12..16)
        self._create_room(1, 6, 12, 16, CellType.TRIAGE, "TRIAGE", door=(6, 14))

        # Intensive Care Unit (ICU) - Sterile Zone (Bottom-Center/Right: x 9..15, y 13..16)
        self._create_room(9, 15, 13, 16, CellType.ICU, "ICU", door=(12, 13))

        # General Ward Beds (Bottom-Right: x 18..22, y 11..16)
        self._create_room(18, 22, 11, 16, CellType.GENERAL_WARD, "GENERAL_WARD", door=(18, 13))

        # Divider Wall between Corridors to create authentic maze navigation challenges
        for y in range(6, 12):
            self.grid[y][6] = CellType.WALL
        # Hallway opening at (6, 7)
        self.grid[7][6] = CellType.EMPTY

        for y in range(5, 12):
            self.grid[y][16] = CellType.WALL
        # Hallway opening at (16, 9)
        self.grid[9][16] = CellType.EMPTY

        # Set higher occupancy probability in main intersections
        for x in range(7, 11):
            self.occupancy_prob[6][x] = 0.65
            self.occupancy_prob[11][x] = 0.55

    def _create_room(self, x1: int, x2: int, y1: int, y2: int, cell_type: CellType, zone_name: str, door: Tuple[int, int]):
        for y in range(y1, y2 + 1):
            for x in range(x1, x2 + 1):
                if x == x1 or x == x2 or y == y1 or y == y2:
                    self.grid[y][x] = CellType.WALL
                else:
                    self.grid[y][x] = cell_type
                    self.zones[zone_name].add((x, y))
        # Door opening
        dx, dy = door
        self.grid[dy][dx] = cell_type
        self.zones[zone_name].add((dx, dy))

    def is_passable(self, x: int, y: int) -> bool:
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.grid[y][x] != CellType.WALL and self.grid[y][x] != CellType.HAZARD
        return False

    def get_neighbors(self, pos: Tuple[int, int]) -> List[Tuple[int, int]]:
        x, y = pos
        # 4-directional cardinal movement for authentic hospital automated guided vehicles (AGV)
        candidates = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
        return [c for c in candidates if self.is_passable(c[0], c[1])]

    def get_room_center(self, zone_name: str) -> Tuple[int, int]:
        coords = list(self.zones[zone_name])
        if not coords:
            return (2, 2)
        avg_x = sum(c[0] for c in coords) // len(coords)
        avg_y = sum(c[1] for c in coords) // len(coords)
        return (avg_x, avg_y)

def get_preset_guru_deliveries(grid: HospitalGrid) -> List[DeliveryTask]:
    """Pre-configured clinical missions for Guru's AegisMed platform."""
    pharm_pos = grid.get_room_center("PHARMACY")
    lab_pos = grid.get_room_center("LAB")
    icu_pos = grid.get_room_center("ICU")
    surg_pos = grid.get_room_center("SURGERY")
    ward_pos = grid.get_room_center("GENERAL_WARD")
    triage_pos = grid.get_room_center("TRIAGE")

    return [
        DeliveryTask(
            task_id="DEL-101",
            name="Emergency Blood Plasma",
            item="O-Negative Blood Units",
            origin=lab_pos,
            destination=icu_pos,
            time_window=(0, 2),  # 09:00 - 10:00
            urgency=3,           # STAT
            energy_cost=18,
            requires_lift=False,
            requires_sterile=True
        ),
        DeliveryTask(
            task_id="DEL-102",
            name="Post-Op Antibiotics",
            item="Vancomycin IV 1g",
            origin=pharm_pos,
            destination=surg_pos,
            time_window=(1, 4),  # 09:30 - 11:00
            urgency=2,           # Urgent
            energy_cost=22,
            requires_lift=True,
            requires_sterile=True
        ),
        DeliveryTask(
            task_id="DEL-103",
            name="Biopsy Pathology Vials",
            item="Histology Tissue Sample",
            origin=surg_pos,
            destination=lab_pos,
            time_window=(2, 5),  # 10:00 - 11:30
            urgency=2,           # Urgent
            energy_cost=15,
            requires_lift=False,
            requires_sterile=False
        ),
        DeliveryTask(
            task_id="DEL-104",
            name="Routine Ward Medication",
            item="Hypertension & Diabetic Meds",
            origin=pharm_pos,
            destination=ward_pos,
            time_window=(3, 6),  # 10:30 - 12:00
            urgency=1,           # Routine
            energy_cost=20,
            requires_lift=False,
            requires_sterile=False
        ),
        DeliveryTask(
            task_id="DEL-105",
            name="Trauma Saline Infusion",
            item="Ringer Lactate 500ml",
            origin=pharm_pos,
            destination=triage_pos,
            time_window=(0, 3),  # 09:00 - 10:30
            urgency=3,           # STAT
            energy_cost=16,
            requires_lift=True,
            requires_sterile=False
        ),
    ]

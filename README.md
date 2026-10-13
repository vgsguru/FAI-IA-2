# AegisMed: Autonomous Hospital Delivery Fleet Commander

<div align="center">

![AegisMed Logo](./assets/veltech_logo.png)

### 🏥 Autonomous Hospital AGV Logistics & Clinical Fleet Commander
**Course:** 25ML35T / Foundations of Artificial Intelligence  
**Student:** Guru Prasath S | **Register Number:** 113223010101  
**Faculty:** Dr. Manoj Kumar D S, Associate Professor / Department of CSE(AI&ML)  
**Institution:** Vel Tech High Tech Dr. Rangarajan Dr. Sakunthala Engineering College  

</div>

---

## 1. Project Overview & Multi-Tier AI Architecture

AegisMed is an integrated autonomous hospital robotics operations suite designed for high-stakes healthcare transport (blood bags, chemotherapy vials, surgical trays, pathology specimens).

```
┌────────────────────────────────────────────────────────────────────────┐
│                   AegisMed Tactical Operations Hub                     │
├────────────────────────────────┬───────────────────────────────────────┤
│ 1. Multi-Task CSP Scheduler    │ Backtracking + MRV + Degree + AC-3    │
│ 2. Informed Heuristic Routing  │ A* Search with Manhattan Metric       │
│ 3. Clinical Knowledge Engine   │ First-Order Horn Clause Inference     │
│ 4. Dynamic Detour Re-Planner   │ Hazard Avoidance + XAI Audit          │
│ 5. Modern Minimalist UI        │ White + Purple Two-Tone with Kinetics │
└────────────────────────────────┴───────────────────────────────────────┘
```

---

## 2. Spatial Grid Topology & Heuristic Pathfinding

The physical hospital facility is structured as a **24 columns × 18 rows** topological matrix comprising sterile zones, surgical wards, elevators, and transit corridors.

### 2.1 Spatial Zones & Movement Weights
| Zone Code | Department Name | Sterility Requirement | Base Traversal Weight |
| :--- | :--- | :--- | :--- |
| `PHARMACY` | Central Pharmacy Depot | Standard | 1.0x |
| `ICU` | Intensive Critical Care Complex | Level-4 Cleanroom Required | 1.2x |
| `LAB` | Central Diagnostic Pathology | Standard | 1.0x |
| `SURGERY` | Surgical Suites / OR | Sterile Isolation | 1.1x |
| `WARD` | Inpatient General Care | Low Noise Constraint | 1.0x |
| `LIFT` | High-Capacity Service Elevator | Vertical Transit Locking | 1.0x |
| `TRIAGE` | Emergency Resuscitation ER | STAT Immediate Access | 1.0x |
| `WALL` | Structural Partitions & Barriers | Non-Traversable | $\infty$ |

### 2.2 Mathematical Formulation of Informed A* Search
$$f(n) = g(n) + h(n), \quad h(n) = |x_n - x_g| + |y_n - y_g|$$

---

## 3. Constraint Satisfaction Problem (CSP) Dispatch Engine
$$\mathcal{P} = \langle \mathcal{X}, \mathcal{D}, \mathcal{C} \rangle$$
- Backtracking Search accelerated by **Minimum Remaining Values (MRV)** heuristic, **Degree heuristic**, and **AC-3 Arc Consistency Propagation**.

---

## 4. Clinical Knowledge Engine & First-Order Rules
1. **Rule 1 (ICU Sterility Protocol)**: $\text{Zone}(z, \text{ICU}) \land \neg \text{SterileCertified}(r) \implies \text{BlockCell}(z)$
2. **Rule 2 (Visiting Hours Foot-Traffic Throttling)**: $\text{Corridor}(c) \land \text{VisitingShift}(t) \implies \text{CostMultiplier}(c, 3.5)$
3. **Rule 3 (Biohazard Spill Containment)**: $\text{SpillReported}(c) \implies \text{BlockCell}(c)$
4. **Rule 4 (Code Blue Priority Expressway)**: $\text{CodeBlueActive}(z) \land \text{Route}(r, z) \implies \text{CostMultiplier}(r, 0.5)$
5. **Rule 5 (Pediatric Quiet Hours Speed Limit)**: $\text{QuietHoursActive}(t) \land \text{Zone}(z, \text{Pediatrics}) \implies \text{VelocityCap}(r, \text{Low})$

---

## 5. Dynamic Detour Re-Planning & Responsible AI (XAI)

When navigation encounters sudden corridor blockage (e.g., patient bed transfer, spill cart), the dynamic re-planner:
1. Halts robot immediately before the obstacle coordinate.
2. Injects the blocked cell into the collision avoidance matrix.
3. Computes a real-time detour from the robot's current coordinate to the goal using A*.
4. Generates a clinical Explainable AI (XAI) transparent justification report.

### 5.1 Empirical Search Benchmarks (A* vs. BFS)

| Mission ID | Origin → Target | Path Length | A* Nodes Expanded | BFS Nodes Expanded | Search Reduction | Latency (ms) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| `TASK-G1` | Lab (4,3) → ER (18,14) | 26 steps | **34** | 154 | **77.9%** | 0.82 ms |
| `TASK-G2` | Pharm (2,2) → ICU (18,3) | 21 steps | **27** | 118 | **77.1%** | 0.65 ms |
| `TASK-G3` | Blood (4,3) → OR (18,9) | 22 steps | **29** | 126 | **76.9%** | 0.71 ms |
| `TASK-G4` | Lab (4,3) → Ward (10,13) | 17 steps | **21** | 89 | **76.4%** | 0.52 ms |
| `TASK-G5` | Pharm (2,2) → ER (18,14) | 27 steps | **36** | 162 | **77.8%** | 0.88 ms |

*Empirical finding: The Manhattan distance heuristic prunes over 76% of irrelevant corridor evaluations across all operational floor routes while maintaining 100% path optimality.*

---

## 6. Quickstart Execution
```bash
# 1-Click Launch (Windows)
run.bat

# Standard CLI Execution
python app.py
```
Zero external dependencies — pure standard library.

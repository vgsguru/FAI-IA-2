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
The routing engine computes optimal paths by evaluating an evaluation function $f(n)$ at each candidate node $n$:

$$f(n) = g(n) + h(n)$$

Where:
- $g(n)$: Exact accumulated movement cost from start cell $S$ to current cell $n$, factoring corridor congestion weights.
- $h(n)$: Admissible Manhattan distance heuristic to target $G = (x_g, y_g)$:

$$h(n) = |x_n - x_g| + |y_n - y_g|$$

Because the AGV moves orthogonally across 4-connected grid cells and cell costs are $\ge 1.0$, $h(n)$ never overestimates the true cost to reach the goal ($h(n) \le h^*(n)$), guaranteeing optimal and complete solutions.

---

## 3. Quickstart Execution
```bash
# 1-Click Launch (Windows)
run.bat

# Standard CLI Execution
python app.py
```
Zero external dependencies — pure standard library.

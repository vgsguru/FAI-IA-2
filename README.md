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

---

## 3. Constraint Satisfaction Problem (CSP) Dispatch Engine

Multi-robot missions cannot be dispatched haphazardly without causing corridor deadlocks, elevator queue starvation, or battery collapse. AegisMed formulates delivery scheduling as a formal Constraint Satisfaction Problem:

$$\mathcal{P} = \langle \mathcal{X}, \mathcal{D}, \mathcal{C} \rangle$$

### 3.1 CSP Formalism
- **Variables ($\mathcal{X}$)**: Set of active clinical delivery tasks $\{T_1, T_2, T_3, T_4, T_5\}$.
- **Domains ($\mathcal{D}_i$)**: Available dispatch time slots $\{0, 1, 2, \dots, 7\}$ representing operational half-hour intervals from 08:30 AM to 12:30 PM.
- **Constraints ($\mathcal{C}$)**:
  1. *Temporal Window Constraint*: $\text{start}_i \le \text{slot}(T_i) \le \text{end}_i$ (Unary).
  2. *Fleet Concurrency Limit*: $\text{slot}(T_i) \neq \text{slot}(T_j)$ for all $i \neq j$ (Binary AllDifferent).
  3. *Elevator Mutual Exclusion*: If $\text{requires\_lift}(T_i) \land \text{requires\_lift}(T_j)$, then $\text{slot}(T_i) \neq \text{slot}(T_j)$.
  4. *Urgency Priority Invariant*: STAT priority tasks ($\text{urgency} = 3$) receive precedence in variable ordering.

### 3.2 Optimization Algorithms
- **Minimum Remaining Values (MRV)**: Selects the unassigned task variable with the smallest legal domain size $|\mathcal{D}_i|$, maximizing early failure detection.
- **Degree Heuristic**: Breaks ties by prioritizing the variable involved in the greatest number of active binary constraints.
- **AC-3 Arc Consistency Propagation**: Enforces arc consistency over the binary constraint network before and during recursive backtracking search, proactively pruning infeasible branches.

---

## 4. Quickstart Execution
```bash
# 1-Click Launch (Windows)
run.bat

# Standard CLI Execution
python app.py
```
Zero external dependencies — pure standard library.

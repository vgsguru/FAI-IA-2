# AegisMed: Autonomous Hospital Delivery Fleet Commander

**Course:** 25ML35T / Foundations of Artificial Intelligence  
**Student Name:** Guru Prasath S  
**Register Number:** 113223010101  
**Faculty:** Dr. Manoj Kumar D S, Associate Professor / Department of CSE(AI&ML)  
**Institution:** Vel Tech High Tech Dr. Rangarajan Dr. Sakunthala Engineering College  

---

## 1. Project Overview
AegisMed is a cyber-clinical operations bridge and multi-agent hospital AGV fleet management platform. It integrates:
1. **Informed Search (A*) with Manhattan Distance Heuristic**: Optimal pathfinding for medicine/sample transit with empirical node expansion logging.
2. **Uninformed Benchmark (BFS)**: Breadth-first frontier comparison proving search space reduction.
3. **CSP Layer**: Scheduling deliveries across time slots using Backtracking with MRV heuristic, Degree heuristic, and AC-3 constraint propagation.
4. **Clinical Knowledge Engine**: Forward-chaining first-order rule base for ICU sterility, visiting hours traffic congestion, and biohazard isolation.
5. **Applied & Responsible AI**: Probabilistic occupancy grid, dynamic obstacle detection and real-time detour re-planning, accompanied by Explainable AI (XAI) rationale logs and healthcare safety audits.

---

## 2. One-Click Execution
Simply double-click `run.bat` or run:
```bash
python app.py
```

---

## 3. Architecture & File Structure
```
├── aegis_core.py             # Hospital 24x18 spatial grid, zones, cell models
├── aegis_search.py           # A* with Manhattan heuristic vs. BFS benchmark
├── aegis_csp.py              # CSP dispatcher (Backtracking + MRV + Degree + AC-3)
├── aegis_rules.py            # First-order clinical rule inference engine
├── aegis_replan.py           # Dynamic detour re-planning, occupancy grid, and XAI
├── app.py                    # Modern Minimal White + Purple GUI with animations
├── run.bat                   # 1-click execution script
├── requirements.txt          # Pure standard library (zero external dependencies)
├── Guru_Project_Report.docx  # Full 9-section report in official Vel Tech format
├── Guru_Project_Report.pdf   # Complete printable PDF project report
├── REPORT.md                 # Full markdown micro-level project report
└── assets/                   # Architecture diagrams, flowcharts, and screenshots
    ├── veltech_logo.png
    ├── guru_fig1_arch.png
    ├── guru_fig2_flow.png
    ├── guru_fig3_input.png
    └── guru_fig4_output.png
```

---

## 4. UI/UX Design System
- **Two-Tone Palette**: Pure White (`#FFFFFF`) background with Royal Violet (`#7C3AED`) and soft lavender accents (`#EDE9FE`).
- **Typography**: Clean Microsoft Segoe UI with clear hierarchical headings and telemetry readouts.
- **Micro-Animations**:
  - Interactive rounded canvas buttons with smooth hover and click transitions.
  - Step-by-step corridor path tracing animation (`self.after`).
  - Dynamic detour overlays and blocked cell markers.
  - Live search space efficiency card updates.
```

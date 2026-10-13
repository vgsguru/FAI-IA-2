"""
AegisMed — Autonomous Hospital Fleet Commander
Modern Minimal White + Purple UI with Animations
Author: Guru Prasath S (113223010101)
"""

import tkinter as tk
from tkinter import ttk, messagebox
import math, time
from typing import List, Tuple, Dict, Optional

from aegis_core import HospitalGrid, CellType, DeliveryTask, get_preset_guru_deliveries
from aegis_search import astar_search, bfs_search, compare_search_algorithms, SearchResult
from aegis_csp import CSPScheduler, TIME_SLOT_LABELS
from aegis_rules import HospitalRuleEngine
from aegis_replan import DynamicReplanner, ReplanResult

# ── Strict 2-Color Palette ──────────────────────────────────────────────
WHITE       = "#FFFFFF"
PURPLE      = "#7C3AED"
PURPLE_LIGHT= "#EDE9FE"   # tinted white (purple 5%)
PURPLE_MID  = "#A78BFA"   # lighter purple for accents
PURPLE_DARK = "#5B21B6"   # hover / pressed
PURPLE_GHOST= "#F5F3FF"   # barely-there tint
GRAY_LINE   = "#E5E7EB"   # neutral grid lines
WALL_COLOR  = "#C4B5FD"   # purple-tinted wall
FONT_DARK   = "#1E1B4B"   # near-black with purple undertone
FONT_MID    = "#6B7280"   # muted gray for secondary text

FONT_FAMILY = "Segoe UI"

class AnimatedButton(tk.Canvas):
    """A modern flat button with hover animation."""
    def __init__(self, parent, text, command, filled=True, width=260, height=42, **kw):
        super().__init__(parent, width=width, height=height, bg=WHITE, bd=0, highlightthickness=0, **kw)
        self.cmd = command
        self.filled = filled
        self.w, self.h = width, height
        self.hover = False
        self._text = text

        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)
        self._draw()

    def _draw(self):
        self.delete("all")
        r = 8
        if self.filled:
            fill = PURPLE_DARK if self.hover else PURPLE
            fg = WHITE
        else:
            fill = PURPLE_GHOST if self.hover else WHITE
            fg = PURPLE
        # Rounded rect
        self.create_rounded_rect(2, 2, self.w-2, self.h-2, r, fill=fill, outline=PURPLE, width=1.5)
        self.create_text(self.w//2, self.h//2, text=self._text, fill=fg,
                         font=(FONT_FAMILY, 10, "bold"))

    def create_rounded_rect(self, x1, y1, x2, y2, r, **kw):
        points = [
            x1+r,y1, x2-r,y1, x2,y1, x2,y1+r,
            x2,y2-r, x2,y2, x2-r,y2, x1+r,y2,
            x1,y2, x1,y2-r, x1,y1+r, x1,y1
        ]
        self.create_polygon(points, smooth=True, **kw)

    def _on_enter(self, e): self.hover = True; self._draw()
    def _on_leave(self, e): self.hover = False; self._draw()
    def _on_click(self, e): self.cmd()


class AegisMedApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("AegisMed  ·  Hospital Fleet Commander")
        self.geometry("1440x900")
        self.minsize(1200, 780)
        self.configure(bg=WHITE)

        # ── Data ────────────────────────────────────────────────────────
        self.grid_model   = HospitalGrid(24, 18)
        self.deliveries   = get_preset_guru_deliveries(self.grid_model)
        self.selected     = self.deliveries[0]
        self.rule_engine  = HospitalRuleEngine(self.grid_model)
        self.replanner    = DynamicReplanner(self.grid_model)

        self.cur_path: List[Tuple[int,int]]     = []
        self.explored_a: List[Tuple[int,int]]   = []
        self.explored_b: List[Tuple[int,int]]   = []
        self.replan_res: Optional[ReplanResult]  = None
        self.blocked_cell: Optional[Tuple[int,int]] = None
        self.anim_step = 0
        self.anim_id   = None

        # ── Layout ──────────────────────────────────────────────────────
        self._build_header()
        body = tk.Frame(self, bg=WHITE)
        body.pack(fill=tk.BOTH, expand=True, padx=28, pady=(0, 24))

        self._build_left_panel(body)
        self._build_center(body)
        self._build_right_panel(body)

        self._run_plan()

    # ════════════════════════════════════════════════════════════════════
    # HEADER
    # ════════════════════════════════════════════════════════════════════
    def _build_header(self):
        hdr = tk.Frame(self, bg=WHITE, height=72)
        hdr.pack(fill=tk.X)
        hdr.pack_propagate(False)

        # Thin purple accent line at very top
        tk.Frame(hdr, bg=PURPLE, height=3).pack(fill=tk.X, side=tk.TOP)

        inner = tk.Frame(hdr, bg=WHITE)
        inner.pack(fill=tk.BOTH, expand=True, padx=32)

        # Logo
        logo_frame = tk.Frame(inner, bg=WHITE)
        logo_frame.pack(side=tk.LEFT, pady=12)

        dot = tk.Canvas(logo_frame, width=28, height=28, bg=WHITE, bd=0, highlightthickness=0)
        dot.pack(side=tk.LEFT, padx=(0, 10))
        dot.create_oval(2, 2, 26, 26, fill=PURPLE, outline="")

        tk.Label(logo_frame, text="AegisMed", font=(FONT_FAMILY, 18, "bold"),
                 fg=FONT_DARK, bg=WHITE).pack(side=tk.LEFT)
        tk.Label(logo_frame, text="Fleet Commander", font=(FONT_FAMILY, 11),
                 fg=FONT_MID, bg=WHITE).pack(side=tk.LEFT, padx=(8, 0), pady=(4, 0))

        # Right badges
        right = tk.Frame(inner, bg=WHITE)
        right.pack(side=tk.RIGHT, pady=12)

        self._badge(right, "● System Online", PURPLE)
        self._badge(right, "Guru Prasath S  ·  113223010101", FONT_MID)

    def _badge(self, parent, text, color):
        lbl = tk.Label(parent, text=text, font=(FONT_FAMILY, 9), fg=color, bg=PURPLE_GHOST,
                       padx=14, pady=5)
        lbl.pack(side=tk.LEFT, padx=4)

    # ════════════════════════════════════════════════════════════════════
    # LEFT PANEL — Controls
    # ════════════════════════════════════════════════════════════════════
    def _build_left_panel(self, parent):
        col = tk.Frame(parent, bg=WHITE, width=300)
        col.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 20))
        col.pack_propagate(False)

        # Section: Mission
        self._section_label(col, "MISSION")

        self.task_var = tk.StringVar(value=self.selected.name)
        names = [d.name for d in self.deliveries]

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("P.TCombobox", fieldbackground=WHITE, background=PURPLE_GHOST,
                         foreground=FONT_DARK, bordercolor=PURPLE_MID, arrowcolor=PURPLE)
        cb = ttk.Combobox(col, textvariable=self.task_var, values=names, state="readonly",
                          font=(FONT_FAMILY, 10), style="P.TCombobox")
        cb.pack(fill=tk.X, pady=(0, 8))
        cb.bind("<<ComboboxSelected>>", lambda e: self._on_task_change())

        self.lbl_info = tk.Label(col, text="", font=(FONT_FAMILY, 9), fg=FONT_MID,
                                 bg=PURPLE_GHOST, justify=tk.LEFT, anchor="nw",
                                 padx=12, pady=10, wraplength=270)
        self.lbl_info.pack(fill=tk.X, pady=(0, 16))

        # Buttons
        AnimatedButton(col, "▶  Compute A* Route", self._run_plan).pack(pady=4)
        AnimatedButton(col, "⚡  Benchmark A* vs BFS", self._run_compare).pack(pady=4)
        AnimatedButton(col, "⚠  Dynamic Obstacle Re-plan", self._run_replan, filled=False).pack(pady=4)
        AnimatedButton(col, "📅  Solve CSP Schedule", self._run_csp, filled=False).pack(pady=4)

        # Section: Knowledge Rules
        self._section_label(col, "CLINICAL RULES", top=24)

        self.chk_sterile  = tk.BooleanVar(value=True)
        self.chk_visiting = tk.BooleanVar(value=True)
        self.chk_spill    = tk.BooleanVar(value=False)
        self.chk_code     = tk.BooleanVar(value=False)
        self.chk_quiet    = tk.BooleanVar(value=False)

        for txt, var in [
            ("ICU Sterile Certified", self.chk_sterile),
            ("Peak Visiting Hours", self.chk_visiting),
            ("Biohazard Spill Active", self.chk_spill),
            ("Code Blue Override", self.chk_code),
            ("Quiet Hours Throttle", self.chk_quiet),
        ]:
            self._make_check(col, txt, var)

    def _section_label(self, parent, text, top=0):
        tk.Label(parent, text=text, font=(FONT_FAMILY, 9, "bold"), fg=PURPLE,
                 bg=WHITE, anchor="w").pack(fill=tk.X, pady=(top + 12, 6))
        tk.Frame(parent, bg=PURPLE_LIGHT, height=1).pack(fill=tk.X, pady=(0, 8))

    def _make_check(self, parent, text, var):
        tk.Checkbutton(parent, text=text, variable=var, command=self._run_plan,
                       font=(FONT_FAMILY, 9), fg=FONT_DARK, bg=WHITE,
                       selectcolor=PURPLE_LIGHT, activebackground=WHITE,
                       activeforeground=PURPLE, highlightthickness=0,
                       bd=0).pack(anchor="w", pady=2)

    # ════════════════════════════════════════════════════════════════════
    # CENTER — Grid Canvas
    # ════════════════════════════════════════════════════════════════════
    def _build_center(self, parent):
        frame = tk.Frame(parent, bg=WHITE)
        frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 20))

        # Title row
        top = tk.Frame(frame, bg=WHITE)
        top.pack(fill=tk.X, pady=(0, 8))
        tk.Label(top, text="Hospital Floor Plan", font=(FONT_FAMILY, 13, "bold"),
                 fg=FONT_DARK, bg=WHITE).pack(side=tk.LEFT)
        tk.Label(top, text="24 × 18  Multi-Zone Matrix", font=(FONT_FAMILY, 10),
                 fg=FONT_MID, bg=WHITE).pack(side=tk.LEFT, padx=(10, 0))

        # Legend
        leg = tk.Frame(frame, bg=WHITE)
        leg.pack(fill=tk.X, pady=(0, 6))
        for name, color in [("A* Path", PURPLE), ("BFS Explored", PURPLE_MID),
                             ("Blocked", "#EF4444"), ("Start", "#10B981"), ("Goal", PURPLE_DARK)]:
            tk.Canvas(leg, width=10, height=10, bg=WHITE, bd=0, highlightthickness=0)\
                .pack(side=tk.LEFT, padx=(12, 2))
            leg.winfo_children()[-1].create_oval(1, 1, 9, 9, fill=color, outline="")
            tk.Label(leg, text=name, font=(FONT_FAMILY, 8), fg=FONT_MID, bg=WHITE)\
                .pack(side=tk.LEFT)

        # Canvas with border
        border = tk.Frame(frame, bg=PURPLE_LIGHT, padx=1, pady=1)
        border.pack(fill=tk.BOTH, expand=True)
        self.canvas = tk.Canvas(border, bg=WHITE, bd=0, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Configure>", lambda e: self._render_grid())

    # ════════════════════════════════════════════════════════════════════
    # RIGHT PANEL — Metrics + CSP + XAI
    # ════════════════════════════════════════════════════════════════════
    def _build_right_panel(self, parent):
        col = tk.Frame(parent, bg=WHITE, width=380)
        col.pack(side=tk.RIGHT, fill=tk.Y)
        col.pack_propagate(False)

        # ─ A* vs BFS Metric Cards ─
        self._section_label(col, "SEARCH METRICS")

        cards = tk.Frame(col, bg=WHITE)
        cards.pack(fill=tk.X, pady=(0, 6))

        # A* Card
        self.card_a = tk.Frame(cards, bg=PURPLE_GHOST, padx=14, pady=10,
                               highlightthickness=1, highlightbackground=PURPLE_MID)
        self.card_a.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 6))
        tk.Label(self.card_a, text="A* INFORMED", font=(FONT_FAMILY, 8, "bold"),
                 fg=PURPLE, bg=PURPLE_GHOST).pack(anchor="w")
        self.lbl_a_nodes = tk.Label(self.card_a, text="— nodes", font=(FONT_FAMILY, 16, "bold"),
                                    fg=FONT_DARK, bg=PURPLE_GHOST)
        self.lbl_a_nodes.pack(anchor="w")
        self.lbl_a_detail = tk.Label(self.card_a, text="", font=(FONT_FAMILY, 8),
                                     fg=FONT_MID, bg=PURPLE_GHOST)
        self.lbl_a_detail.pack(anchor="w")

        # BFS Card
        self.card_b = tk.Frame(cards, bg=WHITE, padx=14, pady=10,
                               highlightthickness=1, highlightbackground=GRAY_LINE)
        self.card_b.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        tk.Label(self.card_b, text="BFS UNINFORMED", font=(FONT_FAMILY, 8, "bold"),
                 fg=FONT_MID, bg=WHITE).pack(anchor="w")
        self.lbl_b_nodes = tk.Label(self.card_b, text="— nodes", font=(FONT_FAMILY, 16, "bold"),
                                    fg=FONT_DARK, bg=WHITE)
        self.lbl_b_nodes.pack(anchor="w")
        self.lbl_b_detail = tk.Label(self.card_b, text="", font=(FONT_FAMILY, 8),
                                     fg=FONT_MID, bg=WHITE)
        self.lbl_b_detail.pack(anchor="w")

        # Efficiency badge
        self.lbl_eff = tk.Label(col, text="", font=(FONT_FAMILY, 9, "bold"),
                                fg=PURPLE, bg=PURPLE_GHOST, padx=12, pady=6, anchor="w")
        self.lbl_eff.pack(fill=tk.X, pady=(0, 14))

        # ─ CSP Schedule ─
        self._section_label(col, "CSP DISPATCH TIMETABLE")

        tree_frame = tk.Frame(col, bg=WHITE)
        tree_frame.pack(fill=tk.X)

        style = ttk.Style()
        style.configure("Purple.Treeview", background=WHITE, fieldbackground=WHITE,
                         foreground=FONT_DARK, rowheight=26, font=(FONT_FAMILY, 9))
        style.configure("Purple.Treeview.Heading", background=PURPLE_GHOST,
                         foreground=PURPLE, font=(FONT_FAMILY, 9, "bold"))

        columns = ("task", "item", "slot", "urg")
        self.tree_csp = ttk.Treeview(tree_frame, columns=columns, show="headings",
                                      height=5, style="Purple.Treeview")
        for cid, head, w in [("task", "ID", 65), ("item", "Payload", 135),
                              ("slot", "Slot", 100), ("urg", "Priority", 70)]:
            self.tree_csp.heading(cid, text=head)
            self.tree_csp.column(cid, width=w, anchor="center" if cid != "item" else "w")
        self.tree_csp.pack(fill=tk.X)

        # ─ XAI Log ─
        self._section_label(col, "EXPLAINABLE AI LOG", top=8)

        self.txt_xai = tk.Text(col, bg=PURPLE_GHOST, fg=FONT_DARK, font=(FONT_FAMILY, 8),
                               bd=0, padx=12, pady=10, wrap=tk.WORD,
                               insertbackground=PURPLE, highlightthickness=1,
                               highlightbackground=PURPLE_LIGHT)
        self.txt_xai.pack(fill=tk.BOTH, expand=True)

    # ════════════════════════════════════════════════════════════════════
    # ACTIONS
    # ════════════════════════════════════════════════════════════════════
    def _on_task_change(self):
        name = self.task_var.get()
        for d in self.deliveries:
            if d.name == name:
                self.selected = d; break
        self._run_plan()

    def _run_plan(self):
        if self.anim_id:
            self.after_cancel(self.anim_id); self.anim_id = None

        t = self.selected
        urg = {3: "STAT", 2: "Urgent", 1: "Routine"}.get(t.urgency, "?")
        self.lbl_info.config(
            text=f"{t.task_id}  ·  {t.item}\n"
                 f"Route  {t.origin} → {t.destination}\n"
                 f"Priority {urg}  ·  Lift {'Yes' if t.requires_lift else 'No'}  ·  {t.energy_cost}% battery")

        spills = [(10, 6), (10, 7)] if self.chk_spill.get() else []
        rule_res = self.rule_engine.evaluate_and_apply_rules(
            self.chk_sterile.get(), self.chk_visiting.get(), spills,
            self.chk_code.get(), self.chk_quiet.get())

        res = astar_search(self.grid_model, t.origin, t.destination)
        self.cur_path    = res.path
        self.explored_a  = res.explored_order
        self.explored_b  = []
        self.replan_res  = None
        self.blocked_cell = None

        self.lbl_a_nodes.config(text=f"{res.nodes_expanded} nodes")
        self.lbl_a_detail.config(text=f"Path {res.path_length} steps  ·  {res.execution_time_ms:.1f} ms")
        self.lbl_b_nodes.config(text="— nodes")
        self.lbl_b_detail.config(text="Run benchmark to compare")
        self.lbl_eff.config(text=f"✦  A* path computed with Manhattan heuristic")

        self.txt_xai.delete("1.0", tk.END)
        self.txt_xai.insert(tk.END, f"Mission: {t.name}\n")
        self.txt_xai.insert(tk.END, f"Rules fired: {len(rule_res.fired_rules)}\n")
        for exp in rule_res.explanations:
            self.txt_xai.insert(tk.END, f"  • {exp}\n")
        self.txt_xai.insert(tk.END, f"\nA* optimal cost: {res.cost:.1f}  ({res.path_length} steps)\n")

        self._animate_path()

    def _run_compare(self):
        if self.anim_id:
            self.after_cancel(self.anim_id); self.anim_id = None

        t = self.selected
        res = compare_search_algorithms(self.grid_model, t.origin, t.destination)
        ra, rb = res["A*"], res["BFS"]
        self.cur_path   = ra.path
        self.explored_a = ra.explored_order
        self.explored_b = rb.explored_order

        self.lbl_a_nodes.config(text=f"{ra.nodes_expanded} nodes")
        self.lbl_a_detail.config(text=f"Path {ra.path_length}  ·  {ra.execution_time_ms:.1f} ms")
        self.lbl_b_nodes.config(text=f"{rb.nodes_expanded} nodes")
        self.lbl_b_detail.config(text=f"Path {rb.path_length}  ·  {rb.execution_time_ms:.1f} ms")

        saved = rb.nodes_expanded - ra.nodes_expanded
        pct = (saved / max(1, rb.nodes_expanded)) * 100
        self.lbl_eff.config(text=f"⚡  A* pruned {pct:.0f}% of search space  ({saved} fewer nodes)")

        self.txt_xai.delete("1.0", tk.END)
        self.txt_xai.insert(tk.END, f"═══ A* vs BFS BENCHMARK ═══\n\n")
        self.txt_xai.insert(tk.END, f"A*  →  {ra.nodes_expanded} nodes expanded  ({ra.execution_time_ms:.2f} ms)\n")
        self.txt_xai.insert(tk.END, f"BFS →  {rb.nodes_expanded} nodes expanded  ({rb.execution_time_ms:.2f} ms)\n\n")
        self.txt_xai.insert(tk.END, f"Manhattan heuristic pruned {saved} unnecessary corridor evaluations.\n")

        self._animate_path()

    def _run_replan(self):
        if self.anim_id:
            self.after_cancel(self.anim_id); self.anim_id = None
        if not self.cur_path or len(self.cur_path) < 5:
            messagebox.showwarning("Notice", "Path too short."); return

        idx = max(2, len(self.cur_path) // 2)
        rr = self.replanner.simulate_navigation_and_replan(self.cur_path, idx)
        if not rr: return

        self.replan_res  = rr
        self.blocked_cell = rr.blocked_cell
        ar, br = rr.astar_replanned, rr.bfs_replanned

        self.lbl_a_nodes.config(text=f"{ar.nodes_expanded} nodes")
        self.lbl_a_detail.config(text=f"Detour {ar.path_length}  ·  {ar.execution_time_ms:.1f} ms")
        self.lbl_b_nodes.config(text=f"{br.nodes_expanded} nodes")
        self.lbl_b_detail.config(text=f"Detour {br.path_length}  ·  {br.execution_time_ms:.1f} ms")

        diff = br.nodes_expanded - ar.nodes_expanded
        self.lbl_eff.config(text=f"⚠  Re-plan: A* saved {diff} nodes vs BFS")

        self.txt_xai.delete("1.0", tk.END)
        self.txt_xai.insert(tk.END, rr.explanation + "\n\n")
        for k, v in rr.safety_audit.items():
            self.txt_xai.insert(tk.END, f"  ✔ {k}: {v}\n")

        self._render_grid()

    def _run_csp(self):
        sched = CSPScheduler(self.deliveries)
        plan  = sched.solve()
        for item in self.tree_csp.get_children():
            self.tree_csp.delete(item)
        if plan:
            urg_map = {3: "STAT", 2: "Urgent", 1: "Routine"}
            for d in self.deliveries:
                s = plan.get(d.task_id, -1)
                self.tree_csp.insert("", tk.END,
                    values=(d.task_id, d.item, TIME_SLOT_LABELS.get(s, "—"), urg_map.get(d.urgency)))
            self.txt_xai.delete("1.0", tk.END)
            self.txt_xai.insert(tk.END, "═══ CSP SCHEDULE (MRV + AC-3) ═══\n\n")
            for step in sched.search_steps_log:
                self.txt_xai.insert(tk.END, f"{step}\n")
            messagebox.showinfo("CSP Solved", f"Feasible schedule for {len(plan)} missions.")
        else:
            messagebox.showerror("Infeasible", "No valid schedule found.")

    # ════════════════════════════════════════════════════════════════════
    # ANIMATION — step-by-step path reveal
    # ════════════════════════════════════════════════════════════════════
    def _animate_path(self):
        self.anim_step = 0
        self._render_grid()
        if self.cur_path:
            self._anim_tick()

    def _anim_tick(self):
        if self.anim_step >= len(self.cur_path):
            self.anim_id = None; return
        self.anim_step += 1
        self._render_grid()
        self.anim_id = self.after(35, self._anim_tick)

    # ════════════════════════════════════════════════════════════════════
    # GRID RENDERER
    # ════════════════════════════════════════════════════════════════════
    def _render_grid(self):
        self.canvas.delete("all")
        W = self.canvas.winfo_width()
        H = self.canvas.winfo_height()
        if W < 50 or H < 50: return

        gw, gh = self.grid_model.width, self.grid_model.height
        cw, ch = W / gw, H / gh

        zone_colors = {
            CellType.PHARMACY:     PURPLE_GHOST,
            CellType.ICU:          PURPLE_LIGHT,
            CellType.LAB:          PURPLE_GHOST,
            CellType.GENERAL_WARD: "#F9FAFB",
            CellType.SURGERY:      PURPLE_LIGHT,
            CellType.LIFT:         PURPLE_GHOST,
            CellType.TRIAGE:       PURPLE_GHOST,
            CellType.WALL:         WALL_COLOR,
            CellType.HAZARD:       "#FCA5A5",
            CellType.EMPTY:        WHITE,
        }

        # Cells
        for y in range(gh):
            for x in range(gw):
                ct = self.grid_model.grid[y][x]
                x1, y1 = x * cw, y * ch
                x2, y2 = x1 + cw, y1 + ch
                color = zone_colors.get(ct, WHITE)
                if ct == CellType.EMPTY and self.grid_model.cost_matrix[y][x] > 1.5:
                    color = PURPLE_GHOST
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline=GRAY_LINE, width=0.5)

        # BFS explored (light dots)
        for ex in self.explored_b:
            if ex not in (self.selected.origin, self.selected.destination):
                cx, cy = ex[0]*cw + cw/2, ex[1]*ch + ch/2
                r = min(cw, ch) * 0.18
                self.canvas.create_oval(cx-r, cy-r, cx+r, cy+r, fill=PURPLE_LIGHT, outline="")

        # A* explored (medium dots)
        for ex in self.explored_a:
            if ex not in (self.selected.origin, self.selected.destination):
                cx, cy = ex[0]*cw + cw/2, ex[1]*ch + ch/2
                r = min(cw, ch) * 0.15
                self.canvas.create_oval(cx-r, cy-r, cx+r, cy+r, fill=PURPLE_MID, outline="")

        # Animated path
        visible_path = self.cur_path[:self.anim_step] if self.anim_step > 0 else self.cur_path
        if visible_path and len(visible_path) > 1:
            pts = []
            for px, py in visible_path:
                pts.extend([px*cw + cw/2, py*ch + ch/2])
            self.canvas.create_line(pts, fill=PURPLE, width=3.5, smooth=True, capstyle=tk.ROUND)

        # Replanned detour
        if self.replan_res and self.replan_res.replanned_path:
            rpts = []
            for rx, ry in self.replan_res.replanned_path:
                rpts.extend([rx*cw + cw/2, ry*ch + ch/2])
            self.canvas.create_line(rpts, fill=PURPLE_DARK, width=4, dash=(6, 3), capstyle=tk.ROUND)

        # Blocked cell
        if self.blocked_cell:
            bx, by = self.blocked_cell
            pad = 3
            self.canvas.create_rectangle(bx*cw+pad, by*ch+pad, (bx+1)*cw-pad, (by+1)*ch-pad,
                                         fill="#EF4444", outline=WHITE, width=2)
            self.canvas.create_text(bx*cw+cw/2, by*ch+ch/2, text="✕", fill=WHITE,
                                    font=(FONT_FAMILY, 8, "bold"))

        # Start & Goal markers
        if self.selected:
            for pos, color, label in [
                (self.selected.origin, "#10B981", "S"),
                (self.selected.destination, PURPLE_DARK, "G")
            ]:
                px, py = pos
                pad = 2
                self.canvas.create_oval(px*cw+pad, py*ch+pad, (px+1)*cw-pad, (py+1)*ch-pad,
                                        fill=color, outline=WHITE, width=2)
                self.canvas.create_text(px*cw+cw/2, py*ch+ch/2, text=label,
                                        fill=WHITE, font=(FONT_FAMILY, 7, "bold"))

        # Room labels
        room_labels = {
            "PHARMACY": "Pharmacy", "LAB": "Central Lab", "SURGERY": "Surgery",
            "LIFT": "Elevator", "ICU": "ICU", "GENERAL_WARD": "Ward", "TRIAGE": "Triage"
        }
        for zname, label in room_labels.items():
            cx, cy = self.grid_model.get_room_center(zname)
            self.canvas.create_text(cx*cw+cw/2, cy*ch+ch/2, text=label,
                                    fill=PURPLE_DARK, font=(FONT_FAMILY, 8, "bold"))

if __name__ == "__main__":
    app = AegisMedApp()
    app.mainloop()

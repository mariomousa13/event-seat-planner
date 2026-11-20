"""
Event Seating Planner – Streamlit interface
AAIN-7001 Foundations of Artificial Intelligence · Mario Mousa & Denisha Singh

Run with:
    python -m streamlit run app.py

This first version shows EXAMPLE DATA so the layout can be built and tested
before the app is connected to scenarios.py and the real algorithms.
Everything fake lives in the section marked "EXAMPLE DATA". To connect the
real code, only run_planner() needs to change (see "CONNECTING THE REAL CODE").

Data shapes the interface expects
---------------------------------
scenario = {
    "guests":      ["Guest1", "Guest2", ...],
    "num_tables":  5,
    "capacity":    8,
    "together":    [("Guest1", "Guest5"), ...],   # must share a table
    "apart":       [("Guest2", "Guest9"), ...],   # must be at different tables
    "fixed":       {"Guest7": 2, ...},            # guest -> table number (1-based)
    "preferences": [("Guest3", "Guest4"), ...],   # soft: prefer same table
}

result = {
    "name":        "Greedy First-Fit",      # one of ALGORITHMS
    "status":      "Solved",                # Solved | Failed | Timeout | No solution
    "assignments": 20,                      # assignments tried
    "time":        0.000039,                # seconds
    "assignment":  {"Guest1": 1, ...} or None   # guest -> table number, None if not solved
}
"""

import math
import random

import streamlit as st


# =============================================================================
# SETTINGS
# =============================================================================

CAPACITY = 8          # seats per table
TIME_LIMIT = 10       # seconds, for Plain Backtracking and MRV + FC

EVENT_SIZES = {
    "12 guests – Small": 12,
    "24 guests – Medium": 24,
    "36 guests – Large": 36,
}
CONSTRAINT_LEVELS = ["Low", "Medium", "High"]
ALGORITHMS = ["Greedy First-Fit", "Plain Backtracking", "MRV + Forward Checking"]
COMPARE_ALL = "Compare All"
SHORT_NAMES = {
    "Greedy First-Fit": "Greedy",
    "Plain Backtracking": "Backtracking",
    "MRV + Forward Checking": "MRV + FC",
}

STATUS_COLORS = {
    "Solved": "#16A34A",
    "Failed": "#DC2626",
    "Timeout": "#D97706",
    "No solution": "#6B7280",
}
STATUS_MESSAGES = {
    "Failed": "failed to find a valid seating arrangement.",
    "Timeout": f"stopped at the {TIME_LIMIT}-second time limit without finding a solution.",
    "No solution": "found that no valid seating arrangement exists for this scenario.",
}

GUEST_COLOR = "#4F5BD5"
TABLE_FILL = "#EEF0FF"
TABLE_STROKE = "#C7CCF5"


# =============================================================================
# EXAMPLE DATA  (for designing the layout only – NOT real algorithm results)
# =============================================================================

USE_EXAMPLE_DATA = True


def example_scenario(num_guests, level, seed):
    """Builds a made-up scenario with roughly the right number of constraints."""
    rng = random.Random(f"scenario-{num_guests}-{level}-{seed}")
    guests = [f"Guest{i}" for i in range(1, num_guests + 1)]
    num_tables = math.ceil(num_guests / CAPACITY)

    scale = num_guests // 12  # 1, 2 or 3
    together_n, apart_n, fixed_n, pref_n = (
        c * scale for c in {"Low": (1, 1, 0, 2), "Medium": (2, 2, 1, 2), "High": (3, 2, 1, 2)}[level]
    )

    used = set()

    def random_pairs(n):
        pairs = []
        while len(pairs) < n:
            a, b = sorted(rng.sample(guests, 2), key=lambda g: int(g[5:]))
            if (a, b) not in used:
                used.add((a, b))
                pairs.append((a, b))
        return pairs

    fixed_guests = sorted(rng.sample(guests, fixed_n), key=lambda g: int(g[5:]))
    return {
        "guests": guests,
        "num_tables": num_tables,
        "capacity": CAPACITY,
        "together": random_pairs(together_n),
        "apart": random_pairs(apart_n),
        "fixed": {g: rng.randint(1, num_tables) for g in fixed_guests},
        "preferences": random_pairs(pref_n),
    }


def example_result(name, scenario, level, seed):
    """Makes up a plausible result so every card style (Solved/Failed/Timeout) can be seen."""
    n = len(scenario["guests"])
    rng = random.Random(f"result-{name}-{n}-{level}-{seed}")

    if name == "Greedy First-Fit":
        status = "Solved" if level == "Low" else "Failed"
        assignments, time = n + rng.randint(0, 10), rng.uniform(0.00003, 0.0001)
    elif name == "Plain Backtracking":
        status = "Solved" if n == 12 else "Timeout"
        if status == "Solved":
            assignments, time = rng.randint(50, 5_000), rng.uniform(0.001, 0.05)
        else:
            assignments, time = rng.randint(4_000_000, 6_500_000), TIME_LIMIT + rng.uniform(0, 0.00005)
    else:
        status = "Solved"
        assignments, time = n + rng.randint(0, 25), rng.uniform(0.002, 0.02)

    assignment = None
    if status == "Solved":
        shuffled = scenario["guests"][:]
        rng.shuffle(shuffled)
        assignment = {g: i % scenario["num_tables"] + 1 for i, g in enumerate(shuffled)}

    return {"name": name, "status": status, "assignments": assignments,
            "time": time, "assignment": assignment}


# =============================================================================
# CONNECTING THE REAL CODE
# =============================================================================

def run_planner(num_guests, level, seed, algorithm_choice):
    """Returns (scenario, results). This is the only function that needs to
    change to connect the real code. Roughly:

        from scenarios import generate_scenario
        from greedy import ...; from backtracking import ...; from mrv_fc import ...

        scenario = generate_scenario(num_guests, level, seed)
        results = [run_one(name, scenario) for name in chosen]

    where run_one() calls the right algorithm and converts its output into
    the `result` shape described at the top of this file.
    """
    chosen = ALGORITHMS if algorithm_choice == COMPARE_ALL else [algorithm_choice]
    scenario = example_scenario(num_guests, level, seed)
    results = [example_result(name, scenario, level, seed) for name in chosen]
    return scenario, results


# =============================================================================
# FORMATTING HELPERS
# =============================================================================

def guest_label(guest):
    """'Guest12' -> '12' (the algorithms keep the full name internally)."""
    return str(guest).replace("Guest", "").strip()


def guest_sort_key(guest):
    label = guest_label(guest)
    return (0, int(label)) if label.isdigit() else (1, label)


def fmt_time(seconds):
    return f"{seconds:.6f} s"


def fmt_count(n):
    return f"{n:,}"


def preferences_satisfied(result, scenario):
    if result["assignment"] is None:
        return None
    a = result["assignment"]
    return sum(1 for x, y in scenario["preferences"] if a.get(x) == a.get(y))


def fmt_prefs(result, scenario):
    satisfied = preferences_satisfied(result, scenario)
    return "–" if satisfied is None else f"{satisfied}/{len(scenario['preferences'])}"


def pair_text(pair):
    return f"{guest_label(pair[0])} & {guest_label(pair[1])}"


# =============================================================================
# STYLING
# =============================================================================

CSS = """
<style>
.block-container {padding-top: 3.5rem; max-width: 1200px;}
.stButton button[kind="primary"] {background: #4F5BD5; border-color: #4F5BD5; color: #FFFFFF;}
.stButton button[kind="primary"]:hover {background: #3F4AC0; border-color: #3F4AC0; color: #FFFFFF;}
.app-title {font-size: 2.4rem !important; font-weight: 700; margin: 0; line-height: 1.2;}
.app-subtitle {font-size: 1.1rem !important; opacity: .65; margin: .2rem 0 1.2rem;}
.section-title {font-size: 1.25rem; font-weight: 650; margin: 1.6rem 0 .6rem;}
.example-badge {display: inline-block; padding: .2rem .7rem; border-radius: 6px;
  background: rgba(217,119,6,.12); border: 1px solid rgba(217,119,6,.45);
  color: #B45309; font-size: .82rem; font-weight: 600; margin-bottom: .8rem;}
.chips {display: flex; flex-wrap: wrap; gap: .5rem; margin: .2rem 0 .4rem;}
.chip {padding: .3rem .8rem; border-radius: 999px; font-size: .9rem;
  background: rgba(79,91,213,.10); border: 1px solid rgba(79,91,213,.28);}
.algo-card {border: 1px solid rgba(127,127,127,.25); border-radius: 12px;
  padding: 1rem 1.1rem .6rem; background: rgba(127,127,127,.04); height: 100%;}
.algo-name {font-weight: 650; font-size: 1.08rem;}
.status-badge {display: inline-block; padding: .15rem .65rem; border-radius: 999px;
  color: white; font-size: .8rem; font-weight: 650; margin: .45rem 0 .7rem;}
.metric-row {display: flex; justify-content: space-between; gap: .5rem;
  padding: .4rem 0; border-top: 1px solid rgba(127,127,127,.15); font-size: .92rem;}
.metric-row span:first-child {opacity: .65;}
.metric-row span:last-child {font-weight: 600; font-variant-numeric: tabular-nums;}
.cmp-table {width: 100%; border-collapse: collapse; font-size: .95rem;}
.cmp-table th, .cmp-table td {padding: .6rem .8rem; text-align: left;
  border-bottom: 1px solid rgba(127,127,127,.18);}
.cmp-table th {font-weight: 650; background: rgba(127,127,127,.06);}
.cmp-table td {font-variant-numeric: tabular-nums;}
.cmp-table td:first-child {opacity: .7;}
.seat-grid {display: flex; flex-wrap: wrap; gap: 1rem; margin-top: .4rem;}
.seat-card {border: 1px solid rgba(127,127,127,.25); border-radius: 14px;
  padding: .6rem .6rem .8rem; width: 236px; text-align: center;
  background: rgba(127,127,127,.04);}
.seat-list {font-size: .85rem; opacity: .7; margin-top: .2rem;}
.legend {display: flex; gap: 1.2rem; font-size: .85rem; opacity: .75; margin: .3rem 0 .2rem;}
.legend span {display: inline-flex; align-items: center; gap: .35rem;}
.dot {width: 14px; height: 14px; border-radius: 50%; display: inline-block;}
</style>
"""


# =============================================================================
# DASHBOARD PIECES
# =============================================================================

def render_summary(scenario, level):
    hard = len(scenario["together"]) + len(scenario["apart"]) + len(scenario["fixed"])
    chips = [
        f"{len(scenario['guests'])} Guests",
        f"{scenario['num_tables']} Tables",
        f"{level} Constraints",
        f"{hard} Hard Constraints",
        f"{len(scenario['preferences'])} Preferences",
    ]
    html = "".join(f'<span class="chip">{c}</span>' for c in chips)
    st.markdown(f'<div class="chips">{html}</div>', unsafe_allow_html=True)


def render_cards(results, scenario):
    columns = st.columns(len(results))
    for col, r in zip(columns, results):
        color = STATUS_COLORS.get(r["status"], "#6B7280")
        rows = [
            ("Assignments tried", fmt_count(r["assignments"])),
            ("Execution time", fmt_time(r["time"])),
            ("Preferences satisfied", fmt_prefs(r, scenario)),
        ]
        rows_html = "".join(
            f'<div class="metric-row"><span>{k}</span><span>{v}</span></div>' for k, v in rows
        )
        col.markdown(
            f'<div class="algo-card" style="border-top: 5px solid {color};">'
            f'<div class="algo-name">{r["name"]}</div>'
            f'<span class="status-badge" style="background:{color};">{r["status"]}</span>'
            f'{rows_html}</div>',
            unsafe_allow_html=True,
        )


def render_comparison_table(results, scenario):
    header = "".join(f"<th>{SHORT_NAMES.get(r['name'], r['name'])}</th>" for r in results)

    def status_cell(r):
        color = STATUS_COLORS.get(r["status"], "#6B7280")
        return f'<td><span style="color:{color}; font-weight:650;">● {r["status"]}</span></td>'

    rows = [
        ("Result", "".join(status_cell(r) for r in results)),
        ("Assignments tried", "".join(f"<td>{fmt_count(r['assignments'])}</td>" for r in results)),
        ("Execution time", "".join(f"<td>{fmt_time(r['time'])}</td>" for r in results)),
        ("Preferences satisfied", "".join(f"<td>{fmt_prefs(r, scenario)}</td>" for r in results)),
    ]
    body = "".join(f"<tr><td>{label}</td>{cells}</tr>" for label, cells in rows)
    st.markdown(
        f'<table class="cmp-table"><thead><tr><th>Metric</th>{header}</tr></thead>'
        f"<tbody>{body}</tbody></table>",
        unsafe_allow_html=True,
    )


def table_svg(table_no, guests, capacity):
    """One round table with numbered guest circles around it. Empty seats are dashed."""
    size, c = 220, 110
    table_r, ring_r, seat_r = 50, 84, 17
    parts = [
        f'<svg viewBox="0 0 {size} {size}" width="{size}" height="{size}" '
        f'xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Table {table_no}">',
        f'<circle cx="{c}" cy="{c}" r="{table_r}" fill="{TABLE_FILL}" stroke="{TABLE_STROKE}" stroke-width="2"/>',
        f'<text x="{c}" y="{c - 9}" text-anchor="middle" dominant-baseline="central" '
        f'font-size="15" font-weight="700" fill="#1F2A5A">Table {table_no}</text>',
        f'<text x="{c}" y="{c + 13}" text-anchor="middle" dominant-baseline="central" '
        f'font-size="13" fill="#4B5577">{len(guests)}/{capacity}</text>',
    ]
    for i in range(capacity):
        angle = -math.pi / 2 + 2 * math.pi * i / capacity
        x = c + ring_r * math.cos(angle)
        y = c + ring_r * math.sin(angle)
        if i < len(guests):
            label = guest_label(guests[i])
            parts.append(
                f'<g><title>Guest {label}</title>'
                f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{seat_r}" fill="{GUEST_COLOR}"/>'
                f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="middle" dominant-baseline="central" '
                f'font-size="13" font-weight="650" fill="#FFFFFF">{label}</text></g>'
            )
        else:
            parts.append(
                f'<g><title>Empty seat</title>'
                f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{seat_r}" fill="none" '
                f'stroke="#9AA0B4" stroke-width="1.5" stroke-dasharray="4 3"/></g>'
            )
    parts.append("</svg>")
    return "".join(parts)


def render_seating(assignment, scenario):
    tables = {t: [] for t in range(1, scenario["num_tables"] + 1)}
    for guest, table in assignment.items():
        tables.setdefault(table, []).append(guest)

    cards = []
    for table_no in sorted(tables):
        guests = sorted(tables[table_no], key=guest_sort_key)
        listing = ", ".join(guest_label(g) for g in guests) or "No guests"
        cards.append(
            f'<div class="seat-card">{table_svg(table_no, guests, scenario["capacity"])}'
            f'<div class="seat-list">{listing}</div></div>'
        )

    st.markdown(
        f'<div class="legend"><span><i class="dot" style="background:{GUEST_COLOR};"></i>Guest</span>'
        f'<span><i class="dot" style="border:1.5px dashed #9AA0B4;"></i>Empty seat</span></div>'
        f'<div class="seat-grid">{"".join(cards)}</div>',
        unsafe_allow_html=True,
    )


def render_scenario_details(scenario, shown_result):
    with st.expander("View Scenario Details"):
        col1, col2, col3, col4 = st.columns(4)

        def pair_list(col, title, caption, pairs):
            col.markdown(f"**{title}**")
            col.caption(caption)
            col.markdown("\n".join(f"- {pair_text(p)}" for p in pairs) if pairs else "_None_")

        pair_list(col1, "Together", "Must share a table", scenario["together"])
        pair_list(col2, "Apart", "Must sit at different tables", scenario["apart"])

        col3.markdown("**Fixed**")
        col3.caption("Assigned to a specific table")
        fixed = scenario["fixed"]
        col3.markdown(
            "\n".join(f"- {guest_label(g)} → Table {t}"
                      for g, t in sorted(fixed.items(), key=lambda kv: guest_sort_key(kv[0])))
            if fixed else "_None_"
        )

        col4.markdown("**Soft preferences**")
        assignment = shown_result["assignment"] if shown_result else None
        if assignment:
            col4.caption(f"Prefer to sit together (✓ = satisfied by {SHORT_NAMES[shown_result['name']]})")
            lines = [f"- {'✓' if assignment.get(a) == assignment.get(b) else '✗'} {pair_text((a, b))}"
                     for a, b in scenario["preferences"]]
        else:
            col4.caption("Prefer to sit together")
            lines = [f"- {pair_text(p)}" for p in scenario["preferences"]]
        col4.markdown("\n".join(lines) if lines else "_None_")


# =============================================================================
# PAGE
# =============================================================================

st.set_page_config(page_title="Event Seating Planner", page_icon="🪑", layout="wide")
st.markdown(CSS, unsafe_allow_html=True)
st.markdown('<div class="app-title">Event Seating Planner</div>'
            '<div class="app-subtitle">CSP-Based Seating Optimization</div>',
            unsafe_allow_html=True)

# ---- Scenario selection ------------------------------------------------------
with st.container(border=True):
    c1, c2, c3, c4 = st.columns([3, 2, 3, 1.4])
    size_label = c1.selectbox("Event size", list(EVENT_SIZES))
    level = c2.selectbox("Constraint level", CONSTRAINT_LEVELS)
    algorithm_choice = c3.selectbox("Algorithm", ALGORITHMS + [COMPARE_ALL], index=3)
    seed = int(c4.number_input("Random seed", min_value=0, value=42, step=1))
    run_clicked = st.button("Run Seating Planner", type="primary")

config = (EVENT_SIZES[size_label], level, seed, algorithm_choice)

if run_clicked:
    with st.spinner("Running the seating planner..."):
        scenario, results = run_planner(*config)
    st.session_state["run"] = {"config": config, "scenario": scenario, "results": results}

run = st.session_state.get("run")

if run is None:
    st.info("Choose an event size, constraint level and algorithm, then click **Run Seating Planner**.")
    st.stop()

if run["config"] != config:
    st.caption("⚠️ You changed the settings. Click **Run Seating Planner** to update the results below.")

scenario, results = run["scenario"], run["results"]
_, run_level, _, run_choice = run["config"]

# ---- Results -----------------------------------------------------------------
st.markdown('<div class="section-title">Results</div>', unsafe_allow_html=True)
if USE_EXAMPLE_DATA:
    st.markdown('<span class="example-badge">EXAMPLE DATA – not real algorithm results yet</span>',
                unsafe_allow_html=True)
render_summary(scenario, run_level)
render_cards(results, scenario)

if run_choice == COMPARE_ALL:
    st.markdown('<div class="section-title">Algorithm Comparison</div>', unsafe_allow_html=True)
    render_comparison_table(results, scenario)

# ---- Seating arrangement -----------------------------------------------------
st.markdown('<div class="section-title">Seating Arrangement</div>', unsafe_allow_html=True)

solved = [r for r in results if r["status"] == "Solved" and r["assignment"]]
not_solved = [r for r in results if r not in solved]

shown = None
if len(solved) > 1:
    pick = st.radio("Show seating arrangement for:",
                    [SHORT_NAMES[r["name"]] for r in solved], horizontal=True)
    shown = next(r for r in solved if SHORT_NAMES[r["name"]] == pick)
elif len(solved) == 1:
    shown = solved[0]
    st.caption(f"Showing the solution found by {shown['name']}.")

for r in not_solved:
    st.warning(f"**{r['name']}** {STATUS_MESSAGES.get(r['status'], 'did not find a solution.')}")

if shown:
    render_seating(shown["assignment"], scenario)
elif not solved:
    st.error("No algorithm found a valid seating arrangement for this scenario.")

# ---- Scenario details --------------------------------------------------------
st.markdown('<div class="section-title">Scenario</div>', unsafe_allow_html=True)
render_scenario_details(scenario, shown)


# Event Seating Planner

**AAIN-7001 – Foundations of Artificial Intelligence**

**Team:** Mario Mousa and Denisha Singh

## About Our Project

Our project is an Event Seating Planner that uses Constraint Satisfaction Problems (CSP) to assign guests to tables.

The idea is to create a seating arrangement that follows certain rules while trying to satisfy guest preferences.

We are comparing three different algorithms to see how they perform when the number of guests and constraints increases:

1. **Greedy First-Fit:** Our baseline. It assigns each guest to the first table that works and never goes back to change previous decisions.
2. **Plain Backtracking:** Tries different assignments and goes back when a choice leads to a dead end.
3. **Backtracking with MRV + Forward Checking:** Uses Minimum Remaining Values (MRV), Degree Heuristic for ties, and Forward Checking to reduce unnecessary search.

Our goal is to compare how well these algorithms solve the same seating problems.

## How Our CSP Works

Each guest is a variable, and the available tables are the possible values (domains).

Every guest must be assigned to exactly one table.

### Hard Constraints

These rules must always be satisfied:

- **Capacity:** Each table can have a maximum of 8 guests.
- **Together:** Two guests must sit at the same table.
- **Apart:** Two guests cannot sit at the same table.
- **Fixed:** A guest must sit at a specific table.

An assignment is only valid if all guests have a table and none of these rules are broken.

### Soft Preferences

Some guests would prefer to sit together, but these preferences do not have to be satisfied for an assignment to be valid.

Each satisfied preference gives 1 point.

We use this score to measure the quality of a seating arrangement.

Right now, our algorithms stop when they find the first valid solution. Improving preference satisfaction is one of our next steps.

## Project Files

- `main.py` – Runs the program, shows the menus, generates scenarios, and compares the algorithms.
- `constraints.py` – Checks the hard constraints and counts satisfied preferences.
- `greedy.py` – Implements our Greedy First-Fit baseline.
- `backtracking.py` – Implements Plain Backtracking.
- `mrv_fc.py` – Implements Backtracking with MRV, Degree Heuristic, and Forward Checking.

## How to Run the Program

### Requirements

- Python 3
- A terminal or VS Code

We only use Python's standard library, so no additional packages are needed.

### Running the Project

1. Download or clone this repository.
2. Open the project folder in VS Code or a terminal.
3. Run:

```bash
python main.py
```

If your computer uses `python3`, you can run:

```bash
python3 main.py
```

The program will ask you to choose the event size, constraint level, and algorithm.

### Step 1: Choose the Event Size

There are four options:

| Event | Guests | Tables |
|---|---|---|
| Demo | 6 | 2 |
| Small | 12 | 2 |
| Medium | 24 | 4 |
| Large | 36 | 5 |

Every table has a maximum capacity of 8 guests.

### Step 2: Choose the Constraint Level

We use three levels:

- **Low:** 1 hard constraint for every 6 guests.
- **Medium:** 1 hard constraint for every 3 guests.
- **High:** 1 hard constraint for every 2 guests.

The constraints are divided between together, apart, and fixed seating rules.

### Step 3: Choose an Algorithm

The program allows you to select:

1. Greedy First-Fit
2. Plain Backtracking
3. MRV + Forward Checking
4. Compare All Algorithms

The Compare All option runs the three algorithms using the same generated scenario.

## How We Generate Scenarios

Instead of entering every guest and constraint manually, the program generates scenarios automatically.

It creates:

- A list of guests.
- The available tables.
- Together constraints.
- Apart constraints.
- Fixed seating assignments.
- Soft preferences.

We first create a temporary reference seating arrangement and use it to generate compatible hard constraints.

This means our automatically generated scenarios have at least one valid solution.

The reference arrangement is only used to create the problem. It is never given to the algorithms as a solution.

We currently use `random.seed(42)` so we can reproduce the same scenarios when testing our code.

## Algorithm Comparison

When we select Compare All, the program shows the results of the three algorithms on the same seating problem.

We compare:

- **Result:** Whether the algorithm found a solution, failed, or reached its time limit.
- **Assignments tried:** How many guest-to-table assignments the algorithm attempted.
- **Execution time:** How long the algorithm took to run.
- **Preferences satisfied:** How many soft preferences were satisfied.

Forward Checking also performs additional checks when updating domains. These checks are included in the execution time but are not counted as assignment attempts.

We also display the seating arrangement grouped by table when an algorithm finds a solution.

### Time Limits

Plain Backtracking and MRV + Forward Checking currently have a 10-second time limit.

This prevents large scenarios from running indefinitely.

If an algorithm reaches the limit, we report a timeout rather than saying that no solution exists.

Greedy is different because it does not backtrack. If it gets stuck, it stops and reports that it could not find a valid assignment.

## What We Have Found So Far

Our initial tests have shown some interesting differences:

- Greedy is very fast, but it can fail even when a valid arrangement exists.
- Plain Backtracking can find solutions by changing previous decisions, but it can become very slow with larger problems.
- MRV and Forward Checking can greatly reduce the number of assignments needed to find a valid solution.

For example, in one scenario with 36 guests and High constraints:

| Metric | Greedy | Backtracking | MRV + FC |
|---|---|---|---|
| Result | Failed | Timeout | Solved |
| Assignments tried | 20 | 3,335,887 | 40 |
| Execution time | 0.000075 s | 10.000018 s | 0.012491 s |
| Preferences satisfied | - | - | 0/6 |

These are preliminary results from one scenario, not our final evaluation.

They help us understand why using CSP heuristics can be useful.

## Our Evaluation Plan

For the final evaluation, we plan to test three event sizes:

- 12 guests
- 24 guests
- 36 guests

Each event size will have Low, Medium, and High constraint levels.

We will generate three different reproducible scenarios for each combination.

This gives us:

**3 event sizes × 3 constraint levels × 3 scenarios = 27 feasible scenarios.**

We will also create 3 intentionally infeasible scenarios, giving us 30 scenarios in total.

All three algorithms will be tested on the same scenarios.

We plan to compare success rate, execution time, attempted assignments, backtracks, and preference satisfaction.

## Next Steps

We have implemented the three basic algorithms and connected them to our terminal interface.

Our next steps are:

1. Test the algorithms on more scenarios.
2. Extend both Backtracking methods to search for better preference scores within a time limit.
3. Create the intentionally infeasible scenarios.
4. Run the full evaluation with multiple random seeds.
5. Analyze the results and prepare our final report and presentation.

The main focus of our project is understanding the differences between the algorithms and evaluating their performance, rather than building a graphical interface.

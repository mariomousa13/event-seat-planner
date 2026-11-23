
import time

from constraints import is_valid
from greedy import greedy_first_fit, greedy_optimize
from backtracking import backtracking_search
from mrv_fc import mrv_fc_search


#######################
# IMPOSSIBLE SCENARIOS
#######################

# Each scenario has a different conflict between hard constraints
scenarios = [
    {
        "name": "Together and Apart Conflict",
        "guests": ["Guest1", "Guest2"],
        "tables": [1, 2],
        "capacity": 2,
        "together": [("Guest1", "Guest2")],
        "apart": [("Guest1", "Guest2")],
        "fixed": {},
        "preferences": []
    },
    {
        "name": "Capacity Conflict",
        "guests": ["Guest1", "Guest2", "Guest3"],
        "tables": [1, 2],
        "capacity": 2,
        "together": [
            ("Guest1", "Guest2"),
            ("Guest2", "Guest3")
        ],
        "apart": [],
        "fixed": {},
        "preferences": []
    },
    {
        "name": "Fixed Table Conflict",
        "guests": ["Guest1", "Guest2"],
        "tables": [1, 2],
        "capacity": 2,
        "together": [("Guest1", "Guest2")],
        "apart": [],
        "fixed": {
            "Guest1": 1,
            "Guest2": 2
        },
        "preferences": []
    }
]


#######################
# TEST THE ALGORITHMS
#######################

for scenario in scenarios:

    print("\n================================")
    print(scenario["name"].upper())
    print("================================")

    # Get the scenario information
    guests = scenario["guests"]
    tables = scenario["tables"]
    capacity = scenario["capacity"]
    together = scenario["together"]
    apart = scenario["apart"]
    fixed = scenario["fixed"]
    preferences = scenario["preferences"]

    # Test both search modes
    for search_mode in ["first_valid", "optimize"]:

        print("\nSearch mode:", search_mode)
        print("-" * 65)

        # Run all three algorithms
        for algorithm in ["Greedy", "Backtracking", "MRV + FC"]:

            start = time.perf_counter()

            if algorithm == "Greedy":

                if search_mode == "first_valid":

                    assignment, attempts = greedy_first_fit(
                        guests, tables, capacity, together, apart, fixed
                    )

                    timed_out = False

                else:

                    assignment, attempts, restarts, timed_out = greedy_optimize(
                        guests, tables, capacity, together, apart, fixed,
                        preferences, time_limit=10, seed=42
                    )

            elif algorithm == "Backtracking":

                assignment, attempts, timed_out = backtracking_search(
                    guests, tables, capacity, together, apart, fixed,
                    time_limit=10,
                    search_mode=search_mode,
                    preferences=preferences
                )

            else:

                assignment, attempts, timed_out = mrv_fc_search(
                    guests, tables, capacity, together, apart, fixed,
                    time_limit=10,
                    search_mode=search_mode,
                    preferences=preferences
                )

            # Calculate the execution time
            elapsed = time.perf_counter() - start

            # Check if the seating plan is complete and valid
            valid = assignment is not None

            if valid:
                valid = len(assignment) == len(guests) and is_valid(
                    assignment, capacity, together, apart, fixed
                )

            # Show the result
            print(
                f"{algorithm:<15} "
                f"Valid: {str(valid):<6} "
                f"Timeout: {str(timed_out):<6} "
                f"Time: {elapsed:.4f}s "
                f"Attempts: {attempts}"
            )


print("\n================================")
print("INFEASIBLE TESTS COMPLETE")
print("================================")

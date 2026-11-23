
import time
import csv

from scenarios import generate_scenario
from constraints import is_valid, count_preferences
from greedy import greedy_first_fit, greedy_optimize
from backtracking import backtracking_search
from mrv_fc import mrv_fc_search


#######################
# EVALUATE ONE ALGORITHM
#######################

def evaluate_algorithm(algorithm, search_mode, scenario, seed):

    # Get the scenario information
    guests = scenario["guests"]
    tables = scenario["tables"]
    capacity = scenario["capacity"]
    together = scenario["together"]
    apart = scenario["apart"]
    fixed = scenario["fixed"]
    preferences = scenario["preferences"]

    # Use the same time limit for all algorithms
    time_limit = 10

    # Start measuring the execution time
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
                preferences, time_limit=time_limit, seed=seed
            )

    elif algorithm == "Backtracking":

        assignment, attempts, timed_out = backtracking_search(
            guests, tables, capacity, together, apart, fixed,
            time_limit=time_limit,
            search_mode=search_mode,
            preferences=preferences
        )

    elif algorithm == "MRV + FC":

        assignment, attempts, timed_out = mrv_fc_search(
            guests, tables, capacity, together, apart, fixed,
            time_limit=time_limit,
            search_mode=search_mode,
            preferences=preferences
        )

    # Measure the total execution time
    elapsed = time.perf_counter() - start

    # Check if we found a valid seating plan
    valid = assignment is not None

    if valid:
        valid = len(assignment) == len(guests) and is_valid(
            assignment, capacity, together, apart, fixed
        )

    # Count preferences only for valid seating plans
    if valid:
        score = count_preferences(assignment, preferences)
    else:
        score = 0

    # Save the results
    return {
        "algorithm": algorithm,
        "mode": search_mode,
        "valid": valid,
        "preferences": score,
        "total_preferences": len(preferences),
        "attempts": attempts,
        "time": elapsed,
        "timed_out": timed_out
    }



#######################
# RUN THE EVALUATION
#######################

if __name__ == "__main__":

    # Test different event sizes, constraint levels, and seeds
    event_sizes = [12, 24, 36]
    constraint_levels = ["low", "medium", "high"]
    seeds = [42, 43, 44]

    algorithms = ["Greedy", "Backtracking", "MRV + FC"]
    search_modes = ["first_valid", "optimize"]

    # Store all results
    results = []

    # Create a CSV file to save the results
    csv_file = "evaluation_results.csv"

    # Define the columns
    fieldnames = [
        "guests",
        "level",
        "seed",
        "algorithm",
        "mode",
        "valid",
        "preferences",
        "total_preferences",
        "attempts",
        "time",
        "timed_out"
    ]

    # Create the file and write the column names
    with open(csv_file, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

    print("\n================================")
    print("ALGORITHM EVALUATION")
    print("================================")

    # Generate each scenario once
    for num_guests in event_sizes:
        for level in constraint_levels:
            for seed in seeds:

                scenario = generate_scenario(num_guests, level, seed)

                print(
                    f"\nGuests: {num_guests} | "
                    f"Level: {level} | Seed: {seed}",
                    flush=True
                )

                # Test the same scenario with all algorithms and modes
                for search_mode in search_modes:
                    for algorithm in algorithms:

                        result = evaluate_algorithm(
                            algorithm, search_mode, scenario, seed
                        )

                        # Include the scenario details
                        result["guests"] = num_guests
                        result["level"] = level
                        result["seed"] = seed

                        results.append(result)
                        # Save each result immediately
                        with open(csv_file, "a", newline="", encoding="utf-8") as file:
                            writer = csv.DictWriter(file, fieldnames=fieldnames)
                            writer.writerow(result)

                        print(
                            f"{algorithm:<15} "
                            f"{search_mode:<12} "
                            f"Valid: {str(result['valid']):<5} "
                            f"Preferences: "
                            f"{result['preferences']}/{result['total_preferences']} "
                            f"Time: {result['time']:.4f}s",
                            flush=True
                        )

    print("\n================================")
    print("EVALUATION COMPLETE")
    print("================================")
    print("Total runs:", len(results))

    print("Results saved to:", csv_file)

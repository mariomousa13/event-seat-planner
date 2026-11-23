import random
import time
from constraints import is_valid, count_preferences


def greedy_first_fit(guests, tables, capacity, together, apart, fixed):
    """
    We go through the guests one by one and try to seat them
    at the first table that works.

    Greedy does not go back, so if a guest has no available
    table, we return None. We also count how many assignments
    we tried.
    """

    assignment = {}
    attempts = 0

    # Go through each guest
    for guest in guests:

        # Try the tables in order
        for table in tables:
            assignment[guest] = table
            attempts += 1

            # Check if this table works
            if is_valid(assignment, capacity, together, apart, fixed):
                break

            # If not, try the next one
            del assignment[guest]

        # No table worked for this guest
        if guest not in assignment:
            return None, attempts

    # All guests have a table
    return assignment, attempts



def greedy_optimize(guests, tables, capacity, together, apart, fixed,
                    preferences, time_limit=10, seed=42):

    # Keep the best seating plan we find
    best_solution = None
    best_score = -1

    # Count the assignments we try
    attempts = 0

    # Count how many seating plans we start
    restarts = 0

    # Use a seed so we can repeat the same test
    rng = random.Random(seed)

    # Start the timer
    start = time.perf_counter()

    # Keep trying until we run out of time
    while time.perf_counter() - start < time_limit:

        # Start a new seating plan
        assignment = {}
        restarts += 1

        # Try guests and tables in a different order
        guest_order = guests.copy()
        table_order = tables.copy()

        rng.shuffle(guest_order)
        rng.shuffle(table_order)

        failed = False

        # Seat guests one at a time, like First-Fit
        for guest in guest_order:

            # Stop if we reach the time limit
            if time.perf_counter() - start >= time_limit:
                failed = True
                break

            # Start with the available tables
            preferred_tables = []

            # Check if a preferred guest is already seated
            for guest1, guest2 in preferences:

                if guest1 == guest and guest2 in assignment:
                    preferred_tables.append(assignment[guest2])

                elif guest2 == guest and guest1 in assignment:
                    preferred_tables.append(assignment[guest1])

            # Try preferred tables first, then the others
            ordered_tables = []

            for table in preferred_tables + table_order:
                if table not in ordered_tables:
                    ordered_tables.append(table)

            placed = False

            # Try each table until we find a valid one
            for table in ordered_tables:

                if time.perf_counter() - start >= time_limit:
                    failed = True
                    break

                # Try placing this guest at the table
                assignment[guest] = table
                attempts += 1

                # Keep the table if all hard constraints are satisfied
                if is_valid(assignment, capacity, together, apart, fixed):
                    placed = True
                    break

                # Remove the guest if the table does not work
                del assignment[guest]

            # Stop this attempt if the guest could not be seated
            if not placed:
                failed = True
                break

        # Skip incomplete seating plans
        if failed:
            continue

        # Make sure every guest has a valid table
        if len(assignment) != len(guests):
            continue

        if not is_valid(assignment, capacity, together, apart, fixed):
            continue

        # Count the satisfied preferences
        score = count_preferences(assignment, preferences)

        # Save this seating plan if it is better
        if score > best_score:
            best_score = score
            best_solution = assignment.copy()

        # Stop if we satisfied every preference
        if best_score == len(preferences):
            break

    # Check if the search reached the time limit
    timed_out = time.perf_counter() - start >= time_limit

    # Return the best solution and the search results
    return best_solution, attempts, restarts, timed_out




#######################
# TEST GREEDY OPTIMIZE
#######################

if __name__ == "__main__":

    from scenarios import generate_scenario

    # Generate a test scenario
    scenario = generate_scenario(24, "medium", 42)

    # Run Greedy Optimize
    solution, attempts, restarts, timed_out = greedy_optimize(
        scenario["guests"],
        scenario["tables"],
        scenario["capacity"],
        scenario["together"],
        scenario["apart"],
        scenario["fixed"],
        scenario["preferences"],
        time_limit=10,
        seed=42
    )

    # Show the results
    print("Solution found:", solution is not None)
    print("Assignments tried:", attempts)
    print("Restarts:", restarts)
    print("Time limit reached:", timed_out)

    if solution is not None:

        # Check that the seating plan follows all hard constraints
        valid = len(solution) == len(scenario["guests"]) and is_valid(
            solution,
            scenario["capacity"],
            scenario["together"],
            scenario["apart"],
            scenario["fixed"]
        )

        print("Valid assignment:", valid)

        # Count the preferences we satisfied
        score = count_preferences(solution, scenario["preferences"])
        print("Preferences satisfied:", score, "/", len(scenario["preferences"]))

        # Show the guests at each table
        print("\nSEATING ARRANGEMENT")

        for table in scenario["tables"]:
            table_guests = []

            for guest in scenario["guests"]:
                if solution[guest] == table:
                    table_guests.append(guest)

            print("Table", table, ":", ", ".join(table_guests))
            print("Seats used:", len(table_guests), "/", scenario["capacity"])

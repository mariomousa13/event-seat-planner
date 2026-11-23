import time
from constraints import is_valid, count_preferences


#######################
# MRV + DEGREE
#######################
def select_guest(guests, domains, assignment, together, apart):

    # We will save the best guest we find
    best_guest = None
    fewest_options = float("inf")
    highest_degree = -1

    # Go through all the guests
    for guest in guests:

        # Skip guests who already have a table
        if guest in assignment:
            continue

        # MRV: count how many tables this guest can still use
        options = len(domains[guest])

        # Count hard constraints with guests not assigned yet
        degree = 0

        for guest1, guest2 in together + apart:

            if guest1 == guest and guest2 not in assignment:
                degree += 1

            elif guest2 == guest and guest1 not in assignment:
                degree += 1

        # MRV: choose the guest with fewer options
        if options < fewest_options:
            best_guest = guest
            fewest_options = options
            highest_degree = degree

        # If MRV is tied, use the Degree Heuristic
        elif options == fewest_options and degree > highest_degree:
            best_guest = guest
            highest_degree = degree

    return best_guest



#######################
# INITIAL DOMAINS
#######################

def create_domains(guests, tables, fixed):

    # Store the available tables for each guest
    domains = {}

    # Go through each guest
    for guest in guests:

        # If the guest has a fixed table, that is the only option
        if guest in fixed:
            domains[guest] = [fixed[guest]]

        # Otherwise, the guest can sit at any table
        else:
            domains[guest] = tables.copy()

    return domains



#######################
# FORWARD CHECKING
#######################

def forward_check(guests, domains, assignment, capacity, together, apart, fixed):

    # Copy the domains so we do not change the original ones
    new_domains = {}

    for guest in guests:
        new_domains[guest] = domains[guest].copy()

    # Go through the guests
    for guest in guests:

        # Skip guests who already have a table
        if guest in assignment:
            new_domains[guest] = [assignment[guest]]
            continue

        # Check the tables this guest can still use
        for table in domains[guest]:

            # Try adding this guest to the current assignment
            test_assignment = assignment.copy()
            test_assignment[guest] = table

            # Remove the table if it breaks a hard constraint
            if not is_valid(test_assignment, capacity, together, apart, fixed):
                new_domains[guest].remove(table)

        # If a guest has no options left, this path cannot work
        if len(new_domains[guest]) == 0:
            return None

    return new_domains


#######################
# BACKTRACKING WITH MRV + FC
#######################

def backtrack_mrv_fc(assignment, guests, domains, capacity, together,
                     apart, fixed, attempts, start, time_limit, timed_out,
                     search_mode, preferences, best_solution, best_score):

    # Stop if we reach the time limit
    if time.perf_counter() - start >= time_limit:
        timed_out[0] = True
        return None

    # All guests have a table, so we found a valid solution
    if len(assignment) == len(guests):

        # Stop here if we only want the first valid solution
        if search_mode == "first_valid":
            return assignment.copy()

        # Count how many preferences this solution satisfies
        score = count_preferences(assignment, preferences)

        # Save this solution if it is better than the previous one
        if score > best_score[0]:
            best_score[0] = score
            best_solution[0] = assignment.copy()

        # Keep searching for a better solution
        return None

    # Choose the next guest using MRV and Degree Heuristic
    guest = select_guest(guests, domains, assignment, together, apart)

    #######################
    # PREFERENCE-AWARE VALUE ORDERING
    #######################

    # Start with the available tables in their original order
    ordered_tables = domains[guest].copy()

    # When optimizing, try tables that satisfy more preferences first
    if search_mode == "optimize":

        # Count the preferences we could satisfy at each table
        table_scores = {}

        for table in ordered_tables:

            score = 0

            # Check if this guest prefers to sit with someone already seated
            for guest1, guest2 in preferences:

                if guest1 == guest and guest2 in assignment:
                    if assignment[guest2] == table:
                        score += 1

                elif guest2 == guest and guest1 in assignment:
                    if assignment[guest1] == table:
                        score += 1

            table_scores[table] = score

        # Try tables with more satisfied preferences first
        ordered_tables.sort(
            key=lambda table: table_scores[table],
            reverse=True
        )

    #######################
    # TRY THE TABLES
    #######################

    # Try the tables in the selected order
    for table in ordered_tables:

        # Check the time before trying another table
        if time.perf_counter() - start >= time_limit:
            timed_out[0] = True
            return None

        assignment[guest] = table
        attempts[0] += 1

        # Check if the assignment follows the hard constraints
        if is_valid(assignment, capacity, together, apart, fixed):

            # Remove tables that no longer work for other guests
            new_domains = forward_check(
                guests, domains, assignment, capacity, together, apart, fixed
            )

            # Continue only if the other guests still have options
            if new_domains is not None:

                result = backtrack_mrv_fc(
                    assignment, guests, new_domains, capacity, together,
                    apart, fixed, attempts, start, time_limit, timed_out,
                    search_mode, preferences, best_solution, best_score
                )

                # Return the solution if we found one
                if result is not None:
                    return result

        # Remove this guest before trying another table
        del assignment[guest]

        # Stop if we already satisfied all preferences
        if search_mode == "optimize" and best_score[0] == len(preferences):
            return None

        # Stop searching if we ran out of time
        if timed_out[0]:
            return None

    # None of the tables worked, so go back
    return None



#######################
# MAIN MRV + FC FUNCTION
#######################


def mrv_fc_search(guests, tables, capacity, together, apart, fixed,
                  time_limit=10, search_mode="first_valid", preferences=None):

    # Count how many assignments we try
    attempts = [0]

    # Check if we run out of time
    timed_out = [False]

    # Keep the best seating plan we find
    best_solution = [None]
    best_score = [-1]

    # Use an empty list if there are no preferences
    if preferences is None:
        preferences = []

    # Start measuring the time
    start = time.perf_counter()

    # Create the starting domains for each guest
    domains = create_domains(guests, tables, fixed)

    # Start the search with an empty assignment
    result = backtrack_mrv_fc(
        {}, guests, domains, capacity, together, apart, fixed,
        attempts, start, time_limit, timed_out,
        search_mode, preferences, best_solution, best_score
    )

    # Return the best solution found when optimizing preferences
    if search_mode == "optimize":
        return best_solution[0], attempts[0], timed_out[0]

    # Otherwise, return the first valid solution
    return result, attempts[0], timed_out[0]



#######################
# TEST MRV + FC
#######################

# Only run this test when we execute mrv_fc.py directly
if __name__ == "__main__":

    from scenarios import generate_scenario

    # Generate a test scenario
    scenario = generate_scenario(24, "medium", 42)

    # Test both search modes
    for mode in ["first_valid", "optimize"]:

        print("\n================================")
        print("Search mode:", mode)
        print("================================")

        # Run MRV + FC
        start = time.perf_counter()

        assignment, attempts, timed_out = mrv_fc_search(
            scenario["guests"],
            scenario["tables"],
            scenario["capacity"],
            scenario["together"],
            scenario["apart"],
            scenario["fixed"],
            time_limit=10,
            search_mode=mode,
            preferences=scenario["preferences"]
        )

        elapsed = time.perf_counter() - start

        # Show the results
        print("Solution found:", assignment is not None)
        print("Assignments tried:", attempts)
        print("Execution time:", round(elapsed, 6), "seconds")
        print("Time limit reached:", timed_out)

        if assignment is not None:

            # Check that the seating plan follows all hard constraints
            valid = len(assignment) == len(scenario["guests"]) and is_valid(
                assignment,
                scenario["capacity"],
                scenario["together"],
                scenario["apart"],
                scenario["fixed"]
            )

            print("Valid assignment:", valid)

            # Count the preferences we satisfied
            score = count_preferences(assignment, scenario["preferences"])
            print("Preferences satisfied:", score, "/", len(scenario["preferences"]))


import time




#######################
# MRV + DEGREE
#######################
from constraints import is_valid
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
                     apart, fixed, attempts, start, time_limit, timed_out):

    # Stop if we reach the time limit
    if time.perf_counter() - start >= time_limit:
        timed_out[0] = True
        return None

    # All guests have a table, so we found a solution
    if len(assignment) == len(guests):
        return assignment.copy()

    # Choose the next guest using MRV and Degree Heuristic
    guest = select_guest(guests, domains, assignment, together, apart)

    # Try the tables that are still available for this guest
    for table in domains[guest]:

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
                    apart, fixed, attempts, start, time_limit, timed_out
                )

                # Return the solution if we found one
                if result is not None:
                    return result

        # If this choice did not work, remove the guest
        del assignment[guest]

        # Stop searching if we ran out of time
        if timed_out[0]:
            return None

    # None of the tables worked, so go back
    return None


#######################
# MAIN MRV + FC FUNCTION
#######################

def mrv_fc_search(guests, tables, capacity, together, apart, fixed, time_limit=10):

    # Count how many assignments we try
    attempts = [0]

    # Check if we run out of time
    timed_out = [False]

    # Create the starting domains for each guest
    domains = create_domains(guests, tables, fixed)

    # Start measuring the time
    start = time.perf_counter()

    # Start the search with an empty assignment
    result = backtrack_mrv_fc(
        {}, guests, domains, capacity, together, apart, fixed,
        attempts, start, time_limit, timed_out
    )

    # Return the result and the information we collected
    return result, attempts[0], timed_out[0]


#######################
# TEST MRV + FC
#######################

# Only run this test when we execute mrv_fc.py directly
if __name__ == "__main__":

    # Create a small seating problem
    guests = ["Guest1", "Guest2", "Guest3", "Guest4"]
    tables = [1, 2, 3]
    capacity = 2

    # Set the hard constraints
    fixed = {"Guest3": 2}
    together = [("Guest3", "Guest4")]
    apart = [("Guest3", "Guest1")]

    # Run the algorithm
    assignment, attempts, timed_out = mrv_fc_search(
        guests, tables, capacity, together, apart, fixed
    )

    # Show what happened
    print("Assignment:", assignment)
    print("Assignments tried:", attempts)
    print("Time limit reached:", timed_out)

    # Check the final seating plan
    if assignment is not None:
        print("Valid assignment:", is_valid(
            assignment, capacity, together, apart, fixed
        ))



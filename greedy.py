
from constraints import is_valid


def greedy_first_fit(guests, tables, capacity, together, apart, fixed):
    """Assign guests to the first table that works."""

    assignment = {}

    # Go through each guest
    for guest in guests:

        # Try the available tables
        for table in tables:
            assignment[guest] = table

            # Check if the assignment is consistent
            if is_valid(assignment, capacity, together, apart, fixed):
                break

            # Remove the assignment if it breaks a rule
            del assignment[guest]

        # No table worked for this guest
        if guest not in assignment:
            return None

    return assignment

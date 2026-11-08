
from constraints import is_valid


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

import time
from constraints import is_valid


def backtracking_search(guests, tables, capacity, together, apart, fixed, time_limit = 10):

    # We use a list so the recursive function can update the counter
    attempts = [0]
    timed_out = [False]

    # Start the timer
    start = time.perf_counter()

    result = backtrack({}, guests, tables, capacity, together, apart, fixed, attempts, start, time_limit, timed_out)

    return result, attempts[0], timed_out[0]


def backtrack(assignment, guests, tables, capacity, together, apart, fixed, attempts,start, time_limit, timed_out):

    # Stop if we reach the time limit
    if time.perf_counter() - start >= time_limit:
        timed_out[0] = True
        return None

    # Every guest has a table, so the assignment is complete
    if len(assignment) == len(guests):
        return assignment

    # Find the first guest who has not been assigned
    guest = None

    for g in guests:
        if g not in assignment:
            guest = g
            break

    # Try the tables in order
    for table in tables:

        # Check the time before trying another table
        if time.perf_counter() - start >= time_limit:
            timed_out[0] = True
            return None
        
        assignment[guest] = table
        attempts[0] += 1

        # Check if this table works
        if is_valid(assignment, capacity, together, apart, fixed):

            # Continue with the next guest
            result = backtrack(assignment, guests, tables, capacity,
                               together, apart, fixed, attempts, start, time_limit, timed_out)

            if result is not None:
                return result

        # Dead end, so remove this table and try the next one
        del assignment[guest]

        # Stop searching if we ran out of time
        if timed_out[0]:
            return None

    # No table worked for this guest, so go back to the previous guest
    return None
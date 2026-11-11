from constraints import is_valid


def backtracking_search(guests, tables, capacity, together, apart, fixed):

    # We use a list so the recursive function can update the counter
    attempts = [0]

    result = backtrack({}, guests, tables, capacity, together, apart, fixed, attempts)

    return result, attempts[0]


def backtrack(assignment, guests, tables, capacity, together, apart, fixed, attempts):

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
        assignment[guest] = table
        attempts[0] += 1

        # Check if this table works
        if is_valid(assignment, capacity, together, apart, fixed):

            # Continue with the next guest
            result = backtrack(assignment, guests, tables, capacity,
                               together, apart, fixed, attempts)

            if result is not None:
                return result

        # Dead end, so remove this table and try the next one
        del assignment[guest]

    # No table worked for this guest, so go back to the previous guest
    return None
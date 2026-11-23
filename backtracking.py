import time
from constraints import is_valid, count_preferences


def backtracking_search(guests, tables, capacity, together, apart, fixed, time_limit = 10, search_mode="first_valid", preferences=None):

    # We use a list so the recursive function can update the counter
    attempts = [0]
    timed_out = [False]

    # we keep the best seating plan we find
    best_solution = [None]
    best_score = [-1]

    # Start the timer
    start = time.perf_counter()

    # Use an empty list if there are no preferences
    if preferences is None:
        preferences = []

    result = backtrack({}, guests, tables, capacity, together, apart, fixed,
                       attempts, start, time_limit, timed_out,
                       search_mode, preferences, best_solution, best_score)
    
    # Return the best solution found when optimizing preferences
    if search_mode == "optimize":
        return best_solution[0], attempts[0], timed_out[0]

    return result, attempts[0], timed_out[0]


def backtrack(assignment, guests, tables, capacity, together, apart, fixed, attempts, start, time_limit, timed_out,
              search_mode, preferences, best_solution, best_score):
    # Stop if we reach the time limit
    if time.perf_counter() - start >= time_limit:
        timed_out[0] = True
        return None

    # Every guest has a table, so we found a valid solution
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
                   together, apart, fixed, attempts, start, time_limit, timed_out,
                   search_mode, preferences, best_solution, best_score)

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

    # No table worked for this guest, so go back to the previous guest
    return None
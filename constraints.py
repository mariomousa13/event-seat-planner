
def is_valid(assignment, capacity, together, apart, fixed):

    # Table capacity
    assigned_tables = list(assignment.values())

    for table in assigned_tables:
        if assigned_tables.count(table) > capacity:
            return False

    # Guests who must sit together
    for guest1, guest2 in together:
        if guest1 in assignment and guest2 in assignment:
            if assignment[guest1] != assignment[guest2]:
                return False

    # Guests who cannot sit together
    for guest1, guest2 in apart:
        if guest1 in assignment and guest2 in assignment:
            if assignment[guest1] == assignment[guest2]:
                return False

    # Fixed table assignments
    for guest, table in fixed.items():
        if guest in assignment:
            if assignment[guest] != table:
                return False

    return True



def count_preferences(assignment, preferences):
    """Count how many guest preferences are satisfied."""

    count = 0

    for guest1, guest2 in preferences:
        if guest1 in assignment and guest2 in assignment:
            if assignment[guest1] == assignment[guest2]:
                count += 1

    return count

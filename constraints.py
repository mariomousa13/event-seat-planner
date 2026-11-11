
def is_valid(assignment, capacity, together, apart, fixed):

    # Check fixed seats first
    for guest, table in fixed.items():
        if guest in assignment:
            if assignment[guest] != table:
                return False

    # Check guests who must sit together
    for guest1, guest2 in together:
        if guest1 in assignment and guest2 in assignment:
            if assignment[guest1] != assignment[guest2]:
                return False

    # Check guests who cannot sit together
    for guest1, guest2 in apart:
        if guest1 in assignment and guest2 in assignment:
            if assignment[guest1] == assignment[guest2]:
                return False

    # Count how many guests are at each table
    table_counts = {}

    for table in assignment.values():
        if table not in table_counts:
            table_counts[table] = 0

        table_counts[table] += 1

        # Stop if the table is full
        if table_counts[table] > capacity:
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

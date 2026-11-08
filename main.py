
from constraints import is_valid, count_preferences
from greedy import greedy_first_fit

# Variables: guests
guests = ["James", "Emma", "Oliver", "Sophia", "Liam", "Chloe"]

# Domains: available tables
tables = [1, 2]

# Maximum capacity per table
capacity = 8

# Hard constraints
together = [("James", "Emma")]
apart = [("James", "Oliver")]
fixed = {"Sophia": 2}

# Soft constraints
preferences = [("Liam", "Chloe")]


# Run the Greedy First-Fit baseline
assignment = greedy_first_fit(guests, tables, capacity, together, apart, fixed)

# Check the result
if assignment is not None:
    print("Greedy assignment:", assignment)
    print("Valid assignment:", is_valid(
        assignment, capacity, together, apart, fixed
    ))
    score = count_preferences(assignment, preferences)
    print("Preferences satisfied:", score, "/", len(preferences))
else:
    print("Greedy could not find a valid assignment.")

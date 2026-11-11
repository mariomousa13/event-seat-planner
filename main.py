import random
import time

from constraints import is_valid, count_preferences
from greedy import greedy_first_fit
from backtracking import backtracking_search

# Hard constraints
together = [("James", "Emma")]
apart = [("James", "Oliver"), ("Liam", "Chloe")]
fixed = {"Sophia": 2, "Chloe": 1}


# Soft constraints
preferences = [("Liam", "Chloe")]


###############################
# EVENT SIZE
###############################

# Choose the event size
print("\n================================")
print("EVENT SEATING PLANNER")
print("================================")
print("1. Demo - 6 guests")
print("2. Small - 12 guests")
print("3. Medium - 24 guests")
print("4. Large - 36 guests")
print("5. Exit")

choice = input("Choose the event size: ")

# Save the selected number of guests
if choice == "1":
    num_guests = 6

elif choice == "2":
    num_guests = 12

elif choice == "3":
    num_guests = 24

elif choice == "4":
    num_guests = 36

elif choice == "5":
    num_guests = None
    print("Exiting the program")

else:
    num_guests = None
    print("Invalid option")

# Check the selected size
if num_guests is not None:
    print("Number of guests:", num_guests)

    guests = []

    for i in range(1, num_guests + 1):
        guests.append("Guest" + str(i))

    # print("Guests:", guests)
    print("Total guests:", len(guests))

    # Set the number of tables
    # The max capacity of each table is 8

    capacity = 8

    if num_guests == 6 or num_guests == 12:
        num_tables = 2

    elif num_guests == 24:
        num_tables = 4

    else:
        num_tables = 5

    # Create the list of available tables
    tables = list(range(1, num_tables + 1))

    print("Tables:", tables)


###############################
# CONSTRAINT LEVEL
###############################

# Choose the constraint level
print("\n================================")
print("CONSTRAINT LEVEL")
print("================================")
print("1. Low")
print("2. Medium")
print("3. High")

level_choice = input("Choose the constraint level: ")

# Save the selected level
if level_choice == "1":
    constraint_level = "low"

elif level_choice == "2":
    constraint_level = "medium"

elif level_choice == "3":
    constraint_level = "high"
    
else:
    constraint_level = None
    print("Invalid option")

# Check the selected level
if constraint_level is not None:
    print("Constraint level:", constraint_level)


# We use three constraint levels to test how the algorithms perform as the problem becomes more restricted.
# Low has 1 hard constraint for every 6 guests
#  Medium has 1 for every 3 guests
# High has 1 for every 2 guests
# These constraints can be together, apart, or fixed seating rules.


# Set the number of hard constraints
if constraint_level == "low":
    num_constraints = num_guests // 6

elif constraint_level == "medium":
    num_constraints = num_guests // 3

else:
    num_constraints = num_guests // 2

print("Number of hard constraints:", num_constraints)


# Split the hard constraints into three types
num_together = num_constraints // 3
num_apart = num_constraints // 3
num_fixed = num_constraints - num_together - num_apart

print("Together constraints:", num_together)
print("Apart constraints:", num_apart)
print("Fixed constraints:", num_fixed)




###############################
# SELECT THE ALGORITHM
###############################

# Choose the algorithm
print("\n================================")
print("ALGORITHM")
print("================================")
print("1. Greedy First-Fit")
print("2. Backtracking")
print("3. MRV + Forward Checking")
print("4. Compare all algorithms")

algorithm_choice = input("Choose an algorithm: ")

    # Save the selected algorithm
if algorithm_choice == "1":
    algorithm = "greedy"

elif algorithm_choice == "2":
    algorithm = "backtracking"

elif algorithm_choice == "3":
    algorithm = "mrv_fc"

elif algorithm_choice == "4":
    algorithm = "compare"
        
else:
    algorithm = None
    print("Invalid option")

# Check the selected algorithm
if algorithm is not None:
    print("Selected algorithm:", algorithm)


# We have to create a starting seating plan for our test scenarios
reference_assignment = {}
table = 1

# Assign guests to tables one by one
for guest in guests:
    reference_assignment[guest] = table

    # Move to the next table
    table += 1

    # Go back to the first one
    if table > len(tables):
        table = 1

# print("Reference assignment:", reference_assignment)

# We use a random seed to have the same choice while running the program again
random.seed(42)


#######################
# TOGETHER CONSTRAINT
#######################

# Store the together constraints
together = []

# Keep adding pairs until we reach the required number
while len(together) < num_together:

    # Choose a random table
    selected_table = random.choice(tables)

    # Find the guests at that table
    table_guests = []

    for guest in guests:
        if reference_assignment[guest] == selected_table:
            table_guests.append(guest)

    # Choose two guests from the same table
    guest1, guest2 = random.sample(table_guests, 2)

    # Make sure we do not add the same pair twice
    if (guest1, guest2) not in together and (guest2, guest1) not in together:
        together.append((guest1, guest2))

# print("Together:", together)
print("Total together constraints:", len(together))


#######################
# APART CONSTRAINT
#######################

# Store the apart constraints
apart = []

# Keep adding pairs until we reach the required number
while len(apart) < num_apart:

    # Choose the first guest randomly
    guest1 = random.choice(guests)

    # Find guests who are at a different table
    different_table_guests = []

    for guest in guests:
        if reference_assignment[guest] != reference_assignment[guest1]:
            different_table_guests.append(guest)

    # Choose the second guest randomly
    guest2 = random.choice(different_table_guests)

    # Avoid adding the same pair twice
    if (guest1, guest2) not in apart and (guest2, guest1) not in apart:
        apart.append((guest1, guest2))

# print("Apart:", apart)
print("Total apart constraints:", len(apart))


#######################
# FIXED CONSTRAINT
#######################

# Store the fixed constraints
fixed = {}

# Keep adding guests until we have enough fixed constraints
while len(fixed) < num_fixed:

    # Choose a random guest
    guest = random.choice(guests)

    # Get the guest's table from the reference assignment
    table = reference_assignment[guest]

    # Avoid choosing the same guest twice
    if guest not in fixed:
        fixed[guest] = table

# print("Fixed:", fixed)
print("Total fixed constraints:", len(fixed))



#######################
# SOFT CONSTRAINTS
#######################

# We use one preference for every 6 guests
# Each satisfied preference gives 1 point
num_preferences = num_guests // 6

# Store the guest preferences
preferences = []

# Keep adding preferences until we have enough
while len(preferences) < num_preferences:

    # Choose two random guests
    guest1, guest2 = random.sample(guests, 2)

    # Check both orders of the pair
    pair = (guest1, guest2)
    reverse_pair = (guest2, guest1)

    # Avoid duplicates and conflicts with hard constraints
    if (pair not in preferences and reverse_pair not in preferences
            and pair not in together and reverse_pair not in together
            and pair not in apart and reverse_pair not in apart):

        preferences.append(pair)

# print("Preferences:", preferences)
print("Total preferences:", len(preferences))



#######################
# SCENARIO SUMMARY
#######################

# Show the scenario we generated
print("\n================================")
print("EVENT DETAILS")
print("================================")

print("Guests:", num_guests)
print("Tables:", num_tables)
print("Capacity per table:", capacity)
print("Constraint level:", constraint_level)

print("\nHARD CONSTRAINTS")
print("Together:", together)
print("Apart:", apart)
print("Fixed:", fixed)

print("\nSOFT PREFERENCES")
print("Preferences:", preferences)



#######################
# GREEDY FIRST-FIT
#######################

# Run Greedy if selected or if we want to compare
if algorithm == "greedy" or algorithm == "compare":

    print("\n================================")
    print("GREEDY FIRST-FIT")
    print("================================")

    # Start the timer
    start = time.perf_counter()

    # Run Greedy
    assignment, attempts = greedy_first_fit(
        guests, tables, capacity, together, apart, fixed
    )

    # Calculate the execution time
    elapsed = time.perf_counter() - start

    print("Assignments tried:", attempts)
    print("Execution time:", round(elapsed, 6), "seconds")

    # Check if Greedy found a solution
    if assignment is None:
        print("No valid assignment found.")

    else:
        # Check the final assignment
        valid = len(assignment) == len(guests) and is_valid(
            assignment, capacity, together, apart, fixed
        )
        print("Valid assignment:", valid)

        # Count the satisfied preferences
        score = count_preferences(assignment, preferences)
        print("Preferences satisfied:", score, "/", len(preferences))

        # Show the guests at each table
        print("\nSEATING ARRANGEMENT")

        for table in tables:
            table_guests = []

            for guest in guests:
                if assignment[guest] == table:
                    table_guests.append(guest)

            print("Table", table, ":", ", ".join(table_guests))
            print("Seats used:", len(table_guests), "/", capacity)



#######################
# BACKTRACKING
#######################

# Run Backtracking if the user selected it
if algorithm == "backtracking" or algorithm == "compare":

    print("\n================================")
    print("BACKTRACKING")
    print("================================")

   # Start the timer
    start = time.perf_counter()

    # Run Backtracking
    assignment, attempts, timed_out = backtracking_search(
        guests, tables, capacity, together, apart, fixed
    )

    # Calculate the execution time
    elapsed = time.perf_counter() - start

    print("Assignments tried:", attempts)
    print("Execution time:", round(elapsed, 6), "seconds")

    # Check why the search stopped
    if timed_out:
       print("Time limit reached (10 seconds).")

    # Check if Backtracking found a solution
    elif assignment is None:
        print("No valid assignment found.")

    else:
        # Check the final assignment
        valid = len(assignment) == len(guests) and is_valid(
            assignment, capacity, together, apart, fixed
        )
        print("Valid assignment:", valid)

        # Count the satisfied preferences
        score = count_preferences(assignment, preferences)
        print("Preferences satisfied:", score, "/", len(preferences))

        # Show the guests at each table
        print("\nSEATING ARRANGEMENT")

        for table in tables:
            table_guests = []

            for guest in guests:
                if assignment[guest] == table:
                    table_guests.append(guest)

            print("Table", table, ":", ", ".join(table_guests))
            print("Seats used:", len(table_guests), "/", capacity)

import time

from scenarios import generate_scenario
from constraints import is_valid, count_preferences
from greedy import greedy_first_fit, greedy_optimize
from backtracking import backtracking_search
from mrv_fc import mrv_fc_search

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
if num_guests is None:
    exit()

print("Number of guests:", num_guests)


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
if constraint_level is None:
    exit()

print("Constraint level:", constraint_level)


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
if algorithm is None:
    exit()

print("Selected algorithm:", algorithm)

###############################
# SEARCH MODE
###############################

# Choose how the algorithms should search
print("\n================================")
print("SEARCH MODE")
print("================================")
print("1. Find First Valid Solution")
print("2. Optimize Preferences")

mode_choice = input("Choose the search mode: ")

# Save the selected search mode
if mode_choice == "1":
    search_mode = "first_valid"

elif mode_choice == "2":
    search_mode = "optimize"

else:
    search_mode = None
    print("Invalid option")

# Check the selected search mode
if search_mode is None:
    exit()

print("Selected search mode:", search_mode)


###############################
# GENERATE THE SCENARIO
###############################

# Let the user choose a random seed
seed_choice = input("Choose a random seed (press Enter for 42): ")

# Use 42 as the default seed
if seed_choice == "":
    seed = 42

elif seed_choice.isdigit():
    seed = int(seed_choice)

else:
    print("Invalid seed")
    exit()

# Generate the scenario using our shared function
scenario = generate_scenario(num_guests, constraint_level, seed)

# Get the scenario information from the dictionary
guests = scenario["guests"]
num_tables = scenario["num_tables"]
tables = scenario["tables"]
capacity = scenario["capacity"]

# Get the hard constraints
together = scenario["together"]
apart = scenario["apart"]
fixed = scenario["fixed"]

# Get the soft preferences
preferences = scenario["preferences"]


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
print("Random seed:", seed)
print("Search mode:", search_mode)

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

    if search_mode == "first_valid":
        print("GREEDY FIRST-FIT")
    else:
        print("GREEDY OPTIMIZE (RANDOM RESTARTS)")

    print("================================")

    # Start the timer
    start = time.perf_counter()

    # Run Greedy with the selected search mode
    if search_mode == "first_valid":

        assignment, attempts = greedy_first_fit(
            guests, tables, capacity, together, apart, fixed
        )

    else:

        assignment, attempts, restarts, timed_out = greedy_optimize(
            guests, tables, capacity, together, apart, fixed,
            preferences, time_limit=10, seed=seed
        )

    
    # Calculate the execution time
    elapsed = time.perf_counter() - start

    # Save the results for the comparison table
    greedy_attempts = attempts
    greedy_time = elapsed

    # Check if Greedy found a solution
    if assignment is None:

        if search_mode == "optimize" and timed_out:
            greedy_status = "Timeout"
        else:
            greedy_status = "Failed"

        greedy_preferences = "-"

    else:

        # We found a solution, even if the time limit was reached
        if search_mode == "optimize" and timed_out:
            greedy_status = "Solved (limit)"
        else:
            greedy_status = "Solved"

        # Count the satisfied preferences
        score = count_preferences(assignment, preferences)
        greedy_preferences = str(score) + "/" + str(len(preferences))

    # Show the search results
    print("Assignments tried:", attempts)

    # Show the number of seating plans started
    if search_mode == "optimize":
        print("Seating plans started:", restarts)

    print("Execution time:", round(elapsed, 6), "seconds")
    print("Result:", greedy_status)

    # Show a message if we reached the time limit
    if search_mode == "optimize" and timed_out:
        print("Time limit reached (10 seconds).")

    # Show the final seating plan
    if assignment is None:
        print("No valid assignment found.")

    else:

        # Check that all guests have a table and follow the rules
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

    if search_mode == "first_valid":
        print("BACKTRACKING - FIRST VALID")
    else:
        print("BACKTRACKING - OPTIMIZE PREFERENCES")

    print("================================")

   # Start the timer
    start = time.perf_counter()

    # Run Backtracking with the selected search mode
    assignment, attempts, timed_out = backtracking_search(
        guests, tables, capacity, together, apart, fixed,
        search_mode=search_mode, preferences=preferences
    )

    # Calculate the execution time
    elapsed = time.perf_counter() - start

    # We have to save the result for the comparison
    backtracking_attempts = attempts
    backtracking_time = elapsed

    # Check if we found a solution
    if assignment is None:

        if timed_out:
            backtracking_status = "Timeout"

        else:
            backtracking_status = "No solution"

        backtracking_preferences = "-"

    else:   

        # We found a valid solution, even if we reached the time limit
        if timed_out:
            backtracking_status = "Solved (limit)"

        else:
            backtracking_status = "Solved"

        # Count how many preferences we satisfied
        score = count_preferences(assignment, preferences)
        backtracking_preferences = str(score) + "/" + str(len(preferences))

    print("Assignments tried:", attempts)
    print("Execution time:", round(elapsed, 6), "seconds")

    # Show a message if the time limit was reached
    if timed_out:
        print("Time limit reached (10 seconds).")

    # Check if Backtracking found a solution
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
# MRV + FORWARD CHECKING
#######################

# Run MRV + FC if selected, or if we want to compare
if algorithm == "mrv_fc" or algorithm == "compare":

    print("\n================================")

    if search_mode == "first_valid":
        print("MRV + FC - FIRST VALID")
    else:
        print("MRV + FC - OPTIMIZE PREFERENCES")

    print("================================")

    # Start the timer
    start = time.perf_counter()

    # Run MRV + FC with the selected search mode
    assignment, attempts, timed_out = mrv_fc_search(
        guests, tables, capacity, together, apart, fixed,
        search_mode=search_mode, preferences=preferences
    )

    # Calculate how long it took
    elapsed = time.perf_counter() - start

    # Save the results for Compare All
    mrv_attempts = attempts
    mrv_time = elapsed

    # Check if we found a solution
    if assignment is None:

        # Check if we ran out of time
        if timed_out:
            mrv_status = "Timeout"
        else:
            mrv_status = "No solution"

        mrv_preferences = "-"

    else:

        # We found a solution, even if we reached the time limit
        if timed_out:
            mrv_status = "Solved (limit)"
        else:
            mrv_status = "Solved"

        # Count how many preferences we satisfied
        score = count_preferences(assignment, preferences)
        mrv_preferences = str(score) + "/" + str(len(preferences))

    # Show the search results
    print("Assignments tried:", attempts)
    print("Execution time:", round(elapsed, 6), "seconds")
    print("Result:", mrv_status)

    # Show a message if we reached the time limit
    if timed_out:
        print("Time limit reached (10 seconds).")

    # Check if MRV + FC found a solution
    if assignment is None:
        print("No valid assignment found.")

    else:

        # Check if all guests have a table and the rules are followed
        valid = len(assignment) == len(guests) and is_valid(
            assignment, capacity, together, apart, fixed
        )

        print("Valid assignment:", valid)

        # Show how many preferences we satisfied
        score = count_preferences(assignment, preferences)
        print("Preferences satisfied:", score, "/", len(preferences))

        # Show who is sitting at each table
        print("\nSEATING ARRANGEMENT")

        for table in tables:
            table_guests = []

            for guest in guests:
                if assignment[guest] == table:
                    table_guests.append(guest)

            print("Table", table, ":", ", ".join(table_guests))
            print("Seats used:", len(table_guests), "/", capacity)




#######################
# ALGORITHM COMPARISON
#######################

# Only show this table if we selected Compare All
if algorithm == "compare":

    # Print the title
    print("\n================================================================================")
    print("ALGORITHM COMPARISON")
    print("================================================================================")

    # Show which scenario we are comparing
    print("Guests:", num_guests, "| Constraint level:", constraint_level)
    print("Search mode:", search_mode)
    print()

    # We leave enough space for each column
    # 23 is for the metric names, like "Assignments tried"
    # 17 is for Greedy and 18 is for Backtracking
    # The < means the text is aligned to the left
    # We chose these numbers so the columns do not overlap
    print(f"{'Metric':<23}{'Greedy':<17}{'Backtracking':<18}{'MRV + FC'}")
    print("-" * 80)

    # Check which algorithms found a solution
    print(f"{'Result':<23}{greedy_status:<17}{backtracking_status:<18}{mrv_status}")

    # Compare how many assignments each algorithm tried
    print(f"{'Assignments tried':<23}{greedy_attempts:<17}{backtracking_attempts:<18}{mrv_attempts}")

    # Show how long each algorithm took
    # .6f means 6 decimal places, for example 0.003123
    # This helps us see the difference when algorithms are very fast
    print(f"{'Execution time (s)':<23}{greedy_time:<17.6f}{backtracking_time:<18.6f}{mrv_time:.6f}")

    # Compare how many preferences each algorithm satisfied
    # For example, 2/4 means 2 out of 4 preferences
    print(f"{'Preferences':<23}{greedy_preferences:<17}{backtracking_preferences:<18}{mrv_preferences}")

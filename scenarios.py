import random

###############################
# SCENARIO GENERATION
###############################

def generate_scenario(num_guests, level, seed=42):

    # Create the list of guests
    guests = []

    for i in range(1, num_guests + 1):
        guests.append("Guest" + str(i))

    # Set the maximum capacity of each table
    capacity = 8

    # Set the number of tables depending on the event size
    if num_guests == 6 or num_guests == 12:
        num_tables = 2

    elif num_guests == 24:
        num_tables = 3

    else:
        num_tables = 5

    # Create the list of available tables
    tables = list(range(1, num_tables + 1))

    # Convert the constraint level to lowercase
    level = level.lower()

    # Set the number of hard constraints
    if level == "low":
        num_constraints = num_guests // 6

    elif level == "medium":
        num_constraints = num_guests // 3

    elif level == "high":
        num_constraints = num_guests // 2

    else:
        raise ValueError("Invalid constraint level")

    # Split the hard constraints into three types
    num_together = num_constraints // 3
    num_apart = num_constraints // 3
    num_fixed = num_constraints - num_together - num_apart

    # Create a reference seating plan for generating valid scenarios
    reference_assignment = {}
    table = 1

    # Assign guests to tables one by one
    for guest in guests:
        reference_assignment[guest] = table

        # Move to the next table
        table += 1

        # Go back to the first table
        if table > len(tables):
            table = 1

    # Use a random seed to generate reproducible scenarios
    rng = random.Random(seed)

    #######################
    # TOGETHER CONSTRAINTS
    #######################

    # Store the together constraints
    together = []

    # Keep adding pairs until we reach the required number
    while len(together) < num_together:

        # Choose a random table
        selected_table = rng.choice(tables)

        # Find the guests at that table
        table_guests = []

        for guest in guests:
            if reference_assignment[guest] == selected_table:
                table_guests.append(guest)

        # Choose two guests from the same table
        guest1, guest2 = rng.sample(table_guests, 2)

        # Make sure we do not add the same pair twice
        if (guest1, guest2) not in together and (guest2, guest1) not in together:
            together.append((guest1, guest2))

    #######################
    # APART CONSTRAINTS
    #######################

    # Store the apart constraints
    apart = []

    # Keep adding pairs until we reach the required number
    while len(apart) < num_apart:

        # Choose the first guest randomly
        guest1 = rng.choice(guests)

        # Find guests who are at a different table
        different_table_guests = []

        for guest in guests:
            if reference_assignment[guest] != reference_assignment[guest1]:
                different_table_guests.append(guest)

        # Choose the second guest randomly
        guest2 = rng.choice(different_table_guests)

        # Avoid adding the same pair twice
        if (guest1, guest2) not in apart and (guest2, guest1) not in apart:
            apart.append((guest1, guest2))

    #######################
    # FIXED CONSTRAINTS
    #######################

    # Store the fixed constraints
    fixed = {}

    # Keep adding guests until we have enough fixed constraints
    while len(fixed) < num_fixed:

        # Choose a random guest
        guest = rng.choice(guests)

        # Get the guest's table from the reference assignment
        table = reference_assignment[guest]

        # Avoid choosing the same guest twice
        if guest not in fixed:
            fixed[guest] = table

    #######################
    # SOFT PREFERENCES
    #######################

    # We use one preference for every 6 guests
    # Each satisfied preference gives 1 point
    num_preferences = num_guests // 6

    # Store the guest preferences
    preferences = []

    # Keep adding preferences until we have enough
    while len(preferences) < num_preferences:

        # Choose two random guests
        guest1, guest2 = rng.sample(guests, 2)

        # Check both orders of the pair
        pair = (guest1, guest2)
        reverse_pair = (guest2, guest1)

        # Avoid duplicates and pairs already used in hard constraints
        if (pair not in preferences and reverse_pair not in preferences
                and pair not in together and reverse_pair not in together
                and pair not in apart and reverse_pair not in apart):

            preferences.append(pair)

    #######################
    # RETURN THE SCENARIO
    #######################

    # Return all the information needed by the algorithms
    # Both main.py and app.py will use this dictionary
    return {
        "guests": guests,
        "num_tables": num_tables,
        "tables": tables,
        "capacity": capacity,
        "together": together,
        "apart": apart,
        "fixed": fixed,
        "preferences": preferences
    }

#######################
# TEST THE GENERATOR
#######################

if __name__ == "__main__":

    # Generate a test scenario
    scenario = generate_scenario(24, "high", 42)

    # Print the scenario details
    print("Guests:", scenario["guests"])
    print("Number of tables:", scenario["num_tables"])
    print("Tables:", scenario["tables"])
    print("Capacity:", scenario["capacity"])

    print("\nHARD CONSTRAINTS")
    print("Together:", scenario["together"])
    print("Apart:", scenario["apart"])
    print("Fixed:", scenario["fixed"])

    print("\nSOFT PREFERENCES")
    print("Preferences:", scenario["preferences"])
def what_is_the_range(age):

    def get_age_range(age):
        # Given age ranges
        rangesOfAges = ['19-25', '26-35', '35-50', '50-70']

        try:
            # Convert the age to an integer (assuming it's a valid integer)
            age = int(age)
        except ValueError:
            return None  # Return None if the input age is not a valid integer

        # Check each range to find the appropriate one
        for age_range in rangesOfAges:
            # Split the age range into lower and upper bounds
            age_bounds = age_range.split('-')

            if len(age_bounds) == 2:
                lower, upper = map(int, age_bounds)

                # Check if the age falls within the current range
                if lower <= age <= upper:
                    return age_range

        # If the age doesn't fit into any range, return None or any other desired value
        return None


    age_range = get_age_range(age)
    return age_range

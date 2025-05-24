def print_number_pyramid(height):
    """
    Prints a pyramid pattern of numbers where each row contains
    the row number repeated that many times, with proper spacing.
    
    Args:
        height: The height of the pyramid (number of rows)
    """
    for i in range(1, height + 1):
        # Print leading spaces
        spaces = " " * (height - i)
        # Print the number repeated i times
        numbers = str(i) * i
        # Print the complete row
        print(spaces + numbers)

# Example usage
height = 5
print_number_pyramid(height)

# Bonus: Inverted pyramid
print("\nInverted pyramid:")
def print_inverted_pyramid(height):
    for i in range(height, 0, -1):
        spaces = " " * (height - i)
        numbers = str(i) * i
        print(spaces + numbers)

print_inverted_pyramid(height) 
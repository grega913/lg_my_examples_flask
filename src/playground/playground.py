import time
from icecream import ic


def square_numbers():
    for i in range(1, 15):
        time.sleep(0.5)
        yield i ** 2




if __name__ == "__main__":
    # Create an iterator from the generator function
    squares = square_numbers()

    # Print the squares
    for square in squares:
        ic(square)
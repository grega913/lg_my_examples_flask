import time
from icecream import ic
import random
import string


def square_numbers():
    for i in range(1, 15):
        time.sleep(0.5)
        yield i ** 2

def generate_random_string(length):
    letters_and_digits = string.ascii_letters + string.digits
    result_str = ''.join(random.choice(letters_and_digits) for i in range(length))
    return result_str


def get_summaryFromSnapshot(snapshot):
    if "summary" in snapshot.values:
        return snapshot.values["summary"]
    else:
        return None


def get_messagesFromSnapshot(snapshot):
    if "messages" in snapshot.values:
        return snapshot.values["summary"]
    else:
        return None

if __name__ == "__main__":
    # Create an iterator from the generator function
    squares = square_numbers()

    # Print the squares
    for square in squares:
        ic(square)
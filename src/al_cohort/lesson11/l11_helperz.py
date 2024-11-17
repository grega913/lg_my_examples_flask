import random
from typing import Literal
from IPython.display import display, Image
from langgraph.graph import StateGraph, START, END, MessagesState
from typing_extensions import TypedDict

class State(TypedDict):
    my_state: str

#state as the list of messages


def multiply_numbers(a: int, b: int) -> int:
    """
    Multiply two numbers.
    Args:
        a: int
        b: int
    """
    return a * b



    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}

def node_1(state: State) -> State:
    print("node_1")
    print(state)
    new_state = state["my_state"] + "I want to travel to "
    return { "my_state": new_state}

def node_2(state: State) -> State:
    print("node_2")
    print(state)
    new_state = state["my_state"] + "Japan"
    return { "my_state": new_state}

def node_3(state: State) -> State:
    print("node_3")
    print(state)
    new_state = state["my_state"] + "Italy"
    return { "my_state": new_state}

# define a new node - conditional node
def decide_node(state:State) -> Literal["node_2", "node_3"]:  # the return value of decision function is either "node_2" or "node_3". So we need to return a Literal
    print("decide_node")
    print(state)
    return random.choice(["node_2", "node_3"])

# define our tools
def get_temperature(city: str) -> str:
    """
    Get the temperature of a city in Celsius.
    Args:
        city: str
    """
    if city.lower() == "new york":
        return 21.5
    if city.lower() == "tokyo":
        return 26.3
    if city.lower() == "san francisco":
        return 18.2
    return 0.0

def convert_to_fahrenheit(celcius: float) -> float:
    """
    Convert a temperature in Celsius to Fahrenheit.
    Args:
        celcius: The temperature in Celsius.
    """
    return (celcius * 9/5) + 32
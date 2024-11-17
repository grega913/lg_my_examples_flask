from icecream import ic
import time
import re

from al_cohort.lesson10.l10_helperz import system_prompt, get_planet_mass, calculate

# region ReAct Agents expleined

# https://app.alejandro-ao.com/lessons/introduction-to-agents/
'''
The ReAct pattern
thought -> (choose tool) -> action (output) -> observation

Initial prompt
should know when to use available tools.

'''
# endRegion

import os
from groq import Groq

client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": "Explain the importance of fast language models",
        }
    ],
    model="llama3-70b-8192",
)

# ic(chat_completion.choices[0].message.content)


class Agent:
    def __init__(self, client, system):
        self.client = client
        self.system = system
        self.messages = []
        if self.system is not None:
            self.messages.append({"role": "system", "content": self.system})

    # when we call our agent, message has to be optional
    def __call__(self, message=""):
        if message:
            self.messages.append({"role": "user", "content": message})
        result = self.execute()
        self.messages.append({"role": "assistant", "content": result})
        return result

    def execute(self):
        completion = client.chat.completions.create(
            messages=self.messages,
            model="llama3-70b-8192",
        )
        return completion.choices[0].message.content

def agent_loop(max_iterations, system, query):
    agent = Agent(client=client, system=system_prompt)          # initializing Agent
    tools = ['calculate', 'get_planet_mass']                    # initializing tools
    next_prompt = query
    i = 0
    while i < max_iterations:
        i += 1
        print(f"Iteration {i}")
        result = agent(next_prompt)
        print(result)

        if "PAUSE" in result and "Action" in result:
            action = re.findall(r"Action: ([a-z_]+): (.+)", result, re.IGNORECASE)
            chosen_tool = action[0][0]
            arg = action[0][1]

            if chosen_tool in tools:                            # if the tool selected is in our tools  . . .
                result_tool = eval(f"{chosen_tool}('{arg}')")     # we are running this tool
                next_prompt = f"Observation: {result_tool}"
                print(next_prompt)
                #result = agent(next_prompt)
                print(result)

            else:
                next_prompt = "Observation: Tool not found"

            print(f"next_prompt: {next_prompt}")
            continue
        if "Answer" in result:
            break




if __name__ == "__main__":
    ic("name = main")

    neil_tyson = Agent(client=client, system=system_prompt)
    result = neil_tyson(message = "What is the mass of the Earth times 5?")

    messages = neil_tyson.messages
    for message in messages:
        print(message)

    print(" - - - - - - - - - - - - - - - - - - - - - - - - -")
    time.sleep(4)
    # now we want to rerun
    result = neil_tyson()
    print(result)

    messages = neil_tyson.messages
    for message in messages:
        print(message)

    print(" - - - - - - - - - - - - - - - - - - - - - - - - -")
    observation = get_planet_mass("Earth")
    print(observation)

    print(" - - - - - - - - - - - - - - - - - - - - - - - - -")
    next_prompt = f"Observation: {observation}"
    result = neil_tyson(next_prompt)
    print(result)

    print(" - - - - - - - - - - - - - - - - - - - - - - - - -")
    messages = neil_tyson.messages
    for message in messages:
        print(message)
    
    print(" - - - - - - - - - - - - - - - - - - - - - - - - -")
    result = neil_tyson()
    print(result)

    


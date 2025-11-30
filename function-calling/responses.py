from openai import OpenAI
from dotenv import load_dotenv
import json

from prompt_toolkit import prompt

load_dotenv()

client = OpenAI()

# -----------------------------------------------------------------------------------------------------------
# Basic chat completion request without function calling
# -----------------------------------------------------------------------------------------------------------
response = client.chat.completions.create(
  model="gpt-4o-mini",
  messages=[
   {"role": "user", "content": "What's the next flight from Buffalo, NY to New York City, NY?"}
  ]
)

print(response.choices[0].message.content)
# -----------------------------------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------------------------------
# Define the function
# -----------------------------------------------------------------------------------------------------------
tools = [
  {
    "type": "function",
    "name": "get_flight_info",
    "description": "Get the next flight information from a departure city to an arrival city.",
    "parameters": {
      "type": "object",
      "properties": {
        "origin": {
          "type": "string",
          "description": "The city from which the flight departs."
        },
        "destination": {
          "type": "string",
          "description": "The city to which the flight arrives."
        }
      },
      "required": ["origin", "destination"]
    }
  }
]
# -----------------------------------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------------------------------
# Using the function in the chat completion request
# -----------------------------------------------------------------------------------------------------------
input_list = [
    {
        "role": "user",
        "content": "What's the next flight from Buffalo, NY to New York City, NY?"
    }
]

print(input_list)

response = client.responses.create(
  model="gpt-4o-mini",
  tools=tools,
  tool_choice="auto",
  input=input_list,
)

input_list += response.output

print(response)
print(input_list)
# -----------------------------------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------------------------------
# Using the function in the chat completion request
# -----------------------------------------------------------------------------------------------------------
def get_flight_info(origin: str, destination: str) -> str:
    flight_info = {
      "flight_number": "AA123",
      "departure_time": "2024-06-15T09:00:00",
      "arrival_time": "2024-06-15T10:15:00",
      "origin": origin,
      "destination": destination
    }

    return json.dumps(flight_info)

origin = json.loads(response.output[0].arguments).get("origin")
destination = json.loads(response.output[0].arguments).get("destination")
params = json.loads(response.output[0].arguments)

type(params)
print(origin)
print(destination)
print(params)
# -----------------------------------------------------------------------------------------------------------


# -----------------------------------------------------------------------------------------------------------
# Using the function in the chat completion request
# -----------------------------------------------------------------------------------------------------------
flight_info = get_flight_info(origin, destination)

input_list += [
    {
        "type": "function_call_output",
        "call_id": response.output[0].call_id,
        "output": flight_info
    }
]

response = client.responses.create(
  model="gpt-4o-mini",
  instructions="Provide the flight information based on the function call output.",
  tools=tools,
  input=input_list
)

print(input_list)

print(response.output_text)
# -----------------------------------------------------------------------------------------------------------

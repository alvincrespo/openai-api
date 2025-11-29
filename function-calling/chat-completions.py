from openai import OpenAI
from dotenv import load_dotenv
import json

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
    "function": {
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
  }
]
# -----------------------------------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------------------------------
# Using the function in the chat completion request
# -----------------------------------------------------------------------------------------------------------
prompt = "What's the next flight from Buffalo, NY to New York City, NY?"

completion = client.chat.completions.create(
  model="gpt-4o-mini",
  messages=[
    {"role": "user", "content": prompt}
  ],
  tools=tools,
  tool_choice="auto"
)

output = completion.choices[0].message

print(output)
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

origin = json.loads(output.tool_calls[0].function.arguments).get("origin")
destination = json.loads(output.tool_calls[0].function.arguments).get("destination")
params = json.loads(output.tool_calls[0].function.arguments)

type(params)
print(origin)
print(destination)
print(params)
# -----------------------------------------------------------------------------------------------------------


# -----------------------------------------------------------------------------------------------------------
# Using the function in the chat completion request
# -----------------------------------------------------------------------------------------------------------
second_response = client.chat.completions.create(
  model="gpt-4o-mini",
  messages=[
    {"role": "user", "content": prompt},
    {"role": "assistant", "tool_calls": output.tool_calls},
    {"role": "tool", "tool_call_id": output.tool_calls[0].id, "name": output.tool_calls[0].function.name, "content": get_flight_info(origin, destination)}
  ]
)

print(second_response.choices[0].message.content)
# -----------------------------------------------------------------------------------------------------------

from openai import OpenAI
from dotenv import load_dotenv
import json

from prompt_toolkit import prompt

load_dotenv()

client = OpenAI()

# -----------------------------------------------------------------------------------------------------------
# Function Implementations
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

def book_flight(origin: str, destination: str, datetime: str, airline: str) -> str:
    booking_confirmation = {
      "confirmation_number": "XYZ789",
      "origin": origin,
      "destination": destination,
      "datetime": datetime,
      "airline": airline
    }

    return json.dumps(booking_confirmation)
# -----------------------------------------------------------------------------------------------------------

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
  },
  {
      "type": "function",
      "name": "book_flight",
      "description": "Book a flight from a departure city to an arrival city.",
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
              },
              "datetime": {
                  "type": "string",
                  "description": "The date and time of the flight."
              },
              "airline": {
                  "type": "string",
                  "description": "The airline to book the flight with."
              }
          },
          "required": ["origin", "destination", "datetime", "airline"]
      }
  }
]
# -----------------------------------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------------------------------
# User Flows
# -----------------------------------------------------------------------------------------------------------
prompt = "What's the next flight from Buffalo, NY to New York City, NY?"
input_list = [
    {
        "role": "user",
        "content": prompt
    }
]

print(f"User asks: {prompt}")

# Step 1: User requests flight information
response = client.responses.create(
  model="gpt-4o-mini",
  tools=tools,
  tool_choice="auto",
  input=input_list,
)

input_list += response.output

flight_info_params = json.loads(response.output[0].arguments)
origin = flight_info_params.get("origin")
destination = flight_info_params.get("destination")
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

print(response.output_text)

prompt = "Book this flight for me with Delta Airlines on January 15, 2026 at 09:00 AM."
input_list += [
    {
        "role": "user",
        "content": prompt
    }
]

print(f"User asks: {prompt}")

response = client.responses.create(
  model="gpt-4o-mini",
  tools=tools,
  tool_choice="auto",
  input=input_list,
)

input_list += response.output

booking_params = json.loads(response.output[0].arguments)
origin = booking_params.get("origin")
destination = booking_params.get("destination")
datetime = booking_params.get("datetime")
airline = booking_params.get("airline")

booking_info = book_flight(origin, destination, datetime, airline)

input_list += [
    {
        "type": "function_call_output",
        "call_id": response.output[0].call_id,
        "output": booking_info
    }
]
response = client.responses.create(
  model="gpt-4o-mini",
  instructions="Provide the booking information based on the function call output.",
  tools=tools,
  input=input_list
)

print(response.output_text)

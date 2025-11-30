from openai import OpenAI
from dotenv import load_dotenv
import json

load_dotenv()

client = OpenAI()

# -----------------------------------------------------------------------------------------------------------
# Function Implementations
# -----------------------------------------------------------------------------------------------------------
def get_flight_info(origin: str, destination: str) -> str:
    """Simulates getting flight info - in reality would hit an API"""
    flight_info = {
        "flight_number": f"AA{hash((origin, destination)) % 1000}",
        "departure_time": "2024-06-15T09:00:00",
        "arrival_time": "2024-06-15T10:15:00",
        "origin": origin,
        "destination": destination,
        "price": 299.99
    }
    return json.dumps(flight_info)

def get_weather(city: str) -> str:
    """Simulates getting weather info"""
    weather_info = {
        "city": city,
        "temperature": 72,
        "conditions": "Partly cloudy",
        "humidity": 45
    }
    return json.dumps(weather_info)

def get_hotel_info(city: str, checkin_date: str) -> str:
    """Simulates getting hotel info"""
    hotel_info = {
        "city": city,
        "hotel_name": "Grand Plaza Hotel",
        "checkin_date": checkin_date,
        "price_per_night": 189.00,
        "availability": True
    }
    return json.dumps(hotel_info)

# -----------------------------------------------------------------------------------------------------------
# Tool Definitions
# -----------------------------------------------------------------------------------------------------------
tools = [
    {
        "type": "function",
        "name": "get_flight_info",
        "description": "Get flight information from a departure city to an arrival city.",
        "parameters": {
            "type": "object",
            "properties": {
                "origin": {"type": "string", "description": "Departure city"},
                "destination": {"type": "string", "description": "Arrival city"}
            },
            "required": ["origin", "destination"]
        }
    },
    {
        "type": "function",
        "name": "get_weather",
        "description": "Get current weather for a city.",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "City name"}
            },
            "required": ["city"]
        }
    },
    {
        "type": "function",
        "name": "get_hotel_info",
        "description": "Get hotel availability and pricing for a city.",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "City name"},
                "checkin_date": {"type": "string", "description": "Check-in date (YYYY-MM-DD)"}
            },
            "required": ["city", "checkin_date"]
        }
    }
]

# -----------------------------------------------------------------------------------------------------------
# Function dispatcher
# -----------------------------------------------------------------------------------------------------------
def execute_function(name: str, arguments: dict):
    """Routes function calls to their implementations"""
    if name == "get_flight_info":
        return get_flight_info(arguments["origin"], arguments["destination"])
    elif name == "get_weather":
        return get_weather(arguments["city"])
    elif name == "get_hotel_info":
        return get_hotel_info(arguments["city"], arguments["checkin_date"])
    else:
        return json.dumps({"error": f"Unknown function: {name}"})

# -----------------------------------------------------------------------------------------------------------
# Parallel Function Calling Example
# -----------------------------------------------------------------------------------------------------------
def run_parallel_example():
    # This prompt naturally triggers multiple function calls
    user_prompt = """I'm planning a trip from Boston to Miami on June 15th, 2024.
    Can you get me the flight info, weather in Miami, and hotel availability?"""

    input_list = [{"role": "user", "content": user_prompt}]

    print(f"User: {user_prompt}\n")
    print("-" * 60)

    # Step 1: Initial request - model should request multiple functions in parallel
    response = client.responses.create(
        model="gpt-4o-mini",
        tools=tools,
        tool_choice="auto",
        input=input_list,
    )

    # Add the model's response (containing tool calls) to the conversation
    input_list += response.output

    # Step 2: Process ALL tool calls from the response
    tool_calls = [item for item in response.output if item.type == "function_call"]

    print(f"Model requested {len(tool_calls)} parallel function calls:\n")

    # Execute each function and collect results
    for tool_call in tool_calls:
        function_name = tool_call.name
        arguments = json.loads(tool_call.arguments)

        print(f"  → {function_name}({arguments})")

        # Execute the function
        result = execute_function(function_name, arguments)

        # Add each result to the conversation
        input_list.append({
            "type": "function_call_output",
            "call_id": tool_call.call_id,
            "output": result
        })

    print("\n" + "-" * 60)

    # Step 3: Get the final response with all function results
    final_response = client.responses.create(
        model="gpt-4o-mini",
        instructions="Summarize the travel information based on the function call outputs.",
        tools=tools,
        input=input_list
    )

    print(f"\nAssistant: {final_response.output_text}")

if __name__ == "__main__":
    run_parallel_example()

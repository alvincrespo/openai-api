from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()

response = client.chat.completions.create(
  model="gpt-4o-mini",
  messages=[
   {"role": "user", "content": "I have these notes with book titles and authors: New releases this week! The Beholders by Hester Musson, The Mystery Guest by Nita Prose. Please organize the titles and authors in a json file."}
  ],
  response_format={"type": "json_object"}
)

print(response.choices[0].message.content)

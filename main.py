from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import textwrap
import google.generativeai as genai
from IPython.display import Markdown
import os 
import re
import json

app = FastAPI()

prompt = """
You are a backend API that responds to the user query by adding this prompt to the user query now you will return the schedule for the user in the below format based on the user's query and you will use only the 12-hour format in AM and PM . The below example is just for structural reference.
 {
time: [XX AM to XX AM,
XX PM to XX PM,
XX PM to XX PM, etc]

task: [Task 1,
Task 2,
Task 3, etc]
}.
Do not do below mentioned things:
1-Do not ask for any more information
2- Do not give incomplete output
3- Strictly Do not include /n and \ in the output just seprate them by comma also add at least 6 tasks.
3 - If a user sends some unrelated query that is not related to the task scheduling kindly reply with the message "NULL" Now the user query goes here.

"""

class Query(BaseModel):
    question: str

def to_markdown(text):
    text = text.replace('•', '  *')
    return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))

GOOGLE_API_KEY=os.getenv('GOOGLE_API_KEY')
Key = "AIzaSyA6cT3ZpL2WM0vxVct5CC6a8Ok6GeWnpy0"
genai.configure(api_key=Key)

def get_gemini_response(question: str):
    model = genai.GenerativeModel("gemini-pro")
    instruction = prompt + question
    response = model.generate_content(instruction)

    # Get the text content from the response
    response_text = response.text

    # Remove the outer double quotes
    response_text = response_text.strip('"')

    # Enclose property names with double quotes
    response_text = re.sub(r'(\w+)\s*:\s*', r'"\1": ', response_text)

    # Parse the JSON string
    json_data = json.loads(response_text)

    return json_data

@app.post("/generate-schedule/")
async def generate_schedule(query: Query):
    try:
        answer = get_gemini_response(query.question)
        return {"schedule": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
from fastapi import FastAPI
from pydantic import BaseModel
import os
from groq import Groq

app = FastAPI()

# It is recommended to set your Groq API key as an environment variable
# for better security and configuration management.
# You can do this by running `export GROQ_API_KEY=your_api_key` in your terminal.
client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

class Message(BaseModel):
    message: str

@app.post("/chat")
async def chat(message: Message):
    """
    This endpoint receives a message from the user, sends it to the Groq API,
    and returns the chatbot's response.
    """
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": message.message,
            }
        ],
        model="llama3-8b-8192",
    )
    return {"response": chat_completion.choices[0].message.content}

if __name__ == "__main__":
    import uvicorn
    # To run this application, you would use the following command in your terminal:
    # uvicorn main:app --reload
    # Ensure you have a .env file with your GROQ_API_KEY or have it set as an environment variable.
    uvicorn.run(app, host="0.0.0.0", port=8000)

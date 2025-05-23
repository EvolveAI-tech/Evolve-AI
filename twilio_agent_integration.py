import os
from fastapi import FastAPI, Request, Form
from fastapi.responses import Response
from twilio.twiml.voice_response import VoiceResponse, Say
from agent import run_agent  # Your AI agent function
import logging

app = FastAPI()
logger = logging.getLogger(__name__)

@app.post("/voice")
async def voice(request: Request,
                From: str = Form(...),  # Caller phone number
                To: str = Form(...),    # Your Twilio number
                Body: str = Form(default=None)):  # Text body if SMS (optional)
    """
    Handle incoming call webhook from Twilio.
    """

    # For demonstration, let's create a prompt for the AI agent.
    # You can customize this based on the caller or context.
    prompt = (
        "You are a friendly and professional hotel receptionist AI. "
        "Answer the caller's questions politely and clearly."
        "\nCaller phone number: " + From + "\n"
        "Please greet the caller and ask how you can help."
    )

    # Run your AI agent to generate a response
    try:
        ai_response = run_agent(prompt)
        logger.info(f"AI response: {ai_response}")
    except Exception as e:
        logger.error(f"AI agent error: {e}")
        ai_response = "Sorry, I am experiencing technical difficulties. Please try again later."

    # Create TwiML voice response
    response = VoiceResponse()
    response.say(ai_response, voice="alice", language="en-US")

    return Response(content=str(response), media_type="application/xml")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

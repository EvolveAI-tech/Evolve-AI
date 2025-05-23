from dotenv import load_dotenv
import os
import logging
import asyncio

from fastapi import FastAPI, Request, HTTPException, Form
from fastapi.responses import PlainTextResponse
from twilio.twiml.voice_response import VoiceResponse
from agent import run_agent

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY is missing in environment variables")

app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.post("/ask")
async def ask_agent(request: Request):
    try:
        data = await request.json()
        prompt = data.get("prompt")
        if not prompt:
            raise HTTPException(status_code=400, detail="Prompt is required")

        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, run_agent, prompt)
        return {"response": response}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in /ask endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/voice")
async def voice(request: Request):
    form = await request.form()
    caller_input = form.get("SpeechResult") or "Hello"
    session_id = form.get("From", "default")  # use caller number as session ID

    try:
        loop = asyncio.get_event_loop()
        ai_response = await loop.run_in_executor(None, run_agent, caller_input, session_id)
    except Exception as e:
        logger.error(f"Error in /voice endpoint: {e}")
        ai_response = "I'm sorry, something went wrong. Please try again later."

    twiml = VoiceResponse()
    twiml.say(ai_response, voice='Polly.Joanna', language='en-CA')
    return PlainTextResponse(str(twiml), media_type="application/xml")

from fastapi import FastAPI, Request
from twilio.twiml.voice_response import VoiceResponse, Gather
from fastapi.responses import Response
import logging
from agent import run_agent

app = FastAPI()
logger = logging.getLogger(__name__)

@app.post("/voice")
async def voice_handler(request: Request):
    form = await request.form()
    user_speech = form.get("SpeechResult", "").strip()

    response = VoiceResponse()

    if not user_speech:
        # Ask caller to say something if no speech detected
        gather = Gather(input="speech", timeout=3, speechTimeout="auto", action="/voice", method="POST")
        gather.say("Hello, this is Elisa, your AI hotel receptionist. Please tell me how I can assist you.")
        response.append(gather)
    else:
        logger.info(f"User said: {user_speech}")

        # Run AI agent with user speech
        ai_reply = run_agent(user_speech)

        # Respond with AI-generated reply
        gather = Gather(input="speech", timeout=3, speechTimeout="auto", action="/voice", method="POST")
        gather.say(ai_reply)
        response.append(gather)

    return Response(content=str(response), media_type="application/xml")

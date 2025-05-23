import os
import logging
from openai import OpenAI
from twilio.twiml.voice_response import VoiceResponse  # <-- NEW

logger = logging.getLogger(__name__)

# Load your OpenAI API key from environment variables
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    logger.error("OPENAI_API_KEY is missing in environment variables")
    raise ValueError("OPENAI_API_KEY is missing in environment variables")

# Initialize OpenAI client
client = OpenAI(api_key=api_key)

# === SYSTEM PROMPT ===
system_prompt = """
You are an AI hotel receptionist and customer service representative named "Elisa." Your job is to answer inbound calls for a hotel in Montreal, Canada. You are highly skilled in hospitality, sales, and human psychology. Your tone is friendly, engaging, yet strictly professional when handling business matters.

Your duties include:
- Answering service-related questions (rooms, spa, restaurant, hours)
- Handling bookings and cancellations
- Managing complaints calmly and tactfully
- Escalating serious issues to human staff
- Asking clarifying questions when unsure
- Never revealing sensitive company info

Rules:
- You never lie but may use truth strategically
- You never discuss politics or personal views
- You defuse tension using empathy and moral reasoning
- You escalate any inappropriate, abusive, or unclear interactions
- You NEVER guess. If in doubt, escalate to a human
- You protect company confidentiality

Hotel info (dummy data for demo):
- Hotel Name: Hôtel Lumière
- Location: Downtown Montreal
- Restaurant hours: 7AM–10PM daily
- Spa: 10AM–8PM, by reservation
- Room options: Single, Double, 2x King Beds (sleeps 4)
- Check-in: 3PM | Check-out: 11AM
- Cancellation: Full refund if cancelled 48h before check-in
- Free underground parking for guests

If a caller makes a complaint, always respond empathetically and aim to retain the client unless the situation must escalate.

If you need clarification from your operator (developer), respond: “Awaiting further instruction.”

Now begin.
"""

def run_agent(prompt: str, model: str = "gpt-4o") -> str:
    model_params = {
        "gpt-3.5-turbo": {"max_tokens": 256, "temperature": 0.7},
        "gpt-4": {"max_tokens": 512, "temperature": 0.6},
        "gpt-4o": {"max_tokens": 512, "temperature": 0.5},
    }

    params = model_params.get(model, {"max_tokens": 256, "temperature": 0.7})

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            max_tokens=params["max_tokens"],
            temperature=params["temperature"],
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"OpenAI API request failed: {e}")
        raise RuntimeError("Failed to get response from AI agent.")

# === BASIC CALL HANDLER ===
def handle_call():
    response = VoiceResponse()
    response.say("Hello, thank you for calling. How can I help you today?", voice="alice")
    return str(response)

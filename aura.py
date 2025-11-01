import os
import json
from datetime import datetime

# Try optional imports (Groq and Supabase). If they're not installed, provide
# safe local fallbacks so the script can run without external dependencies.
user_id = "test_user"

try:
    from groq import Groq
    GROQ_KEY = os.environ.get("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", None)
    groq = Groq(api_key=GROQ_KEY) if GROQ_KEY else None
except Exception:
    groq = None

try:
    from supabase import create_client
    SUPABASE_URL = os.environ.get("SUPABASE_URL", None)
    SUPABASE_KEY = os.environ.get("SUPABASE_KEY", None)
    supabase = None
    if SUPABASE_URL and SUPABASE_KEY:
        try:
            supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        except Exception:
            supabase = None
except Exception:
    supabase = None

# Local fallback storage file when Supabase is unavailable
LOCAL_CONV_FILE = os.path.join(os.path.dirname(__file__), "conversations.json")


def detect_emotion(text):
    text = text.lower()
    if any(word in text for word in ["stress", "anxious", "worried", "nervous"]):
        return "anxious"
    if any(word in text for word in ["sad", "depressed", "down", "lonely"]):
        return "sad"
    if any(word in text for word in ["excited", "happy", "great", "amazing"]):
        return "excited"
    return "neutral"


def get_memory():
    # If Supabase is available, try to fetch recent conversations
    if supabase is not None:
        try:
            result = supabase.table("conversations").select("*").eq(
                "user_id", user_id
            ).order("timestamp", desc=True).limit(5).execute()

            if not getattr(result, "data", None):
                return ""

            memory = ""
            for conv in reversed(result.data):
                memory += f"User: {conv.get('user_input','')}\nAURA: {conv.get('aura_response','')}\n\n"
            return memory
        except Exception:
            # fall through to local file
            pass

    # Local fallback: read last 5 entries from JSON file
    if os.path.exists(LOCAL_CONV_FILE):
        try:
            with open(LOCAL_CONV_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            return ""

        # data expected to be a list of conversations
        mem_items = [d for d in data if d.get("user_id") == user_id]
        if not mem_items:
            return ""
        mem_items = mem_items[-5:]
        memory = ""
        for conv in mem_items:
            memory += f"User: {conv.get('user_input','')}\nAURA: {conv.get('aura_response','')}\n\n"
        return memory

    return ""


def save_conversation(user_input, aura_response, emotion):
    entry = {
        "user_id": user_id,
        "user_input": user_input,
        "aura_response": aura_response,
        "emotion": emotion,
        "timestamp": datetime.now().isoformat(),
    }

    if supabase is not None:
        try:
            supabase.table("conversations").insert(entry).execute()
            return
        except Exception:
            # fall back to local file
            pass

    # Save locally to JSON file
    data = []
    try:
        if os.path.exists(LOCAL_CONV_FILE):
            with open(LOCAL_CONV_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
    except Exception:
        data = []

    data.append(entry)
    try:
        with open(LOCAL_CONV_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        # last resort: ignore write errors
        pass


def chat(user_input):
    # Detect emotion
    emotion = detect_emotion(user_input)
    
    # Get memory
    memory = get_memory()
    
    # Build prompt
    system_prompt = f"""You are AURA, an emotionally intelligent AI companion.

You are warm, curious, and deeply empathetic. You:
- Remember past conversations and reference them naturally
- Adapt your tone to match the user's emotional state
- Ask questions before giving advice
- Keep responses brief (2-3 sentences)
- Admit when you're uncertain

Recent conversation history:
{memory}

The user's current emotion seems: {emotion}"""

    # Try to use Groq if available; otherwise use a small local fallback
    aura_response = ""

    if groq is not None:
        try:
            response = groq.chat.completions.create(
                model="llama-3.1-70b-versatile",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ],
                temperature=0.8,
                max_tokens=150
            )
            # Some SDKs return slightly different shapes; guard safely
            aura_response = getattr(getattr(response.choices[0], 'message', None), 'content', None) or getattr(response.choices[0], 'text', None) or str(response)
        except Exception:
            aura_response = None

    if not aura_response:
        # Simple deterministic fallback response generator
        def fallback_generate(user_input, memory, emotion):
            user_input = user_input.strip()
            if not user_input:
                return "I'm here when you're ready to talk. What's on your mind?"
            if emotion == "anxious":
                return "I hear that you're feeling anxious — can you tell me what's making you feel that way right now?"
            if emotion == "sad":
                return "I'm sorry you're feeling down. Do you want to share more about what's been happening?"
            if emotion == "excited":
                return "That's awesome — what's the best part about that for you?"
            # neutral
            # If there's memory, reference it briefly
            if memory:
                return "I remember we talked about that before — can you remind me what changed?"
            return "Thanks for sharing. How does that make you feel right now?"

        aura_response = fallback_generate(user_input, memory, emotion)

    # Save to memory (either supabase or local)
    save_conversation(user_input, aura_response, emotion)

    return aura_response, emotion


# Main chat loop
print("AURA: Hey, I'm AURA. What's on your mind?\n")

while True:
    user_input = input("You: ")
    
    if user_input.lower() in ["quit", "exit", "bye"]:
        print("AURA: Talk soon. Take care.")
        break
    
    response, emotion = chat(user_input)
    print(f"AURA ({emotion}): {response}\n")
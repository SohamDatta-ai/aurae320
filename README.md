#  AURA E 320 is part of my the project aura which is Local-friendly.

 This is a local test project which uses the groq LLM for assistanct with the emotional context window  and the superbase to store the memory of  the conversations and uses that memory in the future conversations
 
This project is designed to run with optional cloud integrations (Groq for model completions and Supabase for storing conversation history). However, it includes safe local fallbacks so you can run and test the app without any external services.

## Features

- Emotion detection from user text (simple rule-based heuristic).
- Conversation memory: uses Supabase when configured, otherwise stores locally in `conversations.json`.
- Model completions via Groq when configured; otherwise a deterministic local fallback response generator.
- Small, interactive REPL (`aura.py`) for quick testing.

## Files

- `aura.py` — Main script. Run this to start the REPL.
- `conversations.json` — Local fallback storage (auto-created on first run if needed).
- `.ENV` (optional) — place your environment variables here or set them in your shell.

## Quick start (Windows PowerShell)

1. Ensure you have Python 3.8+ installed. Check with:

```powershell
python --version
```

2. (Optional) Create a virtual environment and activate it:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

3. Install optional dependencies if you want to use Groq and Supabase integrations (otherwise you can skip this and AURA will run with local fallbacks):

```powershell
pip install groq-python supabase
```

Note: package names may differ depending on provider SDKs; if `pip install` fails, install the correct SDKs for your environment or run offline.

4. (Optional) Provide API keys via environment variables. In PowerShell you can set them for the session like this:

```powershell
$env:GROQ_KEY = "your_groq_api_key_here"
$env:SUPABASE_URL = "https://your-project.supabase.co"
$env:SUPABASE_KEY = "your_supabase_anon_or_service_key"
```

You can also place them in a `.env` or `.ENV` file and load them into your shell if you prefer.

5. Run the app:

```powershell
python aura.py
```

You should see an initial greeting like:

AURA: Hey, I'm AURA. What's on your mind?

Type messages and press Enter to chat. Type `quit`, `exit`, or `bye` to quit.

## Behavior notes

- If Groq is configured and reachable, AURA will use the model to generate responses. If not, it uses a small deterministic fallback generator that is helpful for offline testing.
- If Supabase is configured and reachable, conversations are saved there. If not, they are appended to `conversations.json` in the project root.
- The fallback behavior makes this project usable without signing up for services while preserving integration paths for production usage.

## Troubleshooting

- Import errors on start: install the optional dependencies listed above or run without them (the script will fall back to local mode). If you see linter/editor warnings about unresolved imports, they are editor static analysis warnings — runtime behavior is guarded by try/except in `aura.py`.
- Permission errors when writing `conversations.json`: ensure the project folder is writable by your user.
- If messages from Groq or Supabase return unexpected shapes, check your SDK versions and API responses; the code includes safe guards but may need small adjustments for different SDK versions.

## Next steps / improvements

- Add unit tests for emotion detection and persistence layer.
- Replace the local fallback generator with a small local LLM (e.g., via Hugging Face + transformers) if you want stronger offline responses.
- Add better configuration support (.env loader like `python-dotenv`) and a `requirements.txt` or `pyproject.toml`.

## License

MIT — feel free to adapt and reuse.


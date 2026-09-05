# Python

- Runtime: Python 3.12.12 (documented; not a pip pin).
- App: Gradio `ChatInterface` under `backend/src/` (`backend/src/app.py`).
- Model client: MiniMax-M2.5 via the OpenAI-compatible `OpenAI()` client (`openai`).
- Pin only direct runtime deps in `backend/requirements.txt`. Do not pin unused transitives (fastapi, uvicorn, httpx).
- Current pins:

```
gradio==6.26.0
openai==3.8.0
pypdf==6.17.0
python-dotenv==1.2.3
requests==2.34.2
```

- Install into `backend/.venv` with `uv pip install --python backend/.venv/bin/python`.
- Do not change visitor-facing chat behavior unless a product change says so.

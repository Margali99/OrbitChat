# 🐾 Margali's Orbit 🪐

A fast, lightweight, and modern multi-model AI assistant with a cat theme, built on FastAPI, LiteLLM, and vanilla web technologies.

---

## ✨ Features

- **Multi-Model Support**: Connect to **Google Gemini** (AI Studio), **Anthropic Claude**, and **xAI Grok** via LiteLLM.
- **BYOK (Bring Your Own Key)**: Encrypted key storage at rest with Fernet, scoped per session.
- **Real-Time Streaming**: Smooth SSE (Server-Sent Events) token streaming.
- **Web Search & Browsing**: Live internet search and URL scraping powered by Tavily.
- **File Upload & Parsing**: Upload and analyze `.pdf`, `.docx`, and `.txt` documents.
- **Playful & Clean UI**:
  - Collapsible sidebar for past orbits / chats
  - Cat paw thinking animation while loading responses
  - Starter prompt suggestions
  - Message feedback (👍 / 👎)
  - Color-accented, clean responsive layout

---

## 📁 Project Structure

```text
orbit/
├── app/
│   ├── llm/            # LiteLLM router and tools (Tavily search & scrape)
│   ├── routers/        # FastAPI routers (chat, session, keys, upload)
│   ├── security/       # Key encryption (Fernet) & session verification
│   ├── config.py       # Pydantic environment settings
│   └── main.py         # FastAPI application entrypoint
├── static/
│   ├── app.js          # Chat UI logic & SSE streaming client
│   ├── index.html      # Margali's Orbit frontend
│   └── style.css       # Responsive styling & cat animations
├── tests/              # Pytest test suite
├── .env.example        # Environment variable template
├── .gitignore          # Git ignore rules
├── conftest.py         # Test configuration & path setup
├── render.yaml         # One-click Render deployment blueprint
└── requirements.txt    # Python dependencies
```

---

## 🚀 Getting Started

### 1. Clone & Set Up Virtual Environment

```bash
git clone <your-repo-url>
cd orbit

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Fill in your configuration:
```env
SUPABASE_URL=https://your-supabase-url.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-supabase-service-role-key
KEY_ENCRYPTION_SECRET=your-32-byte-fernet-key
GEMINI_API_KEY=your-gemini-api-key
TAVILY_API_KEY=your-tavily-api-key
```

### 3. Run the Development Server

```bash
uvicorn app.main:app --reload --port 8000
```

Open your browser and navigate to:
**`http://localhost:8000`**

---

## 🧪 Running Tests

```bash
pytest tests/ -v
```

---

## ☁️ Deployment

Margali's Orbit is ready for deployment on platforms like Render, Railway, or Fly.io:
- Included **`render.yaml`** configuration for rapid setup.
- Standard ASGI entry point: `app.main:app`.

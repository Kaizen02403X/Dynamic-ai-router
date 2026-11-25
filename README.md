[dynamic_ai_router_readme.md](https://github.com/user-attachments/files/35413395/dynamic_ai_router_readme.md)
# 🚀 Dynamic AI Router & Kill Switch

## Powered By
[![Flagsmith](https://img.shields.io/badge/Feature%20Flags-Flagsmith-6633FF?style=for-the-badge)](https://www.flagsmith.com/)
A production-style AI routing gateway built with **FastAPI**, **Flagsmith**, and the **Google GenAI SDK**. Instead of hardcoding AI models and system prompts into backend code, this router fetches live configuration per user on every request—enabling instant kill switches, zero-downtime model switching, automatic failover, and live A/B testing.

---

## ✨ Key Features

* **Instant Kill Switch (`ai_kill_switch`):** Pause AI responses globally or per user in real time from the Flagsmith dashboard without touching code or restarting the server.
* **Dynamic Model & Prompt Routing (`ai_router_config`):** Swap Gemini models and system prompts on the fly via remote JSON config.
* **Automatic Failover:** If the primary model throws an API error (e.g., overload, deprecation, rate limit), the backend silently retries with a configured `fallback_model`.
* **Per-User A/B Testing:** Uses Flagsmith Identity flags (`user_id`) to split traffic cleanly across different models or personas (e.g., `user_1` vs. `user_2`).
* **Live Observability UI:** Dark-mode web interface featuring a real-time status pill (polls `/status` every 3 seconds) and per-response latency tracking (`ms`).
* **Guardrails & Secret Isolation:** Enforces a 1,000-character input cap and loads all API keys securely from a local `.env` file.

---

## 🛠️ Tech Stack

* **Backend:** Python, FastAPI, Uvicorn
* **Feature Flags & Remote Config:** Flagsmith (Local/Self-Hosted)
* **AI Provider:** Google GenAI SDK (`google-genai`)
* **Frontend:** Vanilla HTML/CSS/JavaScript
* **Config Management:** `python-dotenv`

---

## 📁 Project Structure

```text
ai-router/
├── app_1.py          # FastAPI backend, Flagsmith router, failover & latency tracking
├── index_1.html      # Dark-mode chat UI with User ID switcher & live status pill
├── .env.example      # Template for required environment variables
├── .gitignore        # Excludes .env, venv/, and cache files from Git
└── README.md         # Project documentation
```

---

## ⚙️ Setup & Installation

### 1. Clone the repository
```bash
git clone https://github.com/Kaizen02403X/Dynamic-ai-router.git
cd Dynamic-ai-router
```

### 2. Create a virtual environment & install dependencies
```bash
python3 -m venv venv
./venv/bin/python -m pip install fastapi uvicorn flagsmith google-genai python-dotenv
```

### 3. Configure environment variables
Copy `.env.example` to `.env` and fill in your keys:
```bash
cp .env.example .env
```

```env
FLAGSMITH_ENV_KEY=your_flagsmith_server_side_key
FLAGSMITH_API_URL=http://localhost:8000/api/v1/
GEMINI_API_KEY=your_gemini_api_key
```

### 4. Configure Flagsmith Flags
Ensure your local Flagsmith instance is running on `http://localhost:8000` and create two features in your environment:

1. **`ai_kill_switch`** *(Boolean Flag)*
   * Toggle **OFF** for normal operation, **ON** to immediately pause AI replies.
2. **`ai_router_config`** *(Remote Config — JSON String)*
   ```json
   {
     "model": "gemini-3.5-flash-lite",
     "fallback_model": "gemini-3.8-flash",
     "system_prompt": "You are a helpful, concise assistant."
   }
   ```
   *(Optional: Add a Multivariate / A/B test variation with a different `system_prompt` or `model` to test per-user routing.)*

### 5. Run the server
```bash
./venv/bin/python -m uvicorn app_1:app --reload --port 8080
```

Open **`http://localhost:8080`** in your browser.

---

## 🧪 Testing Scenarios

* **A/B Split:** Change the **User ID** input between `user_1`, `user_2`, `user_3`, and `user_4` to observe different prompt/model behaviors per identity.
* **Auto-Failover:** Temporarily set `"model"` in Flagsmith to an invalid name (e.g., `"broken-model"`). The router will automatically fall back to `fallback_model` and tag the reply with `(AUTO-FALLBACK)`.
* **Live Kill Switch:** Flip `ai_kill_switch` **ON** in Flagsmith and watch the top-right status pill switch to **`🚨 KILL SWITCH ON`** within 3 seconds without refreshing the page.

import json
import os
import time
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from flagsmith import Flagsmith
from google import genai
from google.genai import types, errors

load_dotenv()

app = FastAPI()

flagsmith = Flagsmith(
    environment_key=os.getenv("FLAGSMITH_ENV_KEY"),
    api_url=os.getenv("FLAGSMITH_API_URL", "http://localhost:8000/api/v1/"),
)
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

class ChatRequest(BaseModel):
    message: str
    user_id: str = "guest"

@app.get("/", response_class=HTMLResponse)
def home():
    with open("index_1.html", "r") as f:
        return f.read()

@app.get("/status")
def status(user_id: str = "guest"):
    flags = flagsmith.get_identity_flags(identifier=user_id)
    killed = flags.is_feature_enabled("ai_kill_switch")
    config = json.loads(flags.get_feature_value("ai_router_config"))
    return {"killed": killed, "model": config["model"]}

@app.post("/chat")
def chat(req: ChatRequest):
    # Safety Protocol: Cap input length
    if len(req.message) > 1000:
        return {"reply": "⚠️ Message too long (max 1000 characters).", "model": "GUARDRAIL", "killed": False}

    flags = flagsmith.get_identity_flags(identifier=req.user_id)

    # Safety Protocol: Kill Switch
    if flags.is_feature_enabled("ai_kill_switch"):
        return {
            "reply": "🚨 AI is currently paused for maintenance. Please try again later.",
            "model": "KILL SWITCH",
            "killed": True,
        }

    config = json.loads(flags.get_feature_value("ai_router_config"))

    primary_model = config["model"]
    fallback_model = config.get("fallback_model")
    gen_config = types.GenerateContentConfig(
        system_instruction=config["system_prompt"],
        max_output_tokens=500,
    )

    start = time.perf_counter()

    # 1. Try the primary model first
    try:
        response = client.models.generate_content(
            model=primary_model,
            contents=req.message,
            config=gen_config,
        )
        ms = round((time.perf_counter() - start) * 1000)
        return {"reply": response.text, "model": primary_model, "killed": False, "latency_ms": ms}

    # 2. If primary fails (503 overload, 404 typo, rate limit), auto-switch to fallback
    except (errors.ServerError, errors.ClientError) as primary_err:
        if fallback_model:
            try:
                response = client.models.generate_content(
                    model=fallback_model,
                    contents=req.message,
                    config=gen_config,
                )
                ms = round((time.perf_counter() - start) * 1000)
                return {
                    "reply": response.text,
                    "model": f"{fallback_model} (AUTO-FALLBACK)",
                    "killed": False,
                    "latency_ms": ms,
                }
            except (errors.ServerError, errors.ClientError) as fallback_err:
                return {
                    "reply": f"⚠️ Both primary and fallback models failed: {fallback_err.message}",
                    "model": "ALL MODELS FAILED",
                    "killed": True,
                }
        return {"reply": f"⚠️ Model error: {primary_err.message}", "model": primary_model, "killed": True}

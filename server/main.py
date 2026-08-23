from fastapi import FastAPI, Request, Response
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from dotenv import load_dotenv

import api
import webhook
from state import AppState, Deployment

import hashlib
import hmac
import json
import os

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

app = FastAPI()
state = AppState()


@app.get("/health")
def health() -> Response:
    return Response("ok", media_type="text/plain")


@app.post("/webhook")
async def handle(request: Request) -> Response:
    body = await request.body()
    secret = os.getenv("WEBHOOK_SECRET", "")

    if secret:
        signature = request.headers.get("X-Hub-Signature-256", "")
        expected = "sha256=" + hmac.new(
            secret.encode(), body, hashlib.sha256
        ).hexdigest()
        if not hmac.compare_digest(signature, expected):
            return Response(status_code=401)

    payload = json.loads(body)
    return Response(status_code=await webhook.handle(state, payload))


@app.get("/api/status")
def status() -> Deployment | None:
    return api.status(state)


DIST = ROOT / "client" / "dist"
if DIST.is_dir():
    app.mount("/", StaticFiles(directory=DIST, html=True))

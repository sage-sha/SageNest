from fastapi import FastAPI, Request, Response

import api
import webhook
from state import AppState, Deployment

app = FastAPI()
state = AppState()


@app.get("/health")
def health() -> Response:
    return Response("ok", media_type="text/plain")


@app.post("/webhook")
async def handle(request: Request) -> Response:
    return Response(status_code=await webhook.handle(state, await request.json()))


@app.get("/api/status")
def status() -> Deployment | None:
    return api.status(state)

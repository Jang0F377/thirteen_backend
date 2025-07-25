import time
from contextlib import asynccontextmanager
from typing import Callable

import redis.asyncio as aioredis
from fastapi import FastAPI, Request, Response
from prometheus_client import make_asgi_app
from starlette.middleware.cors import CORSMiddleware

from thirteen_backend import config, metrics
from thirteen_backend.api import healthcheck, sessions, websocket
from thirteen_backend.logger import LOGGER

logger = LOGGER


@asynccontextmanager
async def lifespan(asgi_app: FastAPI):
    asgi_app.state.redis_client = aioredis.from_url(config.CACHE_URL)
    await asgi_app.state.redis_client.ping()
    yield
    await asgi_app.state.redis_client.aclose()


app = FastAPI(lifespan=lifespan)
metrics_app = make_asgi_app()


app.mount("/metrics", metrics_app)
app.include_router(healthcheck.router)
app.include_router(sessions.router)
app.include_router(websocket.router)


@app.middleware("http")
async def handle_request_metrics(request: Request, call_next: Callable) -> Response:
    start_time = time.perf_counter()
    response = await call_next(request)
    request_duration = time.perf_counter() - start_time
    metrics.track_request(
        method=request.method,
        path=request.url.path,
        status=response.status_code,
    )
    metrics.track_request_duration(
        method=request.method,
        path=request.url.path,
        status=response.status_code,
        duration=request_duration,
    )
    return response


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import redis.asyncio as aioredis 

from thirteen_backend import config
from thirteen_backend.logger import LOGGER
from thirteen_backend.api import healthcheck, sessions


logger = LOGGER


@asynccontextmanager
async def lifespan(asgi_app: FastAPI):
    asgi_app.state.redis_client = aioredis.from_url(config.CACHE_URL)
    await asgi_app.state.redis_client.ping()
    yield
    await asgi_app.state.redis_client.aclose()


app = FastAPI(lifespan=lifespan)


app.include_router(healthcheck.router)
app.include_router(sessions.router)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

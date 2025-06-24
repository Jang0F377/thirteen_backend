from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import redis.asyncio as aioredis

from thirteen_backend import config
from thirteen_backend.logger import LOGGER


logger = LOGGER


@asynccontextmanager
async def lifespan(asgi_app: FastAPI):
    redis_client = aioredis.from_url(config.CACHE_URL)
    await redis_client.ping()
    yield
    await redis_client.aclose()


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

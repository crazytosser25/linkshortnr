import os
from dotenv import load_dotenv
from contextlib import asynccontextmanager


from fastapi import FastAPI, Depends
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import redis.asyncio as redis
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter

# from src.database.db import new_session
from src.shortner.router import shortner_router


load_dotenv()
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS")
BACKEND_BASE_URL = os.getenv("BACKEND_BASE_URL")


@asynccontextmanager
async def lifespan(app: FastAPI):  # pylint: disable=W0613, W0621
    """Define the lifespan of the FastAPI application.

    This function manages the lifecycle of the FastAPI application, initializing and closing
    resources such as Redis and FastAPILimiter during the app's lifespan.

    Args:
        app (FastAPI): The FastAPI application instance.

    Yields:
        Allows the FastAPI application to run within this context, managing resources.
    """
    global r  # pylint: disable=W0603
    r = await redis.Redis(
        host=os.getenv("REDIS_HOST"),
        port=os.getenv("REDIS_PORT"),
        db=0, encoding="utf-8",
        decode_responses=True
    )
    await FastAPILimiter.init(r)

    yield

    r.close()


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Static page routes
@app.get("/", dependencies=[Depends(RateLimiter(times=5, seconds=30))])
async def main_page():
    return FileResponse("static/index.html")

@app.get("/config", dependencies=[Depends(RateLimiter(times=5, seconds=30))])
async def get_config():
    return {
        "backendBase": BACKEND_BASE_URL
    }

@app.get("/favicon.ico", dependencies=[Depends(RateLimiter(times=5, seconds=30))])
async def favicon():
    return FileResponse("static/favicon.ico")

@app.get("/logo", dependencies=[Depends(RateLimiter(times=5, seconds=30))])
async def photo():
    return FileResponse("static/logo.png")

app.include_router(shortner_router)

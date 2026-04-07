from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import connect_db, close_db
from .routes import officers, schedules, exchanges


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_db()
    yield
    await close_db()


app = FastAPI(
    title="OnDutyService API",
    description="API for managing officer duty schedules",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(officers.router, prefix="/api")
app.include_router(schedules.router, prefix="/api")
app.include_router(exchanges.router, prefix="/api")


@app.get("/")
async def root():
    return {"message": "OnDutyService API is running"}


@app.get("/health")
async def health():
    return {"status": "ok"}

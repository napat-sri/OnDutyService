from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import connect_db, close_db
from .routes import officers, schedules, exchanges

app = FastAPI(
    title="OnDutyService API",
    description="API for managing officer duty schedules",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    await connect_db()


@app.on_event("shutdown")
async def shutdown_event():
    await close_db()


app.include_router(officers.router, prefix="/api")
app.include_router(schedules.router, prefix="/api")
app.include_router(exchanges.router, prefix="/api")


@app.get("/")
async def root():
    return {"message": "OnDutyService API is running"}


@app.get("/health")
async def health():
    return {"status": "ok"}

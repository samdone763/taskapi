from fastapi import FastAPI
from app.api.v1.router import api_router
from app.db.session import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Task Management API",
    description="REST API ya kusimamia kazi na JWT auth.",
    version="1.0.0",
)

app.include_router(api_router)


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok"}

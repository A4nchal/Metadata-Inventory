from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.config.database import mongo
from app.controller.metadata_controller import router as metadata_router

@asynccontextmanager
async def lifespan(app: FastAPI):

    await mongo.connect()
    await mongo.create_indexes()
    print("Application started successfully")

    yield

    await mongo.close()
    print("Application shutdown complete")


app = FastAPI(
    title="HTTP Metadata Inventory Service",
    version="1.0.0",
    description="Service for collecting and storing HTTP metadata.",
    lifespan=lifespan
)

app.include_router(metadata_router)

@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "UP"}
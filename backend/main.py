from fastapi import FastAPI
from app.database import engine, Base
from app.routers import nodes, tasks, system
from app.models import task, system as system_model # Import specific model to ensure it is registered with Base
from app.services.scheduler import start_scheduler
from contextlib import asynccontextmanager

# Create tables
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    start_scheduler()
    yield
    # Shutdown (if needed)

app = FastAPI(title="Crawler Task Manager API", version="0.1.0", lifespan=lifespan)

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(nodes.router)
app.include_router(tasks.router)
app.include_router(system.router)

@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "Service is healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

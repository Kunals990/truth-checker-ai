from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.database import create_tables
from app.routers import auth, users
from app.config import settings

# Create tables on startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    create_tables()
    yield
    # Shutdown
    pass

# Create FastAPI application
app = FastAPI(
    title="FastAPI Google OAuth Authentication",
    description="A complete authentication system using Google OAuth",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(users.router)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Root endpoint to serve main page
@app.get("/", response_class=HTMLResponse)
async def root():
    with open("app/static/index.html", "r") as f:
        return HTMLResponse(f.read())

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "FastAPI Google Auth is running!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app", 
        host=settings.host, 
        port=settings.port, 
        reload=settings.debug
    )
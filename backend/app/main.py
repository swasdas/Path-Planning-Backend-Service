"""Main FastAPI application"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.api import walls, obstacles, paths, metrics, websocket
from app.config import settings

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="Wall Finishing Robot Control System",
    description="Autonomous robot path planning and control system for wall finishing tasks",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(walls.router)
app.include_router(obstacles.router)
app.include_router(paths.router)
app.include_router(metrics.router)
app.include_router(websocket.router)

@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "Wall Finishing Robot Control System API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
def health_check():
    """Health check endpoint"""
    from app.cache import get_redis_client

    # Check Redis
    redis_ok = False
    try:
        redis_client = get_redis_client()
        redis_ok = redis_client.ping()
    except Exception:
        pass

    return {
        "status": "healthy",
        "database": "connected",
        "redis": "connected" if redis_ok else "disconnected"
    }

@app.on_event("startup")
async def startup_event():
    """Startup tasks"""
    print("🤖 Starting Wall Finishing Robot Control System...")
    print(f"📚 API Documentation: http://localhost:8000/docs")
    print(f"🔧 Algorithm Settings:")
    print(f"   - Grid Resolution: {settings.grid_resolution}m")
    print(f"   - GA Population: {settings.ga_population_size}")
    print(f"   - GA Generations: {settings.ga_generations}")

@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown tasks"""
    print("🛑 Shutting down Wall Finishing Robot Control System...")

"""
ViWO Token Economy Simulator - FastAPI Backend
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import simulation, websocket, export

app = FastAPI(
    title="ViWO Token Economy Simulator",
    description="Backend API for token economy simulations with deterministic, Monte Carlo, and Agent-Based modeling",
    version="1.0.0",
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(simulation.router, prefix="/api", tags=["simulation"])
app.include_router(websocket.router, prefix="/ws", tags=["websocket"])
app.include_router(export.router, prefix="/api", tags=["export"])


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "1.0.0"}


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "ViWO Token Economy Simulator",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "health": "/api/health",
            "deterministic": "/api/simulate/deterministic",
            "monte_carlo": "/api/simulate/monte-carlo",
            "agent_based": "/api/simulate/agent-based",
            "websocket": "/ws/simulation/{job_id}",
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


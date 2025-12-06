"""
WebSocket endpoints for streaming simulation results.
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.simulation_runner import SimulationRunner
import asyncio
import json

router = APIRouter()
simulation_runner = SimulationRunner()


@router.websocket("/simulation/{job_id}")
async def websocket_simulation(websocket: WebSocket, job_id: str):
    """
    WebSocket endpoint for streaming simulation progress and results.
    """
    await websocket.accept()
    
    try:
        # Subscribe to job updates
        while True:
            # Check if job exists
            status = simulation_runner.get_status(job_id)
            
            if status is None:
                await websocket.send_json({
                    "type": "error",
                    "message": "Job not found",
                    "details": f"No simulation found with ID: {job_id}"
                })
                break
            
            # Send progress update
            if status["status"] == "running":
                await websocket.send_json({
                    "type": "progress",
                    "current": status["current"],
                    "total": status["total"],
                    "percentage": status["percentage"],
                })
            elif status["status"] == "completed":
                await websocket.send_json({
                    "type": "complete",
                    "result": status["result"]
                })
                break
            elif status["status"] == "error":
                await websocket.send_json({
                    "type": "error",
                    "message": status["error"],
                })
                break
            
            # Wait before next update
            await asyncio.sleep(0.1)
            
    except WebSocketDisconnect:
        # Client disconnected - cancel the job if still running
        simulation_runner.cancel_job(job_id)
    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "message": str(e),
        })
    finally:
        await websocket.close()


















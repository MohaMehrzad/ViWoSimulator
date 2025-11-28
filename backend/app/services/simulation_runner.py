"""
Simulation runner service for managing async simulations.
"""

import threading
from typing import Dict, Any, Optional
from app.models import SimulationParameters
from app.core.monte_carlo import run_monte_carlo_simulation
from app.core.agent_based import run_agent_based_simulation

class SimulationRunner:
    """
    Manages async simulation jobs with progress tracking.
    Uses threading for CPU-bound simulation work.
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        # Singleton pattern for shared state
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._jobs: Dict[str, Dict[str, Any]] = {}
        return cls._instance
    
    def start_monte_carlo(
        self, 
        job_id: str, 
        params: SimulationParameters, 
        iterations: int
    ):
        """Start a Monte Carlo simulation in a background thread"""
        self._jobs[job_id] = {
            "status": "running",
            "type": "monte_carlo",
            "current": 0,
            "total": iterations,
            "percentage": 0.0,
            "result": None,
            "error": None,
            "cancelled": False,
        }
        
        def run():
            try:
                result = run_monte_carlo_simulation(
                    params, 
                    iterations,
                    progress_callback=lambda curr, total: self._update_progress(job_id, curr, total)
                )
                
                if not self._jobs[job_id]["cancelled"]:
                    self._jobs[job_id]["status"] = "completed"
                    self._jobs[job_id]["result"] = result.model_dump()
            except Exception as e:
                self._jobs[job_id]["status"] = "error"
                self._jobs[job_id]["error"] = str(e)
        
        thread = threading.Thread(target=run, daemon=True)
        thread.start()
    
    def start_agent_based(
        self,
        job_id: str,
        params: SimulationParameters,
        agent_count: int,
        duration_months: int
    ):
        """Start an agent-based simulation in a background thread"""
        self._jobs[job_id] = {
            "status": "running",
            "type": "agent_based",
            "current": 0,
            "total": duration_months,
            "percentage": 0.0,
            "result": None,
            "error": None,
            "cancelled": False,
        }
        
        def run():
            try:
                result = run_agent_based_simulation(
                    params,
                    agent_count,
                    duration_months,
                    progress_callback=lambda curr, total: self._update_progress(job_id, curr, total)
                )
                
                if not self._jobs[job_id]["cancelled"]:
                    self._jobs[job_id]["status"] = "completed"
                    self._jobs[job_id]["result"] = result.model_dump()
            except Exception as e:
                self._jobs[job_id]["status"] = "error"
                self._jobs[job_id]["error"] = str(e)
        
        thread = threading.Thread(target=run, daemon=True)
        thread.start()
    
    def _update_progress(self, job_id: str, current: int, total: int):
        """Update progress for a job"""
        if job_id in self._jobs and not self._jobs[job_id]["cancelled"]:
            self._jobs[job_id]["current"] = current
            self._jobs[job_id]["total"] = total
            self._jobs[job_id]["percentage"] = (current / total) * 100 if total > 0 else 0
    
    def get_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a job"""
        return self._jobs.get(job_id)
    
    def cancel_job(self, job_id: str):
        """Cancel a running job"""
        if job_id in self._jobs:
            self._jobs[job_id]["cancelled"] = True
            self._jobs[job_id]["status"] = "cancelled"
    
    def cleanup_job(self, job_id: str):
        """Remove a completed job from memory"""
        if job_id in self._jobs:
            del self._jobs[job_id]





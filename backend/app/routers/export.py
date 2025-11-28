"""
Export endpoints for simulation results.
"""

from fastapi import APIRouter, Response
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Any, Literal
import json
import csv
import io

router = APIRouter()


class ExportRequest(BaseModel):
    result: Any
    format: Literal['json', 'csv'] = 'json'
    filename: str = 'simulation_results'


def flatten_dict(d: dict, parent_key: str = '', sep: str = '_') -> dict:
    """Flatten nested dictionary for CSV export"""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        elif isinstance(v, list):
            for i, item in enumerate(v):
                if isinstance(item, dict):
                    items.extend(flatten_dict(item, f"{new_key}_{i}", sep=sep).items())
                else:
                    items.append((f"{new_key}_{i}", item))
        else:
            items.append((new_key, v))
    return dict(items)


@router.post("/export")
async def export_results(request: ExportRequest):
    """
    Export simulation results in JSON or CSV format.
    """
    if request.format == 'json':
        # JSON export
        content = json.dumps(request.result, indent=2)
        return Response(
            content=content,
            media_type='application/json',
            headers={
                'Content-Disposition': f'attachment; filename="{request.filename}.json"'
            }
        )
    else:
        # CSV export
        # Flatten the result for CSV
        flat_result = flatten_dict(request.result if isinstance(request.result, dict) else request.result.dict())
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header and values
        writer.writerow(flat_result.keys())
        writer.writerow(flat_result.values())
        
        return Response(
            content=output.getvalue(),
            media_type='text/csv',
            headers={
                'Content-Disposition': f'attachment; filename="{request.filename}.csv"'
            }
        )


@router.post("/export/parameters")
async def export_parameters(parameters: dict):
    """
    Export simulation parameters as JSON.
    """
    content = json.dumps(parameters, indent=2)
    return Response(
        content=content,
        media_type='application/json',
        headers={
            'Content-Disposition': 'attachment; filename="viwo-parameters.json"'
        }
    )


@router.post("/export/full-report")
async def export_full_report(data: dict):
    """
    Export full simulation report including parameters and results.
    """
    from datetime import datetime
    
    report = {
        'metadata': {
            'generated_at': datetime.now().isoformat(),
            'simulator_version': '1.0.0',
            'protocol': 'ViWO Token Economy',
        },
        'parameters': data.get('parameters', {}),
        'results': data.get('results', {}),
    }
    
    content = json.dumps(report, indent=2)
    timestamp = datetime.now().strftime('%Y-%m-%d')
    
    return Response(
        content=content,
        media_type='application/json',
        headers={
            'Content-Disposition': f'attachment; filename="viwo-full-report-{timestamp}.json"'
        }
    )





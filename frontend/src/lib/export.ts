import { SimulationParameters, SimulationResult, MonteCarloResult, AgentBasedResult } from '@/types/simulation';
import { API_BASE_URL } from './constants';

export async function exportToJson(
  result: SimulationResult | MonteCarloResult | AgentBasedResult,
  filename: string = 'simulation_results'
): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/api/export`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ result, format: 'json', filename }),
  });

  if (!response.ok) {
    throw new Error('Export failed');
  }

  const blob = await response.blob();
  downloadBlob(blob, `${filename}.json`);
}

export async function exportToCsv(
  result: SimulationResult | MonteCarloResult | AgentBasedResult,
  filename: string = 'simulation_results'
): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/api/export`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ result, format: 'csv', filename }),
  });

  if (!response.ok) {
    throw new Error('Export failed');
  }

  const blob = await response.blob();
  downloadBlob(blob, `${filename}.csv`);
}

export async function exportParameters(parameters: SimulationParameters): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/api/export/parameters`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(parameters),
  });

  if (!response.ok) {
    throw new Error('Export failed');
  }

  const blob = await response.blob();
  const timestamp = new Date().toISOString().split('T')[0];
  downloadBlob(blob, `viwo-parameters-${timestamp}.json`);
}

export async function exportFullReport(
  parameters: SimulationParameters,
  result: SimulationResult | MonteCarloResult | AgentBasedResult
): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/api/export/full-report`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ parameters, results: result }),
  });

  if (!response.ok) {
    throw new Error('Export failed');
  }

  const blob = await response.blob();
  const timestamp = new Date().toISOString().split('T')[0];
  downloadBlob(blob, `viwo-full-report-${timestamp}.json`);
}

export function importParameters(file: File): Promise<Partial<SimulationParameters>> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    
    reader.onload = (e) => {
      try {
        const content = e.target?.result as string;
        const data = JSON.parse(content);
        
        // Handle both direct parameters and full report format
        const parameters = data.parameters || data;
        resolve(parameters);
      } catch (error) {
        reject(new Error('Invalid JSON file'));
      }
    };
    
    reader.onerror = () => reject(new Error('Failed to read file'));
    reader.readAsText(file);
  });
}

function downloadBlob(blob: Blob, filename: string): void {
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

// Client-side export (fallback when backend is not available)
export function exportToJsonClient(data: unknown, filename: string = 'export'): void {
  const json = JSON.stringify(data, null, 2);
  const blob = new Blob([json], { type: 'application/json' });
  downloadBlob(blob, `${filename}.json`);
}

export function exportToCsvClient(data: Record<string, unknown>, filename: string = 'export'): void {
  const flatData = flattenObject(data);
  const headers = Object.keys(flatData).join(',');
  const values = Object.values(flatData).map(v => 
    typeof v === 'string' ? `"${v}"` : v
  ).join(',');
  
  const csv = `${headers}\n${values}`;
  const blob = new Blob([csv], { type: 'text/csv' });
  downloadBlob(blob, `${filename}.csv`);
}

function flattenObject(obj: Record<string, unknown>, prefix: string = ''): Record<string, unknown> {
  const result: Record<string, unknown> = {};
  
  for (const [key, value] of Object.entries(obj)) {
    const newKey = prefix ? `${prefix}_${key}` : key;
    
    if (value && typeof value === 'object' && !Array.isArray(value)) {
      Object.assign(result, flattenObject(value as Record<string, unknown>, newKey));
    } else if (Array.isArray(value)) {
      value.forEach((item, index) => {
        if (typeof item === 'object') {
          Object.assign(result, flattenObject(item as Record<string, unknown>, `${newKey}_${index}`));
        } else {
          result[`${newKey}_${index}`] = item;
        }
      });
    } else {
      result[newKey] = value;
    }
  }
  
  return result;
}



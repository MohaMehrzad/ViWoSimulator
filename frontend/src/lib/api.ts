import { 
  SimulationParameters, 
  SimulationResult, 
  MonteCarloResult, 
  AgentBasedResult,
  MonthlyProgressionResult,
  RetentionCurveData,
  MaturityTier,
  SimulationType 
} from '@/types/simulation';
import { API_BASE_URL } from './constants';

// Convert snake_case to camelCase
function snakeToCamel(str: string): string {
  return str.replace(/_([a-z])/g, (_, letter) => letter.toUpperCase());
}

// Convert object keys from snake_case to camelCase recursively
// Exported for use in WebSocket message handling
export function convertKeysToCamelCase<T>(obj: unknown): T {
  if (Array.isArray(obj)) {
    return obj.map(item => convertKeysToCamelCase(item)) as T;
  }
  
  if (obj !== null && typeof obj === 'object') {
    const newObj: Record<string, unknown> = {};
    for (const key of Object.keys(obj as Record<string, unknown>)) {
      const camelKey = snakeToCamel(key);
      newObj[camelKey] = convertKeysToCamelCase((obj as Record<string, unknown>)[key]);
    }
    return newObj as T;
  }
  
  return obj as T;
}

// Convert camelCase to snake_case
function camelToSnake(str: string): string {
  return str.replace(/[A-Z]/g, letter => `_${letter.toLowerCase()}`);
}

// Convert object keys from camelCase to snake_case recursively
function convertKeysToSnakeCase<T>(obj: unknown): T {
  if (Array.isArray(obj)) {
    return obj.map(item => convertKeysToSnakeCase(item)) as T;
  }
  
  if (obj !== null && typeof obj === 'object') {
    const newObj: Record<string, unknown> = {};
    for (const key of Object.keys(obj as Record<string, unknown>)) {
      const snakeKey = camelToSnake(key);
      newObj[snakeKey] = convertKeysToSnakeCase((obj as Record<string, unknown>)[key]);
    }
    return newObj as T;
  }
  
  return obj as T;
}

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ message: 'Request failed' }));
      throw new Error(error.message || `HTTP ${response.status}`);
    }

    return response.json();
  }

  // Health check
  async health(): Promise<{ status: string; version: string }> {
    return this.request('/api/health');
  }

  // Run deterministic simulation
  async runDeterministic(params: SimulationParameters): Promise<SimulationResult> {
    const snakeParams = convertKeysToSnakeCase(params);
    const result = await this.request<unknown>('/api/simulate/deterministic', {
      method: 'POST',
      body: JSON.stringify(snakeParams),
    });
    return convertKeysToCamelCase<SimulationResult>(result);
  }

  // Start Monte Carlo simulation (returns job ID for WebSocket tracking)
  async startMonteCarlo(
    params: SimulationParameters,
    iterations: number = 1000
  ): Promise<{ jobId: string }> {
    const snakeParams = convertKeysToSnakeCase(params);
    return this.request('/api/simulate/monte-carlo/start', {
      method: 'POST',
      body: JSON.stringify({ parameters: snakeParams, iterations }),
    });
  }

  // Run Monte Carlo simulation synchronously (for small iterations)
  async runMonteCarlo(
    params: SimulationParameters,
    iterations: number = 100
  ): Promise<MonteCarloResult> {
    const snakeParams = convertKeysToSnakeCase(params);
    const result = await this.request<unknown>('/api/simulate/monte-carlo', {
      method: 'POST',
      body: JSON.stringify({ parameters: snakeParams, iterations }),
    });
    return convertKeysToCamelCase<MonteCarloResult>(result);
  }

  // Start Agent-Based simulation
  async startAgentBased(
    params: SimulationParameters,
    agentCount: number = 1000,
    duration: number = 12
  ): Promise<{ jobId: string }> {
    const snakeParams = convertKeysToSnakeCase(params);
    return this.request('/api/simulate/agent-based/start', {
      method: 'POST',
      body: JSON.stringify({ 
        parameters: snakeParams, 
        agent_count: agentCount,
        duration_months: duration 
      }),
    });
  }

  // Run Agent-Based simulation synchronously
  async runAgentBased(
    params: SimulationParameters,
    agentCount: number = 100,
    duration: number = 12
  ): Promise<AgentBasedResult> {
    const snakeParams = convertKeysToSnakeCase(params);
    const result = await this.request<unknown>('/api/simulate/agent-based', {
      method: 'POST',
      body: JSON.stringify({ 
        parameters: snakeParams, 
        agent_count: agentCount,
        duration_months: duration 
      }),
    });
    return convertKeysToCamelCase<AgentBasedResult>(result);
  }

  // Run Monthly Progression simulation (Issue #16)
  async runMonthlyProgression(
    params: SimulationParameters,
    durationMonths: number = 24,
    includeSeasonality: boolean = true,
    marketSaturationFactor: number = 0
  ): Promise<MonthlyProgressionResult> {
    const snakeParams = convertKeysToSnakeCase(params);
    const result = await this.request<unknown>('/api/simulate/monthly-progression', {
      method: 'POST',
      body: JSON.stringify({ 
        parameters: snakeParams, 
        duration_months: durationMonths,
        include_seasonality: includeSeasonality,
        market_saturation_factor: marketSaturationFactor
      }),
    });
    return convertKeysToCamelCase<MonthlyProgressionResult>(result);
  }

  // Get retention curves (Issue #1)
  async getRetentionCurves(): Promise<Record<string, RetentionCurveData>> {
    const result = await this.request<unknown>('/api/retention-curves');
    return convertKeysToCamelCase<Record<string, RetentionCurveData>>(result);
  }

  // Get platform maturity tiers
  async getPlatformMaturityTiers(): Promise<{ tiers: MaturityTier[] }> {
    const result = await this.request<unknown>('/api/platform-maturity-tiers');
    return convertKeysToCamelCase<{ tiers: MaturityTier[] }>(result);
  }

  // Get presets
  async getPresets(): Promise<Record<string, Partial<SimulationParameters>>> {
    return this.request('/api/presets');
  }

  // Export results
  async exportResults(
    result: SimulationResult | MonteCarloResult | AgentBasedResult | MonthlyProgressionResult,
    format: 'json' | 'csv' = 'json'
  ): Promise<Blob> {
    const response = await fetch(`${this.baseUrl}/api/export`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ result, format }),
    });

    if (!response.ok) {
      throw new Error('Export failed');
    }

    return response.blob();
  }
}

export const api = new ApiClient();
export default api;

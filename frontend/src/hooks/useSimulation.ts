'use client';

import { useState, useCallback, useEffect, useRef, useMemo } from 'react';
import { 
  SimulationParameters, 
  SimulationResult, 
  MonteCarloResult, 
  AgentBasedResult,
  SimulationType,
  PercentileKey,
  WebSocketMessage 
} from '@/types/simulation';
import { DEFAULT_PARAMETERS, WS_BASE_URL } from '@/lib/constants';
import { deepMerge } from '@/lib/utils';
import api, { convertKeysToCamelCase } from '@/lib/api';

interface SimulationState {
  parameters: SimulationParameters;
  result: SimulationResult | null;
  monteCarloResult: MonteCarloResult | null;
  agentBasedResult: AgentBasedResult | null;
  isLoading: boolean;
  error: string | null;
  progress: number;
  simulationType: SimulationType;
  selectedPercentile: PercentileKey;
}

export function useSimulation() {
  const [state, setState] = useState<SimulationState>({
    parameters: DEFAULT_PARAMETERS,
    result: null,
    monteCarloResult: null,
    agentBasedResult: null,
    isLoading: false,
    error: null,
    progress: 0,
    simulationType: 'deterministic',
    selectedPercentile: 'p50',
  });

  const wsRef = useRef<WebSocket | null>(null);
  const jobIdRef = useRef<string | null>(null);

  // Compute the active result based on simulation type and selected percentile
  const activeResult = useMemo((): SimulationResult | null => {
    switch (state.simulationType) {
      case 'deterministic':
        return state.result;
      case 'monte_carlo':
        // Return the selected percentile from Monte Carlo results, or fall back to deterministic
        if (state.monteCarloResult?.percentiles) {
          return state.monteCarloResult.percentiles[state.selectedPercentile];
        }
        return state.result; // Fallback to deterministic while MC is running
      case 'agent_based':
        // Agent-based doesn't produce per-module results, so use deterministic as baseline
        return state.result;
      default:
        return state.result;
    }
  }, [state.simulationType, state.result, state.monteCarloResult, state.selectedPercentile]);

  // Update a single parameter
  const updateParameter = useCallback(<K extends keyof SimulationParameters>(
    key: K,
    value: SimulationParameters[K]
  ) => {
    setState(prev => ({
      ...prev,
      parameters: { ...prev.parameters, [key]: value },
    }));
  }, []);

  // Update multiple parameters at once
  const updateParameters = useCallback((updates: Partial<SimulationParameters>) => {
    setState(prev => ({
      ...prev,
      parameters: deepMerge(prev.parameters, updates),
    }));
  }, []);

  // Reset to defaults
  const resetParameters = useCallback(() => {
    setState(prev => ({
      ...prev,
      parameters: DEFAULT_PARAMETERS,
    }));
  }, []);

  // Load preset
  const loadPreset = useCallback((preset: Partial<SimulationParameters>) => {
    setState(prev => ({
      ...prev,
      parameters: deepMerge(DEFAULT_PARAMETERS, preset),
    }));
  }, []);

  // Set simulation type
  const setSimulationType = useCallback((type: SimulationType) => {
    setState(prev => ({ ...prev, simulationType: type }));
  }, []);

  // Set selected percentile for Monte Carlo results
  const setSelectedPercentile = useCallback((percentile: PercentileKey) => {
    setState(prev => ({ ...prev, selectedPercentile: percentile }));
  }, []);

  // Run deterministic simulation
  const runDeterministic = useCallback(async () => {
    setState(prev => ({ ...prev, isLoading: true, error: null }));
    
    try {
      const result = await api.runDeterministic(state.parameters);
      setState(prev => ({ ...prev, result, isLoading: false }));
      return result;
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Simulation failed';
      setState(prev => ({ ...prev, error: message, isLoading: false }));
      throw error;
    }
  }, [state.parameters]);

  // Connect to WebSocket for streaming results
  const connectWebSocket = useCallback((jobId: string) => {
    if (wsRef.current) {
      wsRef.current.close();
    }

    const ws = new WebSocket(`${WS_BASE_URL}/ws/simulation/${jobId}`);
    wsRef.current = ws;
    jobIdRef.current = jobId;

    ws.onmessage = (event) => {
      // Convert snake_case keys from backend to camelCase for frontend
      const rawMessage = JSON.parse(event.data);
      const message = convertKeysToCamelCase<WebSocketMessage>(rawMessage);

      if (message.type === 'progress') {
        setState(prev => ({ 
          ...prev, 
          progress: message.percentage,
        }));
      } else if (message.type === 'complete') {
        setState(prev => {
          const newState = { ...prev, isLoading: false, progress: 100 };
          
          // Determine result type based on current simulation type
          if (prev.simulationType === 'monte_carlo') {
            newState.monteCarloResult = message.result as MonteCarloResult;
          } else if (prev.simulationType === 'agent_based') {
            newState.agentBasedResult = message.result as AgentBasedResult;
          }
          
          return newState;
        });
        ws.close();
      } else if (message.type === 'error') {
        setState(prev => ({ 
          ...prev, 
          error: message.message, 
          isLoading: false 
        }));
        ws.close();
      }
    };

    ws.onerror = () => {
      setState(prev => ({ 
        ...prev, 
        error: 'WebSocket connection failed', 
        isLoading: false 
      }));
    };

    ws.onclose = () => {
      wsRef.current = null;
      jobIdRef.current = null;
    };
  }, []);

  // Run Monte Carlo simulation
  const runMonteCarlo = useCallback(async (iterations: number = 1000) => {
    setState(prev => ({ 
      ...prev, 
      isLoading: true, 
      error: null, 
      progress: 0,
      simulationType: 'monte_carlo' 
    }));

    try {
      if (iterations <= 100) {
        // Small iterations - run synchronously
        const result = await api.runMonteCarlo(state.parameters, iterations);
        setState(prev => ({ 
          ...prev, 
          monteCarloResult: result, 
          isLoading: false,
          progress: 100 
        }));
        return result;
      } else {
        // Large iterations - use WebSocket streaming
        const { jobId } = await api.startMonteCarlo(state.parameters, iterations);
        connectWebSocket(jobId);
      }
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Simulation failed';
      setState(prev => ({ ...prev, error: message, isLoading: false }));
      throw error;
    }
  }, [state.parameters, connectWebSocket]);

  // Run Agent-Based simulation
  const runAgentBased = useCallback(async (
    agentCount: number = 1000,
    duration: number = 12
  ) => {
    setState(prev => ({ 
      ...prev, 
      isLoading: true, 
      error: null, 
      progress: 0,
      simulationType: 'agent_based' 
    }));

    try {
      if (agentCount <= 100) {
        // Small agent count - run synchronously
        const result = await api.runAgentBased(state.parameters, agentCount, duration);
        setState(prev => ({ 
          ...prev, 
          agentBasedResult: result, 
          isLoading: false,
          progress: 100 
        }));
        return result;
      } else {
        // Large agent count - use WebSocket streaming
        const { jobId } = await api.startAgentBased(state.parameters, agentCount, duration);
        connectWebSocket(jobId);
      }
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Simulation failed';
      setState(prev => ({ ...prev, error: message, isLoading: false }));
      throw error;
    }
  }, [state.parameters, connectWebSocket]);

  // Cancel current simulation
  const cancelSimulation = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    setState(prev => ({ 
      ...prev, 
      isLoading: false, 
      progress: 0 
    }));
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  return {
    ...state,
    activeResult,
    updateParameter,
    updateParameters,
    resetParameters,
    loadPreset,
    setSimulationType,
    setSelectedPercentile,
    runDeterministic,
    runMonteCarlo,
    runAgentBased,
    cancelSimulation,
  };
}

export default useSimulation;



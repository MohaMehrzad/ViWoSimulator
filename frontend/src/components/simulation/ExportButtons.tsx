'use client';

import { useRef, useState, useCallback } from 'react';
import { SimulationParameters, SimulationResult, MonteCarloResult, AgentBasedResult, MonthlyProgressionResult } from '@/types/simulation';
import { exportToJsonClient, exportToCsvClient, importParameters, exportFullReportEnhanced } from '@/lib/export';

interface ExportButtonsProps {
  parameters: SimulationParameters;
  result: SimulationResult | MonteCarloResult | AgentBasedResult | MonthlyProgressionResult | null;
  onImportParameters: (params: Partial<SimulationParameters>) => void;
  // Enhanced props for comprehensive report
  monthlyProgressionResult?: MonthlyProgressionResult | null;
  monteCarloResult?: MonteCarloResult | null;
  agentBasedResult?: AgentBasedResult | null;
  // The base simulation result (deterministic)
  baseResult?: SimulationResult | null;
}

export function ExportButtons({ 
  parameters, 
  result, 
  onImportParameters,
  monthlyProgressionResult,
  monteCarloResult,
  agentBasedResult,
  baseResult,
}: ExportButtonsProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [isExporting, setIsExporting] = useState(false);
  const [exportError, setExportError] = useState<string | null>(null);

  const handleExportParameters = () => {
    const timestamp = new Date().toISOString().split('T')[0];
    exportToJsonClient(parameters, `viwo-parameters-${timestamp}`);
  };

  const handleExportResults = () => {
    if (!result) return;
    const timestamp = new Date().toISOString().split('T')[0];
    exportToJsonClient(result, `viwo-results-${timestamp}`);
  };

  /**
   * Enhanced full report export that includes:
   * - Executive summary with key KPIs
   * - Full parameters and results
   * - Monthly progression data
   * - Monte Carlo analysis
   * - Agent-based analysis
   * - Risk assessment
   * - Recommendations
   * - Industry benchmarks
   */
  const handleExportFullReport = useCallback(async () => {
    // Determine the best result to use
    const simulationResult = baseResult || result;
    
    if (!simulationResult) return;
    
    // Check if this is a SimulationResult (has totals property)
    const isSimulationResult = 'totals' in simulationResult;
    
    if (!isSimulationResult) {
      // Fallback to simple export for non-standard results
      const timestamp = new Date().toISOString().split('T')[0];
      const report = {
        metadata: {
          generated_at: new Date().toISOString(),
          simulator_version: '2.0.0',
          protocol: 'ViWO Token Economy',
        },
        parameters,
        results: simulationResult,
      };
      exportToJsonClient(report, `viwo-full-report-${timestamp}`);
      return;
    }

    setIsExporting(true);
    setExportError(null);

    try {
      await exportFullReportEnhanced({
        parameters,
        results: simulationResult as SimulationResult,
        monthlyProgression: monthlyProgressionResult || null,
        monteCarloResult: monteCarloResult || null,
        agentBasedResult: agentBasedResult || null,
      });
    } catch (error) {
      console.error('Full report export failed:', error);
      const errorMessage = error instanceof Error ? error.message : 'Export failed';
      setExportError(errorMessage);
      
      // Fallback to client-side export
      console.log('Falling back to client-side export...');
      const timestamp = new Date().toISOString().split('T')[0];
      const report = {
        metadata: {
          generated_at: new Date().toISOString(),
          simulator_version: '2.0.0',
          protocol: 'ViWO Token Economy',
          note: 'Client-side fallback export - some enhanced features may be missing',
        },
        parameters,
        results: simulationResult,
        monthlyProgression: monthlyProgressionResult || null,
      };
      exportToJsonClient(report, `viwo-full-report-${timestamp}`);
    } finally {
      setIsExporting(false);
    }
  }, [parameters, result, baseResult, monthlyProgressionResult, monteCarloResult, agentBasedResult]);

  const handleExportCsv = () => {
    if (!result) return;
    const timestamp = new Date().toISOString().split('T')[0];
    exportToCsvClient(result, `viwo-results-${timestamp}`);
  };

  const handleImport = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    try {
      const params = await importParameters(file);
      onImportParameters(params);
    } catch (error) {
      console.error('Import failed:', error);
      alert('Failed to import parameters. Please check the file format.');
    }

    // Reset file input
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  // Determine if we have enhanced data available
  const hasEnhancedData = monthlyProgressionResult || monteCarloResult || agentBasedResult;

  return (
    <div className="flex flex-wrap gap-3 pt-4 border-t border-gray-600">
      <button
        onClick={handleExportParameters}
        className="px-4 py-2 rounded-lg font-semibold text-sm bg-emerald-600 text-white 
                   hover:bg-emerald-700 transition-colors flex items-center gap-2"
      >
        📥 Export Parameters
      </button>
      
      <button
        onClick={() => fileInputRef.current?.click()}
        className="px-4 py-2 rounded-lg font-semibold text-sm bg-blue-600 text-white 
                   hover:bg-blue-700 transition-colors flex items-center gap-2"
      >
        📤 Import Parameters
      </button>
      
      <input
        ref={fileInputRef}
        type="file"
        accept=".json"
        onChange={handleImport}
        className="hidden"
      />
      
      <button
        onClick={handleExportResults}
        disabled={!result}
        className="px-4 py-2 rounded-lg font-semibold text-sm bg-purple-600 text-white 
                   hover:bg-purple-700 transition-colors flex items-center gap-2
                   disabled:opacity-50 disabled:cursor-not-allowed"
      >
        📊 Export Results (JSON)
      </button>
      
      <button
        onClick={handleExportCsv}
        disabled={!result}
        className="px-4 py-2 rounded-lg font-semibold text-sm bg-cyan-600 text-white 
                   hover:bg-cyan-700 transition-colors flex items-center gap-2
                   disabled:opacity-50 disabled:cursor-not-allowed"
      >
        📋 Export Results (CSV)
      </button>
      
      <button
        onClick={handleExportFullReport}
        disabled={!result || isExporting}
        className={`px-4 py-2 rounded-lg font-semibold text-sm text-white 
                   transition-colors flex items-center gap-2
                   disabled:opacity-50 disabled:cursor-not-allowed
                   ${hasEnhancedData 
                     ? 'bg-gradient-to-r from-amber-500 to-orange-600 hover:from-amber-600 hover:to-orange-700' 
                     : 'bg-amber-600 hover:bg-amber-700'}`}
        title={hasEnhancedData 
          ? 'Export comprehensive report with all simulation data, summaries, and analysis' 
          : 'Export full report with parameters and results'}
      >
        {isExporting ? (
          <>
            <span className="animate-spin">⏳</span> Generating...
          </>
        ) : (
          <>
            📑 {hasEnhancedData ? 'Export Comprehensive Report' : 'Export Full Report'}
          </>
        )}
      </button>
      
      {exportError && (
        <div className="w-full mt-2 p-2 bg-red-900/50 border border-red-700 rounded text-red-200 text-sm">
          ⚠️ {exportError} - Using fallback export
        </div>
      )}
      
      {hasEnhancedData && (
        <div className="w-full mt-2 text-xs text-gray-400">
          📊 Enhanced report includes: 
          {monthlyProgressionResult && ' Monthly Progression •'}
          {monteCarloResult && ' Monte Carlo Analysis •'}
          {agentBasedResult && ' Agent-Based Analysis •'}
          {' Risk Assessment • Industry Benchmarks • Recommendations'}
        </div>
      )}
    </div>
  );
}



'use client';

import { useRef } from 'react';
import { SimulationParameters, SimulationResult, MonteCarloResult, AgentBasedResult, MonthlyProgressionResult } from '@/types/simulation';
import { exportToJsonClient, exportToCsvClient, importParameters } from '@/lib/export';

interface ExportButtonsProps {
  parameters: SimulationParameters;
  result: SimulationResult | MonteCarloResult | AgentBasedResult | MonthlyProgressionResult | null;
  onImportParameters: (params: Partial<SimulationParameters>) => void;
}

export function ExportButtons({ parameters, result, onImportParameters }: ExportButtonsProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleExportParameters = () => {
    const timestamp = new Date().toISOString().split('T')[0];
    exportToJsonClient(parameters, `viwo-parameters-${timestamp}`);
  };

  const handleExportResults = () => {
    if (!result) return;
    const timestamp = new Date().toISOString().split('T')[0];
    exportToJsonClient(result, `viwo-results-${timestamp}`);
  };

  const handleExportFullReport = () => {
    if (!result) return;
    const timestamp = new Date().toISOString().split('T')[0];
    const report = {
      metadata: {
        generated_at: new Date().toISOString(),
        simulator_version: '1.0.0',
        protocol: 'ViWO Token Economy',
      },
      parameters,
      results: result,
    };
    exportToJsonClient(report, `viwo-full-report-${timestamp}`);
  };

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
        disabled={!result}
        className="px-4 py-2 rounded-lg font-semibold text-sm bg-amber-600 text-white 
                   hover:bg-amber-700 transition-colors flex items-center gap-2
                   disabled:opacity-50 disabled:cursor-not-allowed"
      >
        📑 Export Full Report
      </button>
    </div>
  );
}



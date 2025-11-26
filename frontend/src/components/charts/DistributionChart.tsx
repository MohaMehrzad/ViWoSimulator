'use client';

import { 
  AreaChart, 
  Area, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  ReferenceLine 
} from 'recharts';
import { formatCurrency, formatNumber } from '@/lib/utils';

interface DistributionChartProps {
  data: number[];
  label: string;
  color: string;
  mean?: number;
  formatValue?: (value: number) => string;
}

export function DistributionChart({ 
  data, 
  label, 
  color, 
  mean,
  formatValue = formatNumber 
}: DistributionChartProps) {
  // Create histogram bins
  const sortedData = [...data].sort((a, b) => a - b);
  const min = sortedData[0];
  const max = sortedData[sortedData.length - 1];
  const binCount = 20;
  const binWidth = (max - min) / binCount || 1;
  
  const bins: { range: string; count: number; value: number }[] = [];
  for (let i = 0; i < binCount; i++) {
    const binStart = min + i * binWidth;
    const binEnd = binStart + binWidth;
    const count = data.filter(v => v >= binStart && v < binEnd).length;
    bins.push({
      range: formatValue(binStart),
      count,
      value: binStart + binWidth / 2,
    });
  }

  return (
    <div className="h-64">
      <div className="text-sm font-semibold text-gray-700 mb-2">{label} Distribution</div>
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={bins} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis 
            dataKey="range" 
            tick={{ fontSize: 10 }}
            interval="preserveStartEnd"
          />
          <YAxis 
            tick={{ fontSize: 10 }}
            label={{ value: 'Frequency', angle: -90, position: 'insideLeft', fontSize: 10 }}
          />
          <Tooltip 
            formatter={(value: number, name: string) => [value, 'Count']}
            labelFormatter={(label) => `Value: ${label}`}
            contentStyle={{ 
              backgroundColor: '#fff', 
              border: '1px solid #e5e7eb',
              borderRadius: '8px',
              fontSize: '12px',
            }}
          />
          <Area 
            type="monotone" 
            dataKey="count" 
            stroke={color} 
            fill={color} 
            fillOpacity={0.3} 
          />
          {mean !== undefined && (
            <ReferenceLine 
              x={formatValue(mean)} 
              stroke="#ef4444" 
              strokeDasharray="5 5"
              label={{ value: 'Mean', position: 'top', fontSize: 10 }}
            />
          )}
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}



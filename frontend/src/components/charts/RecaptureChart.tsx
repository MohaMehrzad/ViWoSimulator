'use client';

import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';
import { RecaptureResult } from '@/types/simulation';
import { formatNumber } from '@/lib/utils';

interface RecaptureChartProps {
  recapture: RecaptureResult;
  monthlyEmission: number;
}

const COLORS = {
  burns: '#ef4444',
  buybacks: '#a855f7',
  staking: '#3b82f6',
  treasury: '#f59e0b',
  circulation: '#6b7280',
};

export function RecaptureChart({ recapture, monthlyEmission }: RecaptureChartProps) {
  const netCirculation = monthlyEmission - recapture.totalRecaptured;
  
  const data = [
    { name: 'Burns', value: recapture.burns, color: COLORS.burns },
    { name: 'Buybacks', value: recapture.buybacks, color: COLORS.buybacks },
    { name: 'Staking', value: recapture.staking, color: COLORS.staking },
    { name: 'Treasury', value: recapture.treasury, color: COLORS.treasury },
    { name: 'Net Circulation', value: netCirculation, color: COLORS.circulation },
  ].filter(d => d.value > 0);

  return (
    <div className="h-80">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            labelLine={false}
            label={({ name, percent }) => `${name} ${(percent * 100).toFixed(1)}%`}
            outerRadius={100}
            fill="#8884d8"
            dataKey="value"
          >
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} />
            ))}
          </Pie>
          <Tooltip 
            formatter={(value: number) => formatNumber(value) + ' VCoin'}
          />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}





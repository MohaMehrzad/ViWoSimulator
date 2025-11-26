'use client';

import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { SimulationResult } from '@/types/simulation';
import { formatCurrency } from '@/lib/utils';

interface RevenueChartProps {
  result: SimulationResult;
}

export function RevenueChart({ result }: RevenueChartProps) {
  const data = [
    {
      name: 'Identity',
      revenue: result.identity.revenue,
      costs: result.identity.costs,
      profit: result.identity.profit,
      color: '#8b5cf6',
    },
    {
      name: 'Content',
      revenue: result.content.revenue,
      costs: result.content.costs,
      profit: result.content.profit,
      color: '#ec4899',
    },
    {
      name: 'Community',
      revenue: result.community.revenue,
      costs: result.community.costs,
      profit: result.community.profit,
      color: '#10b981',
    },
    {
      name: 'Advertising',
      revenue: result.advertising.revenue,
      costs: result.advertising.costs,
      profit: result.advertising.profit,
      color: '#3b82f6',
    },
    {
      name: 'Messaging',
      revenue: result.messaging.revenue,
      costs: result.messaging.costs,
      profit: result.messaging.profit,
      color: '#06b6d4',
    },
  ];

  return (
    <div className="h-80">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          data={data}
          margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis dataKey="name" tick={{ fontSize: 12 }} />
          <YAxis 
            tickFormatter={(value) => formatCurrency(value)} 
            tick={{ fontSize: 12 }}
          />
          <Tooltip 
            formatter={(value: number) => formatCurrency(value)}
            contentStyle={{ 
              backgroundColor: '#fff', 
              border: '1px solid #e5e7eb',
              borderRadius: '8px',
            }}
          />
          <Legend />
          <Bar dataKey="revenue" fill="#10b981" name="Revenue" radius={[4, 4, 0, 0]} />
          <Bar dataKey="costs" fill="#f59e0b" name="Costs" radius={[4, 4, 0, 0]} />
          <Bar dataKey="profit" fill="#3b82f6" name="Profit" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}



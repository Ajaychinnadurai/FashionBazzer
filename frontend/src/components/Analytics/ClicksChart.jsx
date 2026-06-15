import React from 'react';
import {
  PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend,
} from 'recharts';

const COLORS = ['#FF3CAC', '#784BA0', '#2B86C5', '#00D4AA', '#FFB800', '#FF6B6B'];

const RADIAN = Math.PI / 180;
function CustomLabel({ cx, cy, midAngle, innerRadius, outerRadius, percent }) {
  const radius = innerRadius + (outerRadius - innerRadius) * 0.5;
  const x = cx + radius * Math.cos(-midAngle * RADIAN);
  const y = cy + radius * Math.sin(-midAngle * RADIAN);

  return (
    <text x={x} y={y} fill="white" textAnchor={x > cx ? 'start' : 'end'} dominantBaseline="central" fontSize={11} fontWeight={600}>
      {`${(percent * 100).toFixed(0)}%`}
    </text>
  );
}

function CustomTooltip({ active, payload }) {
  if (active && payload && payload.length) {
    return (
      <div style={{
        background: '#1A1A2E',
        border: '1px solid rgba(255,255,255,0.1)',
        borderRadius: 12,
        padding: '12px 16px',
      }}>
        <p style={{ color: payload[0].payload.color || '#fff', fontWeight: 600 }}>
          {payload[0].name}
        </p>
        <p style={{ color: '#fff', fontSize: '1.1rem', fontWeight: 700 }}>
          {payload[0].value.toLocaleString()} clicks
        </p>
      </div>
    );
  }
  return null;
}

export default function ClicksChart({ data = [] }) {
  if (data.length === 0) {
    return (
      <div className="glass-card" style={{ padding: '24px' }}>
        <h3 className="section-title">
          <span className="icon">👆</span> Clicks by Platform
        </h3>
        <div style={{
          height: 320,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: 'var(--text-muted)',
          flexDirection: 'column',
          gap: 8,
        }}>
          <span style={{ fontSize: '2rem' }}>📊</span>
          <p>No click data yet. Start posting products to see analytics here.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="glass-card" style={{ padding: '24px' }}>
      <h3 className="section-title">
        <span className="icon">👆</span> Clicks by Platform
      </h3>

      <ResponsiveContainer width="100%" height={320}>
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            labelLine={false}
            label={<CustomLabel />}
            outerRadius={120}
            innerRadius={60}
            dataKey="value"
            stroke="none"
          >
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip content={<CustomTooltip />} />
          <Legend
            verticalAlign="bottom"
            height={36}
            formatter={(value) => <span style={{ color: '#B0B0C0', fontSize: '0.8rem' }}>{value}</span>}
          />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}

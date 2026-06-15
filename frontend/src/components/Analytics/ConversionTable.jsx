import React from 'react';

export default function ConversionTable({ data = [] }) {
  // data should be an array of top products from the backend API
  // Each item: { product_name, platform, clicks, conversions, earnings }

  const isEmpty = data.length === 0;

  return (
    <div className="glass-card" style={{ padding: '24px', overflow: 'hidden' }}>
      <h3 className="section-title">
        <span className="icon">🛒</span> Top Products by Clicks
      </h3>

      {isEmpty ? (
        <div style={{
          padding: '40px 20px',
          textAlign: 'center',
          color: 'var(--text-muted)',
        }}>
          <div style={{ fontSize: '2rem', marginBottom: 8 }}>📊</div>
          <p>No click data yet. Start posting products to see performance here.</p>
        </div>
      ) : (
        <div style={{ overflowX: 'auto' }}>
          <table style={{
            width: '100%',
            borderCollapse: 'collapse',
            fontSize: '0.85rem',
          }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--border)' }}>
                <th style={{ padding: '12px 8px', textAlign: 'left', color: 'var(--text-muted)', fontWeight: 500 }}>Product</th>
                <th style={{ padding: '12px 8px', textAlign: 'left', color: 'var(--text-muted)', fontWeight: 500 }}>Platform</th>
                <th style={{ padding: '12px 8px', textAlign: 'right', color: 'var(--text-muted)', fontWeight: 500 }}>Clicks</th>
                <th style={{ padding: '12px 8px', textAlign: 'right', color: 'var(--text-muted)', fontWeight: 500 }}>Conversions</th>
                <th style={{ padding: '12px 8px', textAlign: 'right', color: 'var(--text-muted)', fontWeight: 500 }}>Rate</th>
                <th style={{ padding: '12px 8px', textAlign: 'right', color: 'var(--text-muted)', fontWeight: 500 }}>Earnings</th>
              </tr>
            </thead>
            <tbody>
              {data.map((row, i) => {
                const convRate = row.clicks > 0
                  ? ((row.conversions || 0) / row.clicks * 100).toFixed(2)
                  : '0.00';
                return (
                  <tr key={i} style={{
                    borderBottom: '1px solid var(--border)',
                    transition: 'var(--transition)',
                  }}
                    onMouseEnter={(e) => e.currentTarget.style.background = 'rgba(255,255,255,0.03)'}
                    onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
                  >
                    <td style={{ padding: '12px 8px', fontWeight: 500, maxWidth: 250, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                      {row.product_name || 'Unknown'}
                    </td>
                    <td style={{ padding: '12px 8px', color: 'var(--text-muted)' }}>{row.platform || '-'}</td>
                    <td style={{ padding: '12px 8px', textAlign: 'right' }}>{(row.clicks || 0).toLocaleString()}</td>
                    <td style={{ padding: '12px 8px', textAlign: 'right' }}>{row.conversions || 0}</td>
                    <td style={{ padding: '12px 8px', textAlign: 'right' }}>
                      <span className="tag tag-success">{convRate}%</span>
                    </td>
                    <td style={{ padding: '12px 8px', textAlign: 'right', fontWeight: 600, color: 'var(--success)' }}>
                      ₹{Number(row.earnings || 0).toLocaleString()}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

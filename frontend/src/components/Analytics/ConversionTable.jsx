import React from 'react';
import { FiTrendingUp, FiTrendingDown } from 'react-icons/fi';

export default function ConversionTable({ data = [] }) {
  if (data.length === 0) {
    data = [
      { product: 'Trendy Co-ord Set', platform: 'Meesho', clicks: 1245, conversions: 37, rate: 2.97, revenue: '₹1,482' },
      { product: 'Bodycon Mini Dress', platform: 'Amazon', clicks: 892, conversions: 24, rate: 2.69, revenue: '₹1,076' },
      { product: 'Maxi Dress - Summer', platform: 'Meesho', clicks: 2156, conversions: 52, rate: 2.41, revenue: '₹1,554' },
      { product: 'Indo-Western Fusion', platform: 'Flipkart', clicks: 654, conversions: 21, rate: 3.21, revenue: '₹1,467' },
      { product: 'Cut-out Party Dress', platform: 'Amazon', clicks: 423, conversions: 15, rate: 3.55, revenue: '₹1,048' },
    ];
  }

  return (
    <div className="glass-card" style={{ padding: '24px', overflow: 'hidden' }}>
      <h3 className="section-title">
        <span className="icon">🛒</span> Top Converting Products
      </h3>

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
              <th style={{ padding: '12px 8px', textAlign: 'right', color: 'var(--text-muted)', fontWeight: 500 }}>Conv.</th>
              <th style={{ padding: '12px 8px', textAlign: 'right', color: 'var(--text-muted)', fontWeight: 500 }}>Rate</th>
              <th style={{ padding: '12px 8px', textAlign: 'right', color: 'var(--text-muted)', fontWeight: 500 }}>Revenue</th>
            </tr>
          </thead>
          <tbody>
            {data.map((row, i) => (
              <tr key={i} style={{
                borderBottom: '1px solid var(--border)',
                transition: 'var(--transition)',
              }}
                onMouseEnter={(e) => e.currentTarget.style.background = 'rgba(255,255,255,0.03)'}
                onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
              >
                <td style={{ padding: '12px 8px', fontWeight: 500 }}>{row.product}</td>
                <td style={{ padding: '12px 8px', color: 'var(--text-muted)' }}>{row.platform}</td>
                <td style={{ padding: '12px 8px', textAlign: 'right' }}>{row.clicks.toLocaleString()}</td>
                <td style={{ padding: '12px 8px', textAlign: 'right' }}>{row.conversions}</td>
                <td style={{ padding: '12px 8px', textAlign: 'right' }}>
                  <span className="tag tag-success">{row.rate}%</span>
                </td>
                <td style={{ padding: '12px 8px', textAlign: 'right', fontWeight: 600, color: 'var(--success)' }}>
                  {row.revenue}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

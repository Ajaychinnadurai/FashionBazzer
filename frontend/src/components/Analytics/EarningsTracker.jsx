import React from 'react';

export default function EarningsTracker({ data = [] }) {
  if (data.length === 0) {
    data = [
      { platform: 'Meesho', amount: 2450, status: 'approved' },
      { platform: 'Amazon', amount: 1800, status: 'pending' },
      { platform: 'Flipkart', amount: 960, status: 'approved' },
      { platform: 'Cuelinks', amount: 340, status: 'pending' },
    ];
  }

  const total = data.reduce((sum, item) => sum + item.amount, 0);
  const approved = data.filter(d => d.status === 'approved').reduce((sum, item) => sum + item.amount, 0);

  return (
    <div className="glass-card" style={{ padding: '24px' }}>
      <h3 className="section-title">
        <span className="icon">💰</span> Earnings Overview
      </h3>

      <div style={{
        display: 'flex',
        gap: 24,
        marginBottom: 20,
        flexWrap: 'wrap',
      }}>
        <div>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: 4 }}>Total Earnings</div>
          <div style={{ fontSize: '2rem', fontWeight: 800, background: 'var(--gradient)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
            ₹{total.toLocaleString()}
          </div>
        </div>
        <div>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: 4 }}>Approved</div>
          <div style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--success)' }}>
            ₹{approved.toLocaleString()}
          </div>
        </div>
        <div>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: 4 }}>Pending</div>
          <div style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--warning)' }}>
            ₹{(total - approved).toLocaleString()}
          </div>
        </div>
      </div>

      {/* Progress bar */}
      <div style={{
        height: 8,
        background: 'rgba(255,255,255,0.06)',
        borderRadius: 4,
        overflow: 'hidden',
        marginBottom: 20,
      }}>
        <div style={{
          height: '100%',
          width: `${total > 0 ? (approved / total) * 100 : 0}%`,
          background: 'var(--gradient)',
          borderRadius: 4,
          transition: 'width 1s ease',
        }} />
      </div>

      {/* Platform breakdown */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
        {data.map((item, i) => (
          <div key={i} style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            padding: '10px 12px',
            borderRadius: 8,
            background: 'rgba(255,255,255,0.03)',
            border: '1px solid var(--border)',
          }}>
            <span style={{ fontWeight: 500, fontSize: '0.9rem' }}>{item.platform}</span>
            <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
              <span style={{ fontWeight: 700, color: 'var(--success)' }}>
                ₹{item.amount.toLocaleString()}
              </span>
              <span className={`tag ${item.status === 'approved' ? 'tag-success' : 'tag-warning'}`}
                style={{ fontSize: '0.65rem' }}>
                {item.status}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

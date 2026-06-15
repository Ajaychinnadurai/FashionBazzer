import React from 'react';

export default function EarningsTracker({ data = [] }) {
  // data should be an array from /analytics/earnings/
  // Each item: { platform, total_earnings, pending, approved, transactions }

  const isEmpty = data.length === 0;

  const total = data.reduce((sum, item) => sum + Number(item.total_earnings || 0), 0);
  const approved = data.reduce((sum, item) => sum + Number(item.approved || 0), 0);
  const pending = data.reduce((sum, item) => sum + Number(item.pending || 0), 0);

  return (
    <div className="glass-card" style={{ padding: '24px' }}>
      <h3 className="section-title">
        <span className="icon">💰</span> Earnings Overview
      </h3>

      {isEmpty ? (
        <div style={{
          padding: '40px 20px',
          textAlign: 'center',
          color: 'var(--text-muted)',
        }}>
          <div style={{ fontSize: '2rem', marginBottom: 8 }}>💸</div>
          <p>No earnings data yet. Commissions will appear here when your affiliate links generate sales.</p>
        </div>
      ) : (
        <>
          <div style={{
            display: 'flex',
            gap: 24,
            marginBottom: 20,
            flexWrap: 'wrap',
          }}>
            <div>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: 4 }}>Total Earnings</div>
              <div style={{ fontSize: '2rem', fontWeight: 800, background: 'var(--gradient)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
                ₹{total.toLocaleString('en-IN', { maximumFractionDigits: 2 })}
              </div>
            </div>
            <div>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: 4 }}>Approved</div>
              <div style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--success)' }}>
                ₹{approved.toLocaleString('en-IN', { maximumFractionDigits: 2 })}
              </div>
            </div>
            <div>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: 4 }}>Pending</div>
              <div style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--warning)' }}>
                ₹{pending.toLocaleString('en-IN', { maximumFractionDigits: 2 })}
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
                <span style={{ fontWeight: 500, fontSize: '0.9rem', textTransform: 'capitalize' }}>
                  {item.platform || 'Unknown'}
                </span>
                <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                  <span style={{ fontWeight: 700, color: 'var(--success)' }}>
                    ₹{Number(item.total_earnings || 0).toLocaleString('en-IN', { maximumFractionDigits: 2 })}
                  </span>
                  <span className={`tag ${Number(item.approved || 0) > 0 ? 'tag-success' : 'tag-warning'}`}
                    style={{ fontSize: '0.65rem' }}>
                    {(Number(item.approved || 0) > 0) ? 'Approved' : 'Pending'}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}

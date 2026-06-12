import React from 'react';
import { FiCheckCircle, FiXCircle, FiClock } from 'react-icons/fi';

export default function PostHistory() {
  const [history, setHistory] = React.useState([]);

  React.useEffect(() => {
    setHistory(getDemoHistory());
  }, []);

  return (
    <div>
      {history.length === 0 ? (
        <div className="empty-state">
          <div className="emoji">📜</div>
          <h3>No post history yet</h3>
          <p>Published posts will appear here.</p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
          {history.map((item, i) => (
            <div key={i} className="glass-card" style={{
              padding: '12px 16px',
              display: 'flex',
              alignItems: 'center',
              gap: 12,
            }}>
              <span style={{ fontSize: '1.2rem' }}>
                {item.status === 'success' ? '✅' : item.status === 'failed' ? '❌' : '⏳'}
              </span>
              <div style={{ flex: 1 }}>
                <div style={{ fontSize: '0.85rem', fontWeight: 500 }}>
                  {item.platform} → {item.product_name || 'Product'}
                </div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                  {new Date(item.posted_at).toLocaleString('en-IN')}
                </div>
              </div>
              <span className={`tag ${item.status === 'success' ? 'tag-success' : item.status === 'failed' ? 'tag-error' : 'tag-warning'}`}>
                {item.status}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function getDemoHistory() {
  const now = Date.now();
  return [
    { platform: 'Telegram', product_name: 'Co-ord Set', status: 'success', posted_at: now - 3600000 },
    { platform: 'Instagram', product_name: 'Bodycon Dress', status: 'success', posted_at: now - 7200000 },
    { platform: 'Facebook', product_name: 'Maxi Dress', status: 'failed', posted_at: now - 14400000 },
    { platform: 'Pinterest', product_name: 'Cut-out Dress', status: 'success', posted_at: now - 21600000 },
  ];
}

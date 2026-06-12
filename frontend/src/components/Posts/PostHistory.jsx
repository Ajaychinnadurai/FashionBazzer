import React from 'react';
import api from '../../services/api';

export default function PostHistory() {
  const [history, setHistory] = React.useState([]);

  React.useEffect(() => {
    fetchHistory();
  }, []);

  async function fetchHistory() {
    try {
      const res = await api.get('/dashboard/overview/');
      setHistory(res.data.recent_posts || []);
    } catch {
      setHistory([]);
    }
  }

  return (
    <div>
      {history.length === 0 ? (
        <div className="empty-state">
          <div className="emoji">📜</div>
          <h3>No post history yet</h3>
          <p>Published posts will appear here once the scheduler starts posting.</p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
          {history.map((item, i) => (
            <div key={item.id || i} className="glass-card" style={{
              padding: '12px 16px',
              display: 'flex',
              alignItems: 'center',
              gap: 12,
            }}>
              <span style={{ fontSize: '1.2rem' }}>
                {item.status === 'published' ? '✅' : item.status === 'failed' ? '❌' : '⏳'}
              </span>
              <div style={{ flex: 1 }}>
                <div style={{ fontSize: '0.85rem', fontWeight: 500 }}>
                  {item.product_name || 'Product'}
                </div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                  {item.published_at
                    ? new Date(item.published_at).toLocaleString('en-IN')
                    : item.scheduled_time
                      ? `Scheduled: ${new Date(item.scheduled_time).toLocaleString('en-IN')}`
                      : ''}
                </div>
              </div>
              <span className={`tag ${item.status === 'published' ? 'tag-success' : item.status === 'failed' ? 'tag-error' : 'tag-warning'}`}>
                {item.status}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

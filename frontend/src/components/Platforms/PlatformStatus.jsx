import React from 'react';
import toast from 'react-hot-toast';
import api from '../../services/api';

const PLATFORM_INFO = {
  telegram: { name: 'Telegram', icon: '✈️', color: '#2AABEE' },
  instagram: { name: 'Instagram', icon: '📸', color: '#E4405F' },
  facebook: { name: 'Facebook', icon: '👍', color: '#1877F2' },
  pinterest: { name: 'Pinterest', icon: '📌', color: '#BD081C' },
  twitter: { name: 'Twitter/X', icon: '🐦', color: '#1DA1F2' },
  threads: { name: 'Threads', icon: '🧵', color: '#101010' },
};

export default function PlatformStatus() {
  const [platforms, setPlatforms] = React.useState([]);
  const [, setLoading] = React.useState(true);
  const [testing, setTesting] = React.useState(null);

  React.useEffect(() => {
    fetchStatus();
  }, []);

  async function fetchStatus() {
    try {
      const res = await api.get('/analytics/status/');
      setPlatforms(Array.isArray(res.data) ? res.data : []);
    } catch {
      setPlatforms(Object.keys(PLATFORM_INFO).map(key => ({
        platform: key,
        is_connected: false,
        error_message: 'API not configured',
      })));
    } finally {
      setLoading(false);
    }
  }

  async function testPlatform(platform) {
    setTesting(platform);
    try {
      const res = await api.post('/analytics/test/', { platform });
      toast.success(
        res.data.connected
          ? `${PLATFORM_INFO[platform]?.name} connected! ✅`
          : `${PLATFORM_INFO[platform]?.name}: ${res.data.error}`
      );
      fetchStatus();
    } catch (err) {
      toast.error(`Test failed for ${platform}`);
    } finally {
      setTesting(null);
    }
  }

  return (
    <div className="dashboard-grid" style={{ gridTemplateColumns: 'repeat(auto-fill, minmax(180px, 1fr))', padding: '0 24px' }}>
      {Object.entries(PLATFORM_INFO).map(([key, info]) => {
        const platform = platforms.find(p => p.platform === key);

        return (
          <div key={key} className="glass-card" style={{
            padding: '20px',
            textAlign: 'center',
            position: 'relative',
            overflow: 'hidden',
          }}>
            {/* Status indicator */}
            <div style={{
              position: 'absolute',
              top: 12,
              right: 12,
            }}>
              <span className={`status-dot ${platform?.is_connected ? 'active' : 'inactive'}`} />
            </div>

            <div style={{ fontSize: '2rem', marginBottom: 8 }}>{info.icon}</div>
            <h4 style={{ fontSize: '0.9rem', fontWeight: 600, marginBottom: 4 }}>{info.name}</h4>

            <span className={`tag ${platform?.is_connected ? 'tag-success' : 'tag-error'}`}
              style={{ fontSize: '0.7rem' }}>
              {platform?.is_connected ? 'Connected' : 'Disconnected'}
            </span>

            <button
              className="btn btn-secondary btn-sm"
              style={{ marginTop: 12, width: '100%' }}
              onClick={() => testPlatform(key)}
              disabled={testing === key}
            >
              {testing === key ? 'Testing...' : 'Test'}
            </button>
          </div>
        );
      })}
    </div>
  );
}

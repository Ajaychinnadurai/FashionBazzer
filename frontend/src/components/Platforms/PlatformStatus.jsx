import React from 'react';
import { useCallback } from 'react';
import toast from 'react-hot-toast';
import { FiRefreshCw } from 'react-icons/fi';
import api from '../../services/api';
import { usePolling } from '../../hooks/usePolling';
import { timeAgo } from '../../utils/formatters';

const PLATFORM_INFO = {
  telegram: { name: 'Telegram', icon: '✈️', color: '#2AABEE' },
  instagram: { name: 'Instagram', icon: '📸', color: '#E4405F' },
  facebook: { name: 'Facebook', icon: '👍', color: '#1877F2' },
  pinterest: { name: 'Pinterest', icon: '📌', color: '#BD081C' },
  twitter: { name: 'Twitter/X', icon: '🐦', color: '#1DA1F2' },
  threads: { name: 'Threads', icon: '🧵', color: '#101010' },
};

export default function PlatformStatus() {
  const [testing, setTesting] = React.useState(null);

  const fetchStatus = useCallback(() =>
    api.get('/analytics/status/').then(r => r.data), []);

  const {
    data: platforms,
    lastUpdated,
    refresh,
  } = usePolling(fetchStatus, 60000, true);

  const platformList = Array.isArray(platforms) ? platforms : [];

  async function testPlatform(platform) {
    setTesting(platform);
    try {
      const res = await api.post('/analytics/test/', { platform });
      toast.success(
        res.data.connected
          ? `${PLATFORM_INFO[platform]?.name} connected! ✅`
          : `${PLATFORM_INFO[platform]?.name}: ${res.data.error}`
      );
      refresh();
    } catch (err) {
      toast.error(`Test failed for ${platform}`);
    } finally {
      setTesting(null);
    }
  }

  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 16, padding: '0 24px' }}>
        <span className="live-indicator">
          <span className="live-dot" />
          Auto-checks every 30min
        </span>
        {lastUpdated && (
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
            Checked {timeAgo(lastUpdated)}
          </span>
        )}
        <button className="btn btn-secondary btn-sm" onClick={refresh} title="Refresh status">
          <FiRefreshCw size={12} />
        </button>
      </div>

      <div className="platform-status-grid">
        {Object.entries(PLATFORM_INFO).map(([key, info]) => {
          const platform = platformList.find(p => p.platform === key);
          const connected = platform?.is_connected ?? false;

          return (
            <div key={key} className={`platform-card glass-card ${connected ? 'connected' : 'disconnected'}`}>
              {/* Animated status bar */}
              <div className={`platform-status-bar ${connected ? 'connected' : 'disconnected'}`} />

              {/* Status indicator */}
              <div style={{ position: 'absolute', top: 12, right: 12 }}>
                <span className={`status-dot ${connected ? 'active' : 'inactive'}`} />
              </div>

              <div style={{ fontSize: '2rem', marginBottom: 8, lineHeight: 1 }}>{info.icon}</div>
              <h4 style={{ fontSize: '0.9rem', fontWeight: 600, marginBottom: 4 }}>{info.name}</h4>

              <span
                className={`tag ${connected ? 'tag-success' : 'tag-error'}`}
                style={{ fontSize: '0.7rem', transition: 'all 0.3s ease' }}
              >
                {connected ? '● Connected' : '○ Disconnected'}
              </span>

              {platform?.error_message && !connected && (
                <p style={{ fontSize: '0.65rem', color: 'var(--error)', marginTop: 6, lineHeight: 1.3, maxWidth: '100%', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                  {platform.error_message}
                </p>
              )}

              {platform?.last_checked && (
                <p style={{ fontSize: '0.6rem', color: 'var(--text-muted)', marginTop: 6 }}>
                  Last: {timeAgo(platform.last_checked)}
                </p>
              )}

              <button
                className="btn btn-secondary btn-sm"
                style={{ marginTop: 8, width: '100%' }}
                onClick={() => testPlatform(key)}
                disabled={testing === key}
              >
                {testing === key ? 'Testing...' : 'Test'}
              </button>
            </div>
          );
        })}
      </div>
    </div>
  );
}

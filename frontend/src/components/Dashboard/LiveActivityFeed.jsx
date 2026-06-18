import React, { useState, useEffect } from 'react';
import { FiClock, FiCheckCircle, FiXCircle, FiActivity } from 'react-icons/fi';
import { timeAgo } from '../../utils/formatters';

const PLATFORM_ICONS = {
  telegram: '✈️',
  instagram: '📸',
  facebook: '👍',
  pinterest: '📌',
  twitter: '🐦',
  threads: '🧵',
};

/**
 * Live activity feed showing recent post/log activity.
 */
export default function LiveActivityFeed({ posts = [], logs = [] }) {
  const [activities, setActivities] = useState([]);

  // Merge posts + logs into a single activity feed, sorted by time
  useEffect(() => {
    const items = [];

    (posts || []).forEach((p) => {
      items.push({
        id: `post-${p.id}`,
        type: 'post',
        status: p.status,
        message: p.product_name || `Product #${p.product}`,
        time: p.created_at || p.scheduled_time,
        platform: null,
      });
    });

    (logs || []).forEach((l) => {
      items.push({
        id: `log-${l.id}`,
        type: 'log',
        status: l.status || 'success',
        message: `${l.platform || ''} post ${l.status || 'completed'}`,
        time: l.posted_at || l.created_at,
        platform: l.platform,
      });
    });

    // Sort newest first, take top 15
    items.sort((a, b) => new Date(b.time || 0) - new Date(a.time || 0));
    setActivities(items.slice(0, 15));
  }, [posts, logs]);

  if (activities.length === 0) {
    return (
      <div className="glass-card" style={{ padding: '24px' }}>
        <h3 className="section-title">
          <span className="icon"><FiActivity size={18} /></span> Live Activity
        </h3>
        <div style={{ padding: '20px', textAlign: 'center', color: 'var(--text-muted)' }}>
          <div style={{ fontSize: '2rem', marginBottom: 8 }}>📡</div>
          <p>No recent activity. Start posting to see live updates here.</p>
        </div>
      </div>
    );
  }

  const getStatusColor = (status) => {
    if (status === 'published' || status === 'success') return 'var(--success)';
    if (status === 'failed') return 'var(--error)';
    return 'var(--warning)';
  };

  const getStatusIcon = (status) => {
    if (status === 'published' || status === 'success') return <FiCheckCircle size={14} />;
    if (status === 'failed') return <FiXCircle size={14} />;
    return <FiClock size={14} />;
  };

  return (
    <div className="glass-card" style={{ padding: '24px' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16 }}>
        <h3 className="section-title" style={{ marginBottom: 0 }}>
          <span className="icon"><FiActivity size={18} /></span> Live Activity
        </h3>
        <span
          className="live-indicator"
          style={{ fontSize: '0.75rem', color: 'var(--success)', display: 'flex', alignItems: 'center', gap: 6 }}
        >
          <span className="live-dot" />
          LIVE
        </span>
      </div>

      <div className="activity-feed">
        {activities.map((item, i) => (
          <div
            key={item.id}
            className="activity-item"
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 12,
              padding: '10px 0',
              borderBottom: i < activities.length - 1 ? '1px solid var(--border)' : 'none',
              opacity: 1,
              animation: `slideIn 0.4s ease-out ${i * 0.05}s both`,
            }}
          >
            {/* Platform icon or type */}
            <div className="activity-icon" style={{ fontSize: '1.2rem', minWidth: 28, textAlign: 'center' }}>
              {item.platform ? PLATFORM_ICONS[item.platform] || '📤' : '📄'}
            </div>

            {/* Status dot */}
            <div
              style={{
                width: 8,
                height: 8,
                borderRadius: '50%',
                background: getStatusColor(item.status),
                flexShrink: 0,
              }}
            />

            {/* Message */}
            <div style={{ flex: 1, minWidth: 0 }}>
              <div style={{ fontSize: '0.85rem', fontWeight: 500, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                {item.message}
              </div>
            </div>

            {/* Status badge */}
            <span
              className={`tag ${item.status === 'published' || item.status === 'success' ? 'tag-success' : item.status === 'failed' ? 'tag-error' : 'tag-warning'}`}
              style={{ fontSize: '0.65rem', flexShrink: 0 }}
            >
              {getStatusIcon(item.status)}
              {item.status}
            </span>

            {/* Time */}
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', minWidth: 55, textAlign: 'right', flexShrink: 0 }}>
              {timeAgo(item.time)}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

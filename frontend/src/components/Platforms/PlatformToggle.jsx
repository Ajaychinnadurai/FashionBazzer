import React from 'react';
import { FiToggleLeft, FiToggleRight } from 'react-icons/fi';

const PLATFORMS = [
  { id: 'telegram', name: 'Telegram', icon: '✈️', color: '#2AABEE' },
  { id: 'instagram', name: 'Instagram', icon: '📸', color: '#E4405F' },
  { id: 'facebook', name: 'Facebook', icon: '👍', color: '#1877F2' },
  { id: 'pinterest', name: 'Pinterest', icon: '📌', color: '#BD081C' },
  { id: 'twitter', name: 'Twitter/X', icon: '🐦', color: '#1DA1F2' },
  { id: 'threads', name: 'Threads', icon: '🧵', color: '#101010' },
];

export default function PlatformToggle() {
  const [enabled, setEnabled] = React.useState({
    telegram: true,
    instagram: true,
    facebook: true,
    pinterest: true,
    twitter: true,
    threads: false,
  });

  function toggle(platform) {
    setEnabled(prev => ({
      ...prev,
      [platform]: !prev[platform],
    }));
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
      {PLATFORMS.map((p) => (
        <div key={p.id} style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '12px 16px',
          borderRadius: 'var(--radius-sm)',
          background: 'rgba(255,255,255,0.03)',
          border: '1px solid var(--border)',
          cursor: 'pointer',
          transition: 'var(--transition)',
        }}
          onClick={() => toggle(p.id)}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <span style={{ fontSize: '1.2rem' }}>{p.icon}</span>
            <span style={{ fontWeight: 500 }}>{p.name}</span>
          </div>
          <div style={{ color: enabled[p.id] ? p.color : 'var(--text-muted)', fontSize: '1.3rem' }}>
            {enabled[p.id] ? <FiToggleRight /> : <FiToggleLeft />}
          </div>
        </div>
      ))}
    </div>
  );
}

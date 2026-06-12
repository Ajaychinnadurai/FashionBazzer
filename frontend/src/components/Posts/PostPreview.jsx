import React from 'react';

export default function PostPreview({ post, onClose }) {
  if (!post) return null;

  const platforms = [
    { key: 'telegram', label: 'Telegram', color: '#2AABEE', icon: '✈️' },
    { key: 'instagram', label: 'Instagram', color: '#E4405F', icon: '📸' },
    { key: 'facebook', label: 'Facebook', color: '#1877F2', icon: '👍' },
    { key: 'twitter', label: 'Twitter/X', color: '#1DA1F2', icon: '🐦' },
    { key: 'pinterest', label: 'Pinterest', color: '#BD081C', icon: '📌' },
  ];

  const captionKey = (p) => `${p}_caption`;

  return (
    <div style={{
      position: 'fixed',
      inset: 0,
      background: 'rgba(0,0,0,0.7)',
      backdropFilter: 'blur(8px)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1000,
      padding: 20,
    }} onClick={onClose}>
      <div className="glass-card" style={{
        maxWidth: 800,
        width: '100%',
        maxHeight: '90vh',
        overflow: 'auto',
        padding: 24,
      }} onClick={(e) => e.stopPropagation()}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          marginBottom: 20,
        }}>
          <h3 style={{ fontSize: '1.2rem', fontWeight: 600 }}>📱 Post Preview</h3>
          <button onClick={onClose} style={{
            background: 'none',
            border: 'none',
            color: 'var(--text-muted)',
            fontSize: '1.5rem',
            cursor: 'pointer',
          }}>✕</button>
        </div>

        {platforms.map((platform) => {
          const caption = post[captionKey(platform.key)];
          if (!caption) return null;

          return (
            <div key={platform.key} style={{
              marginBottom: 20,
              border: `1px solid ${platform.color}30`,
              borderRadius: 12,
              padding: 16,
              background: 'rgba(255,255,255,0.02)',
            }}>
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: 8,
                marginBottom: 12,
              }}>
                <span style={{ fontSize: '1.2rem' }}>{platform.icon}</span>
                <span style={{ color: platform.color, fontWeight: 600, fontSize: '0.9rem' }}>
                  {platform.label}
                </span>
              </div>
              <pre style={{
                whiteSpace: 'pre-wrap',
                fontFamily: 'Inter, sans-serif',
                fontSize: '0.85rem',
                lineHeight: 1.6,
                color: 'var(--text-secondary)',
                maxHeight: 200,
                overflow: 'auto',
              }}>
                {caption}
              </pre>
            </div>
          );
        })}
      </div>
    </div>
  );
}

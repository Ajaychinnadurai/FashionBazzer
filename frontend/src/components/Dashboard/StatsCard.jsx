import React from 'react';

export default function StatsCard({ title, value, change, subtitle, icon, color }) {
  const isPositive = change >= 0;

  return (
    <div className="glass-card" style={{
      padding: '24px',
      display: 'flex',
      flexDirection: 'column',
      gap: 4,
      position: 'relative',
      overflow: 'hidden',
    }}>
      {/* Background glow */}
      <div style={{
        position: 'absolute',
        top: -60,
        right: -60,
        width: 150,
        height: 150,
        borderRadius: '50%',
        background: `${color}15`,
        filter: 'blur(40px)',
      }} />

      <div style={{
        display: 'flex',
        alignItems: 'flex-start',
        justifyContent: 'space-between',
        marginBottom: 12,
      }}>
        <div style={{
          width: 44,
          height: 44,
          borderRadius: 12,
          background: `${color}20`,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: color,
        }}>
          {icon}
        </div>
        <span className={`tag ${isPositive ? 'tag-success' : 'tag-error'}`}>
          {isPositive ? '↑' : '↓'} {Math.abs(change)}%
        </span>
      </div>

      <h3 style={{
        fontSize: '0.8rem',
        color: 'var(--text-muted)',
        fontWeight: 500,
        textTransform: 'uppercase',
        letterSpacing: '0.5px',
      }}>
        {title}
      </h3>

      <p style={{
        fontSize: '1.8rem',
        fontWeight: 800,
        color: 'var(--text)',
        lineHeight: 1.2,
      }}>
        {value}
      </p>

      <span style={{
        fontSize: '0.8rem',
        color: 'var(--text-muted)',
        marginTop: 4,
      }}>
        {subtitle}
      </span>
    </div>
  );
}

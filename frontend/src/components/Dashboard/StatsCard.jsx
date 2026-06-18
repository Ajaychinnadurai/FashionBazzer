import React, { useState, useEffect, useRef } from 'react';

/**
 * Animated counter that counts up from 0 to the target value on mount/change.
 */
function AnimatedValue({ value, duration = 1200 }) {
  const [display, setDisplay] = useState(0);
  const prevRef = useRef(0);
  const rafRef = useRef(null);

  useEffect(() => {
    const target = typeof value === 'string'
      ? parseInt(value.replace(/[^0-9]/g, ''), 10) || 0
      : Number(value) || 0;
    const start = prevRef.current;
    const startTime = performance.now();

    function animate(now) {
      const elapsed = now - startTime;
      const progress = Math.min(elapsed / duration, 1);
      // ease-out cubic
      const eased = 1 - Math.pow(1 - progress, 3);
      const current = Math.round(start + (target - start) * eased);
      setDisplay(current);
      if (progress < 1) {
        rafRef.current = requestAnimationFrame(animate);
      } else {
        prevRef.current = target;
      }
    }

    rafRef.current = requestAnimationFrame(animate);
    return () => {
      if (rafRef.current) cancelAnimationFrame(rafRef.current);
    };
  }, [value, duration]);

  // Extract prefix/suffix from formatted strings like "₹12,345" for display
  let prefix = '';
  let suffix = '';

  if (typeof value === 'string') {
    const match = value.match(/^([^0-9]*)([0-9,]+)(.*)$/);
    if (match) {
      prefix = match[1];
      suffix = match[3];
    }
  }

  return <>{prefix}{(display || 0).toLocaleString('en-IN')}{suffix}</>;
}

/**
 * Mini sparkline bar showing trend data.
 */
function Sparkline({ data = [], color = '#FF3CAC', height = 32 }) {
  if (data.length === 0) return null;
  const max = Math.max(...data, 1);
  const width = data.length * 8; // 8px per bar

  return (
    <svg width={width} height={height} style={{ display: 'block' }}>
      {data.map((val, i) => {
        const barH = Math.max((val / max) * height, 2);
        return (
          <rect
            key={i}
            x={i * 8}
            y={height - barH}
            width={5}
            height={barH}
            rx={2}
            fill={color}
            opacity={0.6}
          >
            <animate
              attributeName="height"
              from="0"
              to={barH}
              dur="0.5s"
              begin={`${i * 0.08}s`}
              fill="freeze"
            />
            <animate
              attributeName="y"
              from={height}
              to={height - barH}
              dur="0.5s"
              begin={`${i * 0.08}s`}
              fill="freeze"
            />
          </rect>
        );
      })}
    </svg>
  );
}

/**
 * Enhanced StatsCard with animated counter + optional sparkline.
 */
export default function StatsCard({
  title,
  value,
  change,
  subtitle,
  icon,
  color,
  sparklineData,
}) {
  const isPositive = change >= 0;

  return (
    <div
      className="glass-card stats-card"
      style={{
        padding: '24px',
        display: 'flex',
        flexDirection: 'column',
        gap: 4,
        position: 'relative',
        overflow: 'hidden',
      }}
    >
      {/* Background glow */}
      <div
        style={{
          position: 'absolute',
          top: -60,
          right: -60,
          width: 150,
          height: 150,
          borderRadius: '50%',
          background: `${color}15`,
          filter: 'blur(40px)',
          transition: 'transform 0.6s ease',
        }}
        className="stats-glow"
      />

      {/* Top row: icon + change badge */}
      <div
        style={{
          display: 'flex',
          alignItems: 'flex-start',
          justifyContent: 'space-between',
          marginBottom: 12,
        }}
      >
        <div
          className="stats-icon-box"
          style={{
            width: 44,
            height: 44,
            borderRadius: 12,
            background: `${color}20`,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color,
          }}
        >
          {icon}
        </div>
        <span
          className={`tag ${isPositive ? 'tag-success' : 'tag-error'} stats-change-badge`}
        >
          {isPositive ? '↑' : '↓'} {Math.abs(change)}%
        </span>
      </div>

      {/* Sparkline (mini trend chart) */}
      {sparklineData && sparklineData.length > 0 && (
        <div style={{ marginBottom: 8 }}>
          <Sparkline data={sparklineData} color={color} />
        </div>
      )}

      {/* Title */}
      <h3
        style={{
          fontSize: '0.8rem',
          color: 'var(--text-muted)',
          fontWeight: 500,
          textTransform: 'uppercase',
          letterSpacing: '0.5px',
        }}
      >
        {title}
      </h3>

      {/* Value with animation */}
      <p
        className="stats-value"
        style={{
          fontSize: '1.8rem',
          fontWeight: 800,
          color: 'var(--text)',
          lineHeight: 1.2,
        }}
      >
        <AnimatedValue value={value} />
      </p>

      {/* Subtitle */}
      <span
        style={{
          fontSize: '0.8rem',
          color: 'var(--text-muted)',
          marginTop: 4,
        }}
      >
        {subtitle}
      </span>
    </div>
  );
}

import React from 'react';

const STYLE_COLORS = {
  excited: '#FF3CAC',
  informative: '#2B86C5',
  urgency: '#FF4757',
  social_proof: '#00D4AA',
  lifestyle: '#784BA0',
  discount: '#FFB800',
  trendy: '#FF6B6B',
  question: '#54A0FF',
  storytelling: '#5F27CD',
  seasonal: '#01A3A4',
  comparison: '#E84393',
  challenge: '#FDCB6E',
};

const STYLE_EMOJIS = {
  excited: '🔥',
  informative: '📊',
  urgency: '⏰',
  social_proof: '⭐',
  lifestyle: '✨',
  discount: '💸',
  trendy: '💅',
  question: '🤔',
  storytelling: '📖',
  seasonal: '☀️',
  comparison: '⚖️',
  challenge: '🎯',
};

const PLATFORM_EMOJIS = {
  telegram: '✈️',
  instagram: '📸',
  facebook: '👍',
  pinterest: '📌',
  twitter: '🐦',
  threads: '🧵',
};

function getMaxClicks(data) {
  let max = 0;
  data.forEach((item) => {
    Object.values(item.platforms || {}).forEach((v) => {
      if (v > max) max = v;
    });
  });
  return max || 1;
}

function getMaxClicksPerPost(data) {
  let max = 0;
  data.forEach((item) => {
    if (item.clicks_per_post > max) max = item.clicks_per_post;
  });
  return max || 1;
}

export default function CaptionPerformance({ data = [] }) {
  const isEmpty = data.length === 0;
  const maxClicks = getMaxClicks(data);
  const maxPerPost = getMaxClicksPerPost(data);

  return (
    <div className="glass-card" style={{ padding: '24px' }}>
      <h3 className="section-title">
        <span className="icon">🧪</span> Caption Style A/B Performance
      </h3>
      <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', margin: '-8px 0 16px' }}>
        Which caption styles drive the most clicks per platform
      </p>

      {isEmpty ? (
        <div style={{ padding: '40px 20px', textAlign: 'center', color: 'var(--text-muted)' }}>
          <div style={{ fontSize: '2rem', marginBottom: 8 }}>🧪</div>
          <p>No caption performance data yet. Data appears as posts get published and clicked.</p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
          {data.map((item, i) => {
            const color = STYLE_COLORS[item.caption_style] || '#666';
            const emoji = STYLE_EMOJIS[item.caption_style] || '📝';
            const platforms = Object.entries(item.platforms || {});

            return (
              <div
                key={i}
                style={{
                  padding: '16px',
                  borderRadius: 12,
                  background: 'rgba(255,255,255,0.02)',
                  border: '1px solid var(--border)',
                  transition: 'var(--transition)',
                }}
              >
                {/* Header row */}
                <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 12 }}>
                  <span style={{ fontSize: '1.5rem' }}>{emoji}</span>
                  <div style={{ flex: 1 }}>
                    <div style={{ fontWeight: 600, fontSize: '0.95rem', textTransform: 'capitalize', display: 'flex', alignItems: 'center', gap: 8 }}>
                      {item.caption_style.replace(/_/g, ' ')}
                      <span style={{
                        display: 'inline-block',
                        width: 8,
                        height: 8,
                        borderRadius: '50%',
                        background: color,
                      }} />
                    </div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: 2 }}>
                      {item.total_posts} posts · {item.total_clicks} total clicks
                    </div>
                  </div>
                  <div style={{ textAlign: 'right' }}>
                    <div style={{
                      fontSize: '1.3rem',
                      fontWeight: 800,
                      color: item.clicks_per_post > 1 ? 'var(--success)' : 'var(--text-muted)',
                    }}>
                      {item.clicks_per_post.toFixed(1)}
                    </div>
                    <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>
                      clicks/post
                    </div>
                  </div>
                </div>

                {/* Per-platform bars */}
                {platforms.length > 0 ? (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 6, marginTop: 8 }}>
                    {platforms.map(([platform, clicks]) => (
                      <div key={platform} style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <span style={{ width: 28, textAlign: 'center', fontSize: '0.85rem' }}>
                          {PLATFORM_EMOJIS[platform] || '🔗'}
                        </span>
                        <span style={{
                          width: 80,
                          fontSize: '0.75rem',
                          color: 'var(--text-muted)',
                          textTransform: 'capitalize',
                          whiteSpace: 'nowrap',
                          overflow: 'hidden',
                          textOverflow: 'ellipsis',
                        }}>
                          {platform}
                        </span>
                        <div style={{
                          flex: 1,
                          height: 20,
                          background: 'rgba(255,255,255,0.04)',
                          borderRadius: 4,
                          overflow: 'hidden',
                          position: 'relative',
                        }}>
                          <div style={{
                            height: '100%',
                            width: `${(clicks / maxClicks) * 100}%`,
                            minWidth: clicks > 0 ? 4 : 0,
                            background: `linear-gradient(90deg, ${color}44, ${color})`,
                            borderRadius: 4,
                            transition: 'width 0.6s ease',
                          }} />
                        </div>
                        <span style={{
                          width: 60,
                          textAlign: 'right',
                          fontSize: '0.8rem',
                          fontWeight: 600,
                          color: '#fff',
                        }}>
                          {clicks.toLocaleString()}
                        </span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', padding: '8px 0' }}>
                    No clicks tracked yet for this style
                  </div>
                )}

                {/* Mini clicks/post bar */}
                <div style={{ marginTop: 10, display: 'flex', alignItems: 'center', gap: 8 }}>
                  <span style={{ fontSize: '0.65rem', color: 'var(--text-muted)', width: 28, textAlign: 'center' }}>📈</span>
                  <div style={{
                    flex: 1,
                    height: 6,
                    background: 'rgba(255,255,255,0.04)',
                    borderRadius: 3,
                    overflow: 'hidden',
                  }}>
                    <div style={{
                      height: '100%',
                      width: `${(item.clicks_per_post / maxPerPost) * 100}%`,
                      background: 'var(--gradient)',
                      borderRadius: 3,
                      transition: 'width 0.6s ease',
                    }} />
                  </div>
                  <span style={{
                    fontSize: '0.7rem',
                    fontWeight: 600,
                    width: 60,
                    textAlign: 'right',
                    color: item.clicks_per_post > 1 ? 'var(--success)' : 'var(--text-muted)',
                  }}>
                    {item.clicks_per_post.toFixed(1)}/post
                  </span>
                </div>
              </div>
            );
          })}

          {/* Legend */}
          <div style={{
            padding: '12px 16px',
            background: 'rgba(255,255,255,0.02)',
            borderRadius: 8,
            fontSize: '0.7rem',
            color: 'var(--text-muted)',
            lineHeight: 1.8,
          }}>
            <strong style={{ color: '#888' }}>How it works:</strong> Each caption style is shown with its clicks per platform (bar width = relative performance).
            Click-to-post ratio (📈) shows which styles convert best. Higher = better engagement.
          </div>
        </div>
      )}
    </div>
  );
}

import React from 'react';
import { FiX, FiExternalLink } from 'react-icons/fi';

const PLATFORMS = [
  { key: 'telegram', label: 'Telegram', color: '#2AABEE', bg: '#17212B', icon: '✈️', textColor: '#fff' },
  { key: 'instagram', label: 'Instagram', color: '#E4405F', bg: '#1a1a2e', icon: '📸', textColor: '#fff' },
  { key: 'facebook', label: 'Facebook', color: '#1877F2', bg: '#18191A', icon: '👍', textColor: '#e4e6eb' },
  { key: 'pinterest', label: 'Pinterest', color: '#BD081C', bg: '#1a1a2e', icon: '📌', textColor: '#fff' },
  { key: 'twitter', label: 'Twitter / X', color: '#1DA1F2', bg: '#000', icon: '🐦', textColor: '#e7e9ea' },
  { key: 'threads', label: 'Threads', color: '#101010', bg: '#101010', icon: '🧵', textColor: '#f5f5f5' },
];

function PlatformBadge({ platform }) {
  return (
    <span style={{
      display: 'inline-flex',
      alignItems: 'center',
      gap: 4,
      fontSize: '0.7rem',
      padding: '2px 8px',
      borderRadius: 10,
      background: `${platform.color}18`,
      color: platform.color,
      fontWeight: 500,
    }}>
      {platform.icon} {platform.label}
    </span>
  );
}

/* ─── Telegram Preview ─── */
function TelegramPreview({ caption, imageUrl }) {
  return (
    <div style={{
      background: '#17212B',
      borderRadius: 14,
      overflow: 'hidden',
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif',
      maxWidth: 420,
      boxShadow: '0 4px 16px rgba(0,0,0,0.3)',
    }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '12px 16px', borderBottom: '1px solid #1f2c38' }}>
        <div style={{
          width: 36, height: 36, borderRadius: '50%',
          background: 'linear-gradient(135deg, #2AABEE, #229ED9)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontSize: '1rem',
        }}>👗</div>
        <div>
          <div style={{ fontSize: '0.9rem', fontWeight: 600, color: '#fff' }}>FashionBazzer</div>
          <div style={{ fontSize: '0.7rem', color: '#6C7883' }}>Bot • Just now</div>
        </div>
      </div>

      {/* Image */}
      {imageUrl && (
        <div style={{
          width: '100%', height: 200,
          background: `url(${imageUrl}) center/cover no-repeat`,
          borderBottom: '1px solid #1f2c38',
        }} />
      )}

      {/* Caption */}
      <div style={{ padding: '12px 16px 16px' }}>
        <div style={{
          fontSize: '0.82rem',
          lineHeight: 1.6,
          color: '#fff',
          whiteSpace: 'pre-wrap',
          wordBreak: 'break-word',
          maxHeight: 280,
          overflow: 'auto',
        }}>
          {caption || 'No Telegram caption'}
        </div>
      </div>
    </div>
  );
}

/* ─── Instagram Preview ─── */
function InstagramPreview({ caption, imageUrl }) {
  const lines = (caption || '').split('\n');
  const hashTagLine = lines.find(l => l.includes('#'));
  const bodyLines = lines.filter(l => !l.includes('#') && l.trim());

  return (
    <div style={{
      background: '#1a1a2e',
      borderRadius: 14,
      overflow: 'hidden',
      fontFamily: '-apple-system, "Segoe UI", Roboto, sans-serif',
      maxWidth: 400,
      boxShadow: '0 4px 16px rgba(0,0,0,0.4)',
      border: '1px solid rgba(255,255,255,0.08)',
    }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '12px 16px' }}>
        <div style={{
          width: 32, height: 32, borderRadius: '50%',
          background: 'linear-gradient(45deg, #feda75, #fa7e1e, #d62976, #962fbf, #4f5bd5)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontSize: '0.8rem', color: '#fff',
        }}>FB</div>
        <div style={{ fontSize: '0.85rem', fontWeight: 600, color: '#fff' }}>FashionBazzer</div>
      </div>

      {/* Image placeholder */}
      <div style={{
        width: '100%', height: 220,
        background: imageUrl
          ? `url(${imageUrl}) center/cover no-repeat`
          : 'linear-gradient(135deg, #2d2d44, #1a1a2e)',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        fontSize: '2rem', color: 'rgba(255,255,255,0.2)',
      }}>
        {!imageUrl && '📷'}
      </div>

      {/* Actions row */}
      <div style={{ display: 'flex', gap: 16, padding: '10px 16px 4px', fontSize: '1.3rem' }}>
        <span>❤️</span> <span>💬</span> <span>↗️</span>
        <span style={{ marginLeft: 'auto' }}>🔖</span>
      </div>

      {/* Caption */}
      <div style={{ padding: '4px 16px 12px', fontSize: '0.82rem', lineHeight: 1.6, color: '#f5f5f5' }}>
        <strong style={{ marginRight: 6 }}>FashionBazzer</strong>
        {bodyLines.slice(0, 3).map((line, i) => (
          <div key={i} style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>{line}</div>
        ))}
        <div style={{ marginTop: 4, color: '#1DA1F2', fontSize: '0.78rem' }}>
          {hashTagLine || '#FashionBazzer #OOTD'}
        </div>
      </div>
    </div>
  );
}

/* ─── Facebook Preview ─── */
function FacebookPreview({ caption, imageUrl }) {
  const lines = (caption || '').split('\n').filter(l => l.trim());
  const truncated = lines.slice(0, 6);

  return (
    <div style={{
      background: '#242526',
      borderRadius: 10,
      overflow: 'hidden',
      fontFamily: 'Helvetica, Arial, sans-serif',
      maxWidth: 500,
      boxShadow: '0 2px 12px rgba(0,0,0,0.3)',
    }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '12px 16px' }}>
        <div style={{
          width: 36, height: 36, borderRadius: '50%',
          background: '#1877F2',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          color: '#fff', fontWeight: 700, fontSize: '0.9rem',
        }}>F</div>
        <div>
          <div style={{ fontSize: '0.85rem', fontWeight: 600, color: '#e4e6eb' }}>FashionBazzer</div>
          <div style={{ fontSize: '0.7rem', color: '#b0b3b8' }}>Sponsored • Just now</div>
        </div>
      </div>

      {/* Caption */}
      <div style={{ padding: '0 16px 12px', fontSize: '0.85rem', lineHeight: 1.5, color: '#e4e6eb' }}>
        {truncated.map((line, i) => (
          <div key={i} style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>
            {line.includes('affiliate_link') || line.includes('http') ? (
              <span style={{ color: '#1877F2' }}>{line}</span>
            ) : line}
          </div>
        ))}
      </div>

      {/* Image + link preview */}
      <div style={{
        width: '100%', height: 180,
        background: imageUrl
          ? `url(${imageUrl}) center/cover no-repeat`
          : '#3a3b3c',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        color: '#b0b3b8', fontSize: '0.85rem',
      }}>
        {!imageUrl && '🛒 Shop on FashionBazzer'}
      </div>

      {/* Actions */}
      <div style={{ display: 'flex', gap: 4, padding: '8px 16px', borderTop: '1px solid #3e4042', fontSize: '0.82rem', color: '#b0b3b8' }}>
        <span style={{ flex: 1, textAlign: 'center', padding: 6 }}>👍 Like</span>
        <span style={{ flex: 1, textAlign: 'center', padding: 6 }}>💬 Comment</span>
        <span style={{ flex: 1, textAlign: 'center', padding: 6 }}>↗️ Share</span>
      </div>
    </div>
  );
}

/* ─── Pinterest Preview ─── */
function PinterestPreview({ caption, imageUrl }) {
  return (
    <div style={{
      background: '#fff',
      borderRadius: 16,
      overflow: 'hidden',
      fontFamily: '-apple-system, "Segoe UI", Roboto, sans-serif',
      maxWidth: 280,
      boxShadow: '0 4px 20px rgba(0,0,0,0.15)',
    }}>
      {/* Pin image */}
      <div style={{
        width: '100%', height: 320,
        background: imageUrl
          ? `url(${imageUrl}) center/cover no-repeat`
          : 'linear-gradient(135deg, #f5f5f5, #e0e0e0)',
        display: 'flex', alignItems: 'flex-end', justifyContent: 'center',
        position: 'relative',
      }}>
        <div style={{
          position: 'absolute', top: 12, right: 12,
          background: '#e60023', color: '#fff',
          border: 'none', borderRadius: 24,
          padding: '8px 16px', fontWeight: 700, fontSize: '0.85rem',
          cursor: 'pointer',
        }}>Save</div>
      </div>

      {/* Title */}
      <div style={{ padding: '12px 16px 8px' }}>
        <div style={{
          fontSize: '0.82rem', fontWeight: 700, color: '#111',
          lineHeight: 1.4, overflow: 'hidden', textOverflow: 'ellipsis',
          display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical',
        }}>
          {(caption || '').split('\n')[0] || 'Trendy Dress'}
        </div>
        <div style={{
          fontSize: '0.72rem', color: '#767676', marginTop: 4,
          overflow: 'hidden', textOverflow: 'ellipsis',
          display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical',
        }}>
          {(caption || '').split('\n').slice(1, 3).join(' ')}
        </div>
      </div>
    </div>
  );
}

/* ─── Twitter Preview ─── */
function TwitterPreview({ caption, imageUrl }) {
  const lines = (caption || '').split('\n').filter(l => l.trim());
  const displayCaption = lines.slice(0, 4).join('\n');

  return (
    <div style={{
      background: '#000',
      borderRadius: 16,
      overflow: 'hidden',
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif',
      maxWidth: 500,
      border: '1px solid #2f3336',
    }}>
      {/* Tweet header */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 12, padding: '12px 16px 8px' }}>
        <div style={{
          width: 40, height: 40, borderRadius: '50%',
          background: 'linear-gradient(135deg, #FF3CAC, #784BA0)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          color: '#fff', fontWeight: 700, fontSize: '0.9rem',
        }}>FB</div>
        <div>
          <div style={{ fontSize: '0.9rem', fontWeight: 700, color: '#e7e9ea' }}>FashionBazzer</div>
          <div style={{ fontSize: '0.8rem', color: '#71767b' }}>@fashionbazzer</div>
        </div>
        <div style={{ marginLeft: 'auto', fontSize: '1.1rem', color: '#71767b' }}>···</div>
      </div>

      {/* Tweet body */}
      <div style={{ padding: '0 16px 8px', fontSize: '0.9rem', lineHeight: 1.5, color: '#e7e9ea', whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>
        {displayCaption || 'No caption'}
      </div>

      {/* Tweet image */}
      {imageUrl && (
        <div style={{ margin: '0 16px 12px', borderRadius: 16, overflow: 'hidden' }}>
          <div style={{
            width: '100%', height: 200,
            background: `url(${imageUrl}) center/cover no-repeat`,
          }} />
        </div>
      )}

      {/* Tweet actions */}
      <div style={{ display: 'flex', justifyContent: 'space-between', padding: '4px 16px 12px', maxWidth: 400, color: '#71767b', fontSize: '0.88rem' }}>
        <span>💬</span><span>🔁</span><span>❤️</span><span>🔖</span><span>↗️</span>
      </div>
    </div>
  );
}

/* ─── Threads Preview ─── */
function ThreadsPreview({ caption }) {
  const lines = (caption || '').split('\n').filter(l => l.trim());
  const displayCaption = lines.slice(0, 5).join('\n');

  return (
    <div style={{
      background: '#101010',
      borderRadius: 12,
      overflow: 'hidden',
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
      maxWidth: 500,
      border: '1px solid #2f3336',
    }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '12px 16px' }}>
        <div style={{
          width: 36, height: 36, borderRadius: '50%',
          background: 'linear-gradient(135deg, #333, #555)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          color: '#fff', fontSize: '0.9rem',
        }}>FB</div>
        <div>
          <div style={{ fontSize: '0.85rem', fontWeight: 600, color: '#f5f5f5' }}>fashionbazzer</div>
          <div style={{ fontSize: '0.72rem', color: '#6c6c6c' }}>1h • 23 replies</div>
        </div>
        <div style={{ marginLeft: 'auto', fontSize: '1.2rem', color: '#6c6c6c' }}>···</div>
      </div>

      {/* Content */}
      <div style={{ padding: '0 16px 12px', fontSize: '0.85rem', lineHeight: 1.5, color: '#f5f5f5', whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>
        {displayCaption || 'No caption'}
      </div>

      {/* Actions */}
      <div style={{ display: 'flex', gap: 24, padding: '4px 16px 12px', color: '#6c6c6c', fontSize: '0.95rem' }}>
        <span>❤️</span>
        <span>💬</span>
        <span>🔁</span>
        <span>↗️</span>
      </div>
    </div>
  );
}

/* ─── Main PostPreview Component ─── */
export default function PostPreview({ post, onClose }) {
  if (!post) return null;

  const imageUrl = post.product_image || post.image_url || '';

  return (
    <div style={{
      position: 'fixed',
      inset: 0,
      background: 'rgba(0,0,0,0.75)',
      backdropFilter: 'blur(10px)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1000,
      padding: 20,
    }} onClick={onClose}>
      <div className="glass-card" style={{
        maxWidth: 1200,
        width: '100%',
        maxHeight: '92vh',
        overflow: 'auto',
        padding: 0,
        borderRadius: 16,
      }} onClick={(e) => e.stopPropagation()}>

        {/* Header */}
        <div style={{
          position: 'sticky', top: 0, zIndex: 10,
          display: 'flex', alignItems: 'center', justifyContent: 'space-between',
          padding: '16px 24px',
          borderBottom: '1px solid var(--border)',
          background: 'rgba(26,26,46,0.95)',
          backdropFilter: 'blur(12px)',
        }}>
          <div>
            <h3 style={{ fontSize: '1.15rem', fontWeight: 600, margin: 0 }}>
              <span style={{ marginRight: 8 }}>📱</span> Post Preview
            </h3>
            <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', margin: '4px 0 0' }}>
              {post.product_name || `Post #${post.id}`}
              <span style={{ margin: '0 8px' }}>·</span>
              <span className={`tag ${post.status === 'published' ? 'tag-success' : post.status === 'failed' ? 'tag-error' : 'tag-warning'}`}>
                {post.status}
              </span>
              {post.caption_style && (
                <>
                  <span style={{ margin: '0 8px' }}>·</span>
                  <PlatformBadge platform={{ label: post.caption_style.replace(/_/g, ' '), color: '#FFB800', icon: '🎨' }} />
                </>
              )}
            </p>
          </div>
          <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
            <a
              href={`/posts?preview=${post.id}`}
              className="btn btn-secondary btn-sm"
              style={{ textDecoration: 'none' }}
            >
              <FiExternalLink size={14} /> Permalink
            </a>
            <button onClick={onClose} className="btn btn-secondary btn-sm" title="Close">
              <FiX size={16} />
            </button>
          </div>
        </div>

        {/* Platform Previews */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))',
          gap: 24,
          padding: 24,
        }}>
          {PLATFORMS.map((platform) => {
            const captionKey = `${platform.key}_caption`;
            const caption = post[captionKey];
            if (!caption) return null;

            return (
              <div key={platform.key}>
                <div style={{
                  display: 'flex', alignItems: 'center', gap: 8,
                  marginBottom: 12, fontSize: '0.85rem', fontWeight: 600, color: platform.color,
                }}>
                  <span style={{ fontSize: '1.1rem' }}>{platform.icon}</span>
                  {platform.label}
                </div>

                {platform.key === 'telegram' && <TelegramPreview caption={caption} imageUrl={imageUrl} />}
                {platform.key === 'instagram' && <InstagramPreview caption={caption} imageUrl={imageUrl} />}
                {platform.key === 'facebook' && <FacebookPreview caption={caption} imageUrl={imageUrl} />}
                {platform.key === 'pinterest' && <PinterestPreview caption={caption} imageUrl={imageUrl} />}
                {platform.key === 'twitter' && <TwitterPreview caption={caption} imageUrl={imageUrl} />}
                {platform.key === 'threads' && <ThreadsPreview caption={caption} />}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

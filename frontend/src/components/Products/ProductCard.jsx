import React from 'react';
import { FiExternalLink, FiStar, FiMessageCircle, FiBarChart2 } from 'react-icons/fi';
import './ProductCard.css';

export default function ProductCard({ product, onGenerate }) {
  return (
    <div className="product-card glass-card" style={{ padding: 0, overflow: 'hidden' }}>
      {/* Image */}
      <div className="product-image-wrapper" style={{ height: 200, background: 'var(--bg-card)' }}>
        {product.image_url ? (
          <img
            src={product.image_url}
            alt={product.name}
            onError={(e) => {
              e.target.style.display = 'none';
            }}
          />
        ) : (
          <div style={{
            height: '100%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '3rem',
            opacity: 0.3,
          }}>
            👗
          </div>
        )}
        <span className={`platform-badge ${product.platform}`}>{product.platform}</span>
        {product.discount_percent > 0 && (
          <span className="discount-badge">-{product.discount_percent}%</span>
        )}
      </div>

      {/* Content */}
      <div style={{ padding: '16px' }}>
        <h3 style={{
          fontSize: '0.85rem',
          fontWeight: 600,
          marginBottom: 8,
          lineHeight: 1.4,
          display: '-webkit-box',
          WebkitLineClamp: 2,
          WebkitBoxOrient: 'vertical',
          overflow: 'hidden',
          minHeight: 38,
        }}>
          {product.name}
        </h3>

        <div className="price-container">
          <span className="current-price">₹{parseInt(product.sale_price).toLocaleString()}</span>
          {product.original_price > product.sale_price && (
            <span className="original-price">₹{parseInt(product.original_price).toLocaleString()}</span>
          )}
        </div>

        {/* Rating & Reviews */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: 12,
          marginTop: 8,
          fontSize: '0.8rem',
          color: 'var(--text-muted)',
        }}>
          <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
            <FiStar size={14} color="#FFB800" /> {product.rating}
          </span>
          <span>{product.review_count?.toLocaleString()} reviews</span>
        </div>

        {/* Category */}
        {product.category && (
          <span className="tag tag-primary" style={{ marginTop: 8 }}>
            {product.category}
          </span>
        )}

        {/* AI Tagline */}
        {product.ai_tagline && (
          <p style={{
            marginTop: 10,
            fontSize: '0.8rem',
            color: 'var(--text-secondary)',
            fontStyle: 'italic',
            lineHeight: 1.5,
            borderTop: '1px solid var(--border)',
            paddingTop: 10,
          }}>
            💬 {product.ai_tagline}
          </p>
        )}

        {/* Actions */}
        <div style={{
          display: 'flex',
          gap: 8,
          marginTop: 12,
          paddingTop: 12,
          borderTop: '1px solid var(--border)',
        }}>
          <button
            className="btn btn-primary btn-sm"
            onClick={() => onGenerate?.(product.id)}
            style={{ flex: 1 }}
          >
            <FiMessageCircle size={14} /> Generate Post
          </button>
          {product.affiliate_url && (
            <a
              href={product.affiliate_url}
              target="_blank"
              rel="noopener noreferrer"
              className="btn btn-secondary btn-sm"
            >
              <FiExternalLink size={14} />
            </a>
          )}
        </div>
      </div>
    </div>
  );
}

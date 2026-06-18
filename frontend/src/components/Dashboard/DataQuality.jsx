import React, { useState, useEffect, useRef } from 'react';
import api from '../../services/api';
import {
  FiAlertTriangle, FiTrendingDown,
  FiGrid, FiRefreshCw,
} from 'react-icons/fi';

// ── Color palette ──
const COLORS = {
  primary: '#FF3CAC',
  success: '#00D4AA',
  warning: '#FFB800',
  error: '#FF4757',
  info: '#3B82F6',
  purple: '#A855F7',
  pink: '#EC4899',
  teal: '#14B8A6',
  orange: '#F97316',
};

const PLATFORM_COLORS = {
  meesho: COLORS.purple,
  amazon: COLORS.orange,
  flipkart: COLORS.primary,
  myntra: COLORS.info,
  ajio: COLORS.teal,
};

const PLATFORM_EMOJIS = {
  meesho: '🛍️',
  amazon: '📦',
  flipkart: '🛒',
  myntra: '👗',
  ajio: '✨',
};

const CATEGORY_LABELS = {
  'co-ord': 'Co-ord Sets',
  'y2k': 'Y2K',
  'bodycon': 'Bodycon',
  'cottagecore': 'Cottagecore',
  'indo-western': 'Indo-Western',
  'athleisure': 'Athleisure',
  'cut-out': 'Cut-out',
  'wrap': 'Wrap',
  'other': 'Other',
};

// ── Animated counter ──
function AnimatedValue({ value, suffix = '', prefix = '', duration = 1000 }) {
  const [display, setDisplay] = useState(0);
  const prevRef = useRef(0);

  useEffect(() => {
    const target = Number(value) || 0;
    const start = prevRef.current;
    const startTime = performance.now();
    let raf;

    function animate(now) {
      const progress = Math.min((now - startTime) / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      setDisplay(Math.round(start + (target - start) * eased));
      if (progress < 1) raf = requestAnimationFrame(animate);
      else prevRef.current = target;
    }

    raf = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(raf);
  }, [value, duration]);

  return <>{prefix}{(display || 0).toLocaleString('en-IN')}{suffix}</>;
}

// ── Mini progress bar ──
function ProgressBar({ value, max, color = COLORS.primary, height = 8, label }) {
  const pct = max > 0 ? Math.min((value / max) * 100, 100) : 0;
  return (
    <div style={{ width: '100%' }}>
      {label && (
        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', marginBottom: 4, color: 'var(--text-muted)' }}>
          <span>{label}</span>
          <span>{Math.round(pct)}%</span>
        </div>
      )}
      <div style={{ width: '100%', height, background: 'rgba(255,255,255,0.06)', borderRadius: height / 2, overflow: 'hidden' }}>
        <div style={{ width: `${pct}%`, height: '100%', background: color, borderRadius: height / 2, transition: 'width 1s ease' }} />
      </div>
    </div>
  );
}

// ── Stat Card ──
function StatCard({ title, value, subtitle, icon, color, trend, trendLabel, prefix = '', suffix = '' }) {
  return (
    <div className="glass-card" style={{
      padding: '20px', display: 'flex', flexDirection: 'column', gap: 8, position: 'relative', overflow: 'hidden',
    }}>
      <div style={{
        position: 'absolute', top: -40, right: -40, width: 120, height: 120, borderRadius: '50%',
        background: `${color}12`, filter: 'blur(30px)',
      }} />
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div style={{
          width: 40, height: 40, borderRadius: 10, background: `${color}18`,
          display: 'flex', alignItems: 'center', justifyContent: 'center', color,
        }}>
          {icon}
        </div>
        {trend !== undefined && (
          <span style={{
            fontSize: '0.75rem', fontWeight: 600, padding: '2px 8px', borderRadius: 6,
            background: trend >= 0 ? 'rgba(0,212,170,0.15)' : 'rgba(255,71,87,0.15)',
            color: trend >= 0 ? COLORS.success : COLORS.error,
          }}>
            {trend >= 0 ? '↑' : '↓'} {Math.abs(trend)}%
          </span>
        )}
      </div>
      <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 500, textTransform: 'uppercase', letterSpacing: '0.5px' }}>
        {title}
      </span>
      <div style={{ fontSize: '1.8rem', fontWeight: 800, color: 'var(--text)', lineHeight: 1.2 }}>
        <AnimatedValue value={value} prefix={prefix} suffix={suffix} />
      </div>
      {subtitle && <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{subtitle}</span>}
    </div>
  );
}

// ── Quality gauge ──
function QualityGauge({ score }) {
  const color = score >= 80 ? COLORS.success : score >= 50 ? COLORS.warning : COLORS.error;
  const emoji = score >= 80 ? '🌟' : score >= 50 ? '⚠️' : '🔴';
  return (
    <div className="glass-card" style={{ padding: '24px', textAlign: 'center', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 12 }}>
      <span style={{ fontSize: '2.5rem' }}>{emoji}</span>
      <div style={{ fontSize: '2.5rem', fontWeight: 800, color }}>
        <AnimatedValue value={score} suffix="%" />
      </div>
      <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)', fontWeight: 500 }}>
        Data Quality Score
      </span>
      <ProgressBar value={score} max={100} color={color} height={6} />
    </div>
  );
}

// ── Horizontal bar chart ──
function HorizontalBar({ items, valueKey, labelKey, colorMap, maxValue }) {
  if (!items || items.length === 0) return <div style={{ color: 'var(--text-muted)', padding: 16, textAlign: 'center' }}>No data</div>;
  const max = maxValue || Math.max(...items.map(i => Number(i[valueKey] || 0)), 1);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
      {items.map((item, i) => {
        const val = Number(item[valueKey] || 0);
        const pct = (val / max) * 100;
        const color = typeof colorMap === 'function' ? colorMap(item) : colorMap?.[item[labelKey]] || COLORS.primary;
        return (
          <div key={item[labelKey] || i}>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', marginBottom: 4 }}>
              <span style={{ color: 'var(--text)' }}>{item[labelKey] || item.platform || item.category}</span>
              <span style={{ color: 'var(--text-muted)', fontWeight: 600 }}>{val.toLocaleString('en-IN')}</span>
            </div>
            <div style={{ width: '100%', height: 20, background: 'rgba(255,255,255,0.04)', borderRadius: 10, overflow: 'hidden', position: 'relative' }}>
              <div style={{
                width: `${pct}%`, height: '100%', background: color, borderRadius: 10,
                transition: 'width 0.8s ease', opacity: 0.8,
              }} />
              {item.stale !== undefined && item.stale > 0 && (
                <div style={{
                  position: 'absolute', top: 0, left: `${(item.stale / max) * 100}%`,
                  height: '100%', width: 4, background: COLORS.error, borderRadius: 2,
                }} />
              )}
            </div>
            {item.stale !== undefined && item.stale > 0 && (
              <div style={{ fontSize: '0.65rem', color: COLORS.error, marginTop: 2 }}>
                {item.stale} stale
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}

// ── Offender table row ──
function OffenderRow({ product, index }) {
  const isStaleView = product.original_price === product.sale_price;
  const hasRating = Number(product.rating) > 0;

  return (
    <tr key={product.id}>
      <td style={{ padding: '8px 12px', color: 'var(--text-muted)', fontSize: '0.8rem', textAlign: 'center' }}>{index + 1}</td>
      <td style={{ padding: '8px 12px', fontSize: '0.85rem', color: 'var(--text)', maxWidth: 200, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
        {product.name?.substring(0, 40)}...
      </td>
      <td style={{ padding: '8px 12px' }}>
        <span style={{
          fontSize: '0.75rem', padding: '2px 8px', borderRadius: 6,
          background: `${PLATFORM_COLORS[product.platform] || COLORS.primary}18`,
          color: PLATFORM_COLORS[product.platform] || COLORS.primary,
          fontWeight: 600,
        }}>
          {PLATFORM_EMOJIS[product.platform] || '📱'} {product.platform}
        </span>
      </td>
      <td style={{ padding: '8px 12px', fontSize: '0.85rem', color: 'var(--text)' }}>
        ₹{Number(product.sale_price).toLocaleString('en-IN')}
      </td>
      <td style={{ padding: '8px 12px', fontSize: '0.85rem' }}>
        {isStaleView ? (
          <span style={{ color: COLORS.error }}>⚠️ Same</span>
        ) : (
          <span style={{ color: COLORS.success }}>₹{Number(product.original_price).toLocaleString('en-IN')}</span>
        )}
      </td>
      <td style={{ padding: '8px 12px', fontSize: '0.85rem' }}>
        {hasRating ? (
          <span style={{ color: COLORS.warning }}>⭐ {product.rating}</span>
        ) : (
          <span style={{ color: COLORS.error }}>—</span>
        )}
      </td>
      <td style={{ padding: '8px 12px', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
        {product.review_count || '0'}
      </td>
    </tr>
  );
}

export default function DataQualityDashboard() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    fetchData();
  }, []);

  async function fetchData() {
    try {
      const res = await api.get('/dashboard/data-quality/');
      setData(res.data);
    } catch (err) {
      console.error('Failed to fetch data quality:', err);
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 300 }}>
        <div style={{ width: 40, height: 40, border: '3px solid var(--border)', borderTopColor: 'var(--primary)', borderRadius: '50%', animation: 'spin 0.8s linear infinite' }} />
      </div>
    );
  }

  if (!data) {
    return (
      <div className="glass-card" style={{ padding: 40, textAlign: 'center' }}>
        <div style={{ fontSize: '3rem', marginBottom: 16 }}>⚠️</div>
        <h2>Failed to load data quality metrics</h2>
        <p style={{ color: 'var(--text-muted)' }}>Check backend connection and try again.</p>
        <button className="btn btn-primary" onClick={fetchData} style={{ marginTop: 16 }}>
          <FiRefreshCw size={14} /> Retry
        </button>
      </div>
    );
  }

  // Calculate quality score based on healthy data proportions
  const healthScore = Math.round(
    ((data.total_products - data.stale_count) / data.total_products * 40) +
    ((data.total_products - data.missing_rating_count) / data.total_products * 30) +
    (data.content_ratio / 100 * 20) +
    (data.fresh_count / data.total_products * 10)
  );

  return (
    <div className="fade-in">
      <div className="page-header">
        <div>
          <h1>📊 Data Quality</h1>
          <p>Product data accuracy monitoring dashboard</p>
        </div>
        <button className="btn btn-secondary" onClick={fetchData}>
          <FiRefreshCw size={14} /> Refresh
        </button>
      </div>

      {/* Quality Score + Key Metrics */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr 1fr', gap: 16, padding: '0 24px', marginBottom: 24 }}>
        <QualityGauge score={healthScore} />
        <StatCard
          title="Total Products"
          value={data.total_products}
          subtitle={`${data.has_content} with AI content (${data.content_ratio}%)`}
          icon={<FiGrid size={18} />}
          color={COLORS.info}
        />
        <StatCard
          title="Stale Prices"
          value={data.stale_count}
          subtitle={`${data.stale_percent}% of total · ${data.fresh_count} fresh in 24h`}
          icon={<FiAlertTriangle size={18} />}
          color={data.stale_percent > 30 ? COLORS.error : data.stale_percent > 10 ? COLORS.warning : COLORS.success}
        />
        <StatCard
          title="Missing Ratings"
          value={data.missing_rating_count}
          subtitle={`${data.missing_rating_percent}% of total`}
          icon={<FiTrendingDown size={18} />}
          color={data.missing_rating_percent > 30 ? COLORS.error : data.missing_rating_percent > 10 ? COLORS.warning : COLORS.success}
        />
      </div>

      {/* Tabs */}
      <div style={{
        display: 'flex', gap: 0, margin: '0 24px 20px',
        borderBottom: '1px solid var(--border)', paddingBottom: 0,
      }}>
        {['overview', 'platforms', 'categories', 'offenders'].map(tab => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            style={{
              padding: '10px 20px', border: 'none', background: 'transparent',
              color: activeTab === tab ? 'var(--text)' : 'var(--text-muted)',
              fontWeight: activeTab === tab ? 600 : 400,
              borderBottom: activeTab === tab ? '2px solid var(--primary)' : '2px solid transparent',
              cursor: 'pointer', fontSize: '0.85rem', textTransform: 'capitalize',
              transition: 'var(--transition)',
            }}
          >
            {tab === 'overview' && '📈 Overview'}
            {tab === 'platforms' && '📱 Platforms'}
            {tab === 'categories' && '🏷️ Categories'}
            {tab === 'offenders' && '⚠️ Offenders'}
          </button>
        ))}
      </div>

      {/* Tab: Overview */}
      {activeTab === 'overview' && (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20, padding: '0 24px' }}>
          <div className="glass-card" style={{ padding: 20 }}>
            <h3 style={{ margin: '0 0 12px', fontSize: '0.95rem', fontWeight: 600 }}>📋 Data Health Breakdown</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
              <ProgressBar
                value={data.total_products - data.stale_count}
                max={data.total_products}
                color={COLORS.success}
                label="Products with valid prices"
              />
              <ProgressBar
                value={data.total_products - data.missing_rating_count}
                max={data.total_products}
                color={COLORS.warning}
                label="Products with ratings"
              />
              <ProgressBar
                value={data.has_content}
                max={data.total_products}
                color={COLORS.purple}
                label="Products with AI content"
              />
              <ProgressBar
                value={data.fresh_count}
                max={data.total_products}
                color={COLORS.info}
                label="Products refreshed in 24h"
              />
            </div>
          </div>

          <div className="glass-card" style={{ padding: 20 }}>
            <h3 style={{ margin: '0 0 12px', fontSize: '0.95rem', fontWeight: 600 }}>💰 Pricing Overview</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '8px 0', borderBottom: '1px solid var(--border)' }}>
                <span style={{ color: 'var(--text-muted)' }}>Average Discount</span>
                <span style={{ fontSize: '1.4rem', fontWeight: 800, color: COLORS.success }}>
                  {data.avg_discount}%
                </span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '8px 0', borderBottom: '1px solid var(--border)' }}>
                <span style={{ color: 'var(--text-muted)' }}>Stale Price Rate</span>
                <span style={{ fontSize: '1.2rem', fontWeight: 600, color: data.stale_percent > 30 ? COLORS.error : COLORS.warning }}>
                  {data.stale_percent}%
                </span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '8px 0', borderBottom: '1px solid var(--border)' }}>
                <span style={{ color: 'var(--text-muted)' }}>Missing Rating Rate</span>
                <span style={{ fontSize: '1.2rem', fontWeight: 600, color: data.missing_rating_percent > 30 ? COLORS.error : COLORS.warning }}>
                  {data.missing_rating_percent}%
                </span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '8px 0' }}>
                <span style={{ color: 'var(--text-muted)' }}>AI Content Coverage</span>
                <span style={{ fontSize: '1.2rem', fontWeight: 600, color: data.content_ratio > 50 ? COLORS.success : COLORS.warning }}>
                  {data.content_ratio}%
                </span>
              </div>
            </div>
          </div>

          <div className="glass-card" style={{ padding: 20 }}>
            <h3 style={{ margin: '0 0 12px', fontSize: '0.95rem', fontWeight: 600 }}>🏆 Quality Score</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Price Accuracy</span>
                <span style={{ color: COLORS.success, fontWeight: 600 }}>40 pts</span>
              </div>
              <ProgressBar
                value={data.total_products - data.stale_count}
                max={data.total_products}
                color={COLORS.success}
                height={6}
              />
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 4 }}>
                <span style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Rating Completeness</span>
                <span style={{ color: COLORS.warning, fontWeight: 600 }}>30 pts</span>
              </div>
              <ProgressBar
                value={data.total_products - data.missing_rating_count}
                max={data.total_products}
                color={COLORS.warning}
                height={6}
              />
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 4 }}>
                <span style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Content Coverage</span>
                <span style={{ color: COLORS.purple, fontWeight: 600 }}>20 pts</span>
              </div>
              <ProgressBar
                value={data.has_content}
                max={data.total_products}
                color={COLORS.purple}
                height={6}
              />
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 4 }}>
                <span style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Data Freshness</span>
                <span style={{ color: COLORS.info, fontWeight: 600 }}>10 pts</span>
              </div>
              <ProgressBar
                value={data.fresh_count}
                max={data.total_products}
                color={COLORS.info}
                height={6}
              />
            </div>
          </div>

          <div className="glass-card" style={{ padding: 20 }}>
            <h3 style={{ margin: '0 0 12px', fontSize: '0.95rem', fontWeight: 600 }}>🕐 Data Freshness</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 12, alignItems: 'center', justifyContent: 'center', minHeight: 120 }}>
              <div style={{ fontSize: '2rem', fontWeight: 800, color: COLORS.info }}>
                <AnimatedValue value={data.fresh_count} suffix={` / ${data.total_products}`} />
              </div>
              <span style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                Products updated in last 24 hours
              </span>
              <span style={{ color: 'var(--text-muted)', fontSize: '0.75rem' }}>
                Last refresh: {data.last_refresh ? new Date(data.last_refresh).toLocaleString('en-IN') : 'Never'}
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Tab: Platforms */}
      {activeTab === 'platforms' && (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20, padding: '0 24px' }}>
          <div className="glass-card" style={{ padding: 20 }}>
            <h3 style={{ margin: '0 0 16px', fontSize: '0.95rem', fontWeight: 600 }}>Products by Platform</h3>
            <HorizontalBar
              items={data.platform_distribution}
              valueKey="count"
              labelKey="platform"
              colorMap={(item) => PLATFORM_COLORS[item.platform] || COLORS.primary}
            />
          </div>
          <div className="glass-card" style={{ padding: 20 }}>
            <h3 style={{ margin: '0 0 16px', fontSize: '0.95rem', fontWeight: 600 }}>Stale Products by Platform</h3>
            <HorizontalBar
              items={data.platform_distribution}
              valueKey="stale"
              labelKey="platform"
              colorMap={(item) => COLORS.error}
              maxValue={Math.max(...data.platform_distribution.map(i => Number(i.stale)), 1)}
            />
            <div style={{ marginTop: 16, fontSize: '0.75rem', color: 'var(--text-muted)' }}>
              Red marker on bars above shows stale count relative to total
            </div>
          </div>
        </div>
      )}

      {/* Tab: Categories */}
      {activeTab === 'categories' && (
        <div style={{ padding: '0 24px' }}>
          <div className="glass-card" style={{ padding: 20 }}>
            <h3 style={{ margin: '0 0 16px', fontSize: '0.95rem', fontWeight: 600 }}>Products by Category</h3>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: 12 }}>
              {data.category_distribution?.map((cat, i) => {
                const catKey = cat.category;
                const total = cat.count;
                const pct = (total / data.total_products * 100);
                const label = CATEGORY_LABELS[catKey] || catKey;
                const colors = Object.values(COLORS);
                const color = colors[i % colors.length];

                return (
                  <div key={catKey} style={{ display: 'flex', alignItems: 'center', gap: 12, padding: '8px 0' }}>
                    <div style={{
                      width: 40, height: 40, borderRadius: 10,
                      background: `${color}18`, display: 'flex',
                      alignItems: 'center', justifyContent: 'center',
                      fontSize: '1.2rem',
                    }}>
                      {['🧩', '🌟', '💃', '🌿', '🪷', '🏃', '✂️', '🎀', '📦'][i % 9]}
                    </div>
                    <div style={{ flex: 1 }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                        <span style={{ fontSize: '0.85rem', color: 'var(--text)' }}>{label}</span>
                        <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 600 }}>
                          {total} ({pct.toFixed(1)}%)
                        </span>
                      </div>
                      <ProgressBar value={total} max={data.total_products} color={color} height={6} />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}

      {/* Tab: Offenders */}
      {activeTab === 'offenders' && (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20, padding: '0 24px' }}>
          <div className="glass-card" style={{ padding: 20, overflow: 'hidden' }}>
            <h3 style={{ margin: '0 0 12px', fontSize: '0.95rem', fontWeight: 600 }}>
              ⚠️ Worst Stale Prices <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 400 }}>(no MRP found)</span>
            </h3>
            {data.worst_stale_products?.length > 0 ? (
              <div style={{ overflowX: 'auto' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.8rem' }}>
                  <thead>
                    <tr style={{ borderBottom: '1px solid var(--border)' }}>
                      <th style={{ padding: '8px 12px', textAlign: 'center', color: 'var(--text-muted)', fontWeight: 500 }}>#</th>
                      <th style={{ padding: '8px 12px', textAlign: 'left', color: 'var(--text-muted)', fontWeight: 500 }}>Product</th>
                      <th style={{ padding: '8px 12px', textAlign: 'left', color: 'var(--text-muted)', fontWeight: 500 }}>Platform</th>
                      <th style={{ padding: '8px 12px', textAlign: 'right', color: 'var(--text-muted)', fontWeight: 500 }}>Price</th>
                      <th style={{ padding: '8px 12px', textAlign: 'right', color: 'var(--text-muted)', fontWeight: 500 }}>MRP</th>
                      <th style={{ padding: '8px 12px', textAlign: 'center', color: 'var(--text-muted)', fontWeight: 500 }}>Rating</th>
                      <th style={{ padding: '8px 12px', textAlign: 'right', color: 'var(--text-muted)', fontWeight: 500 }}>Reviews</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.worst_stale_products.map((p, i) => (
                      <OffenderRow key={p.id} product={p} index={i} />
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div style={{ textAlign: 'center', padding: 40, color: COLORS.success }}>
                <div style={{ fontSize: '3rem', marginBottom: 8 }}>🎉</div>
                No stale prices found!
              </div>
            )}
          </div>

          <div className="glass-card" style={{ padding: 20, overflow: 'hidden' }}>
            <h3 style={{ margin: '0 0 12px', fontSize: '0.95rem', fontWeight: 600 }}>
              ⭐ Worst Missing Ratings <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 400 }}>(no real rating data)</span>
            </h3>
            {data.worst_rating_products?.length > 0 ? (
              <div style={{ overflowX: 'auto' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.8rem' }}>
                  <thead>
                    <tr style={{ borderBottom: '1px solid var(--border)' }}>
                      <th style={{ padding: '8px 12px', textAlign: 'center', color: 'var(--text-muted)', fontWeight: 500 }}>#</th>
                      <th style={{ padding: '8px 12px', textAlign: 'left', color: 'var(--text-muted)', fontWeight: 500 }}>Product</th>
                      <th style={{ padding: '8px 12px', textAlign: 'left', color: 'var(--text-muted)', fontWeight: 500 }}>Platform</th>
                      <th style={{ padding: '8px 12px', textAlign: 'right', color: 'var(--text-muted)', fontWeight: 500 }}>Price</th>
                      <th style={{ padding: '8px 12px', textAlign: 'center', color: 'var(--text-muted)', fontWeight: 500 }}>Rating</th>
                      <th style={{ padding: '8px 12px', textAlign: 'right', color: 'var(--text-muted)', fontWeight: 500 }}>Reviews</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.worst_rating_products.map((p, i) => (
                      <OffenderRow key={p.id} product={p} index={i} />
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div style={{ textAlign: 'center', padding: 40, color: COLORS.success }}>
                <div style={{ fontSize: '3rem', marginBottom: 8 }}>🎉</div>
                All products have ratings!
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

import React from 'react';
import { Link } from 'react-router-dom';
import {
  FiArrowRight, FiGrid, FiStar, FiSend, FiTrendingUp, FiBarChart2,
  FiDollarSign, FiClock, FiShield, FiZap, FiRefreshCw, FiCheckCircle,
} from 'react-icons/fi';

const FEATURES = [
  {
    icon: FiGrid, color: '#FF3CAC',
    title: 'Auto Product Scraping',
    desc: 'Every 6 hours, FashionBazzer scrapes Amazon, Meesho, and Flipkart for the latest trending dresses. Products are filtered by rating (4.0+), price (under ₹1,500), and trending signals. No manual searching — always fresh inventory.',
    highlights: ['Amazon India scraping', 'Meesho trending products', 'Flipkart bestsellers', 'Auto image fetching', 'Duplicate detection'],
  },
  {
    icon: FiStar, color: '#784BA0',
    title: 'AI-Powered Content Generation',
    desc: 'Each product gets a unique AI-generated tagline using HuggingFace\'s Mistral-7B model, plus platform-specific captions in 8 rotating styles: excited, informative, urgency, social proof, lifestyle, trendy, question, and discount.',
    highlights: ['AI taglines via HuggingFace', '8 caption styles', '6 platform variants', 'Smart fallback templates', 'Auto image composition'],
  },
  {
    icon: FiSend, color: '#2B86C5',
    title: '6-Platform Auto Posting',
    desc: 'Posts are automatically published to Telegram, Instagram, Facebook, Pinterest, Twitter/X, and Threads. Each platform gets platform-optimized captions and image sizes.',
    highlights: ['Telegram (9x/day)', 'Instagram (3x/day)', 'Facebook (3x/day)', 'Pinterest (4x/day)', 'Twitter/X (3x/day)', 'Threads (2x/day)'],
  },
  {
    icon: FiTrendingUp, color: '#00D4AA',
    title: 'Smart Scheduling',
    desc: 'All posts are scheduled at peak engagement hours for Indian audiences. The scheduler runs on IST and automatically adjusts for best reach. 24+ posts/day, every day.',
    highlights: ['IST-optimized timing', 'Peak hour targeting', '24+ daily posts', 'Auto top-up queue', 'Misfire recovery'],
  },
  {
    icon: FiBarChart2, color: '#FFB800',
    title: 'Real-Time Analytics',
    desc: 'Track every click, conversion, and commission in real-time. See which platforms perform best, which products drive the most revenue, and how your earnings grow day-over-day.',
    highlights: ['Click tracking', 'Conversion tracking', 'Platform analytics', 'Revenue dashboard', 'Trending products'],
  },
  {
    icon: FiDollarSign, color: '#FF3CAC',
    title: 'Commission Tracking',
    desc: 'Auto-sync earnings from all affiliate networks (Amazon, Meesho, Flipkart). Track pending vs approved commissions, view earnings by platform, and estimate future revenue.',
    highlights: ['Multi-network sync', 'Pending tracking', 'Approved earnings', 'Platform breakdown', 'Revenue projections'],
  },
  {
    icon: FiRefreshCw, color: '#784BA0',
    title: 'Content Recycling',
    desc: 'Never run out of posts. When the pending queue drops below threshold, the system automatically recycles existing products with fresh captions, taglines, and images.',
    highlights: ['Auto-refill pipeline', 'Smart recycling (6x/day)', 'Fresh captions each cycle', 'Queue health monitoring', 'No manual intervention'],
  },
  {
    icon: FiShield, color: '#2B86C5',
    title: 'Platform Health Monitoring',
    desc: 'All API connections are tested every 30 minutes. If a platform goes down, you\'ll see it immediately in the dashboard. Auto-retry on failure keeps your pipeline running.',
    highlights: ['30-second health checks', 'Auto error detection', 'Visual status indicators', 'Retry on failure', 'Connection history'],
  },
];

export default function FeaturesPage() {
  React.useEffect(() => { window.scrollTo(0, 0); }, []);

  return (
    <div className="landing-page">
      {/* Simple nav bar */}
      <nav className="page-top-nav">
        <Link to="/" style={{ display: 'flex', alignItems: 'center', gap: 8, textDecoration: 'none' }}>
          <span style={{ fontSize: '1.4rem' }}>👗</span>
          <span style={{ fontWeight: 700, fontSize: '1rem', background: 'var(--gradient)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>FashionBazzer</span>
        </Link>
        <div style={{ display: 'flex', gap: 8 }}>
          <Link to="/" className="btn btn-secondary btn-sm">← Back</Link>
          <Link to="/dashboard" className="btn btn-primary btn-sm">Dashboard <FiArrowRight size={14} /></Link>
        </div>
      </nav>

      <div className="landing-hero" style={{ minHeight: 'auto', paddingBottom: 40 }}>
        <div style={{ maxWidth: 1000, margin: '0 auto', padding: '120px 24px 40px', textAlign: 'center' }}>
          <div className="hero-badge"><FiZap size={12} /> Everything Automated</div>
          <h1 className="hero-title" style={{ fontSize: 'clamp(2rem, 5vw, 3.2rem)' }}>
            All Features, <span className="gradient-text">Zero Effort</span>
          </h1>
          <p className="hero-subtitle">11 automated jobs · 6 platforms · 24+ daily posts · Real-time analytics</p>
        </div>
      </div>

      <div style={{ maxWidth: 1100, margin: '0 auto', padding: '0 24px 80px' }}>
        {FEATURES.map((f, i) => {
          const Icon = f.icon;
          return (
            <div key={i} className="glass-card" style={{
              padding: '32px 36px', marginBottom: 20,
              display: 'flex', gap: 32, alignItems: 'flex-start',
              flexWrap: 'wrap',
            }}>
              <div className="feature-icon" style={{
                width: 64, height: 64, borderRadius: 16,
                background: `${f.color}20`, color: f.color,
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                flexShrink: 0,
              }}>
                <Icon size={28} />
              </div>
              <div style={{ flex: 1, minWidth: 250 }}>
                <h3 style={{ fontSize: '1.2rem', fontWeight: 700, marginBottom: 8, color: f.color }}>{f.title}</h3>
                <p style={{ color: 'var(--text-secondary)', lineHeight: 1.7, marginBottom: 16 }}>{f.desc}</p>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
                  {f.highlights.map((h, j) => (
                    <span key={j} className="tag tag-primary"><FiCheckCircle size={12} /> {h}</span>
                  ))}
                </div>
              </div>
            </div>
          );
        })}

        <div style={{ textAlign: 'center', marginTop: 40 }}>
          <Link to="/pricing" className="btn btn-primary btn-lg">
            View Pricing <FiArrowRight size={18} />
          </Link>
        </div>
      </div>
    </div>
  );
}

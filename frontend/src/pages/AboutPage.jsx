import React from 'react';
import { Link } from 'react-router-dom';
import { FiArrowRight, FiHeart, FiTarget, FiEye } from 'react-icons/fi';

export default function AboutPage() {
  React.useEffect(() => { window.scrollTo(0, 0); }, []);

  return (
    <div className="landing-page">
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
        <div style={{ maxWidth: 800, margin: '0 auto', padding: '120px 24px 40px', textAlign: 'center' }}>
          <h1 className="hero-title" style={{ fontSize: 'clamp(2rem, 5vw, 3.2rem)' }}>
            About <span className="gradient-text">FashionBazzer</span>
          </h1>
          <p className="hero-subtitle">Democratizing affiliate marketing with automation.</p>
        </div>
      </div>

      <div style={{ maxWidth: 700, margin: '0 auto', padding: '0 24px 60px' }}>
        <div className="glass-card" style={{ padding: '32px', marginBottom: 20 }}>
          <h2 style={{ fontSize: '1.3rem', fontWeight: 700, marginBottom: 16 }}>Our Story</h2>
          <p style={{ color: 'var(--text-secondary)', lineHeight: 1.8, marginBottom: 16 }}>
            FashionBazzer was built to solve a simple problem: most affiliate marketers spend hours every day 
            creating content, scheduling posts, and tracking links. We realized that <strong>90% of this work 
            could be automated</strong> — so we built the engine that does exactly that.
          </p>
          <p style={{ color: 'var(--text-secondary)', lineHeight: 1.8 }}>
            What started as a side project for automating Telegram fashion channels has grown into a 
            full-fledged affiliate marketing engine powering <strong>24+ posts/day</strong> across 6 platforms. 
            All without any human involvement after initial setup.
          </p>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 16, marginBottom: 20 }}>
          {[
            { icon: FiTarget, title: 'Mission', desc: 'Make affiliate marketing accessible to everyone — no technical skills, no time investment, ₹0 startup cost.' },
            { icon: FiEye, title: 'Vision', desc: 'A world where anyone can build a passive income stream through fully automated social media marketing.' },
            { icon: FiHeart, title: 'Values', desc: 'Simplicity, automation, transparency. We believe in tools that do the work so you don\'t have to.' },
          ].map((item, i) => {
            const Icon = item.icon;
            return (
              <div key={i} className="glass-card" style={{ padding: '24px' }}>
                <div className="feature-icon" style={{ width: 48, height: 48, borderRadius: 12, background: 'rgba(255,60,172,0.15)', color: '#FF3CAC', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: 12 }}>
                  <Icon size={22} />
                </div>
                <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: 8 }}>{item.title}</h3>
                <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', lineHeight: 1.7 }}>{item.desc}</p>
              </div>
            );
          })}
        </div>

        <div className="glass-card" style={{ padding: '32px', textAlign: 'center' }}>
          <h2 style={{ fontSize: '1.3rem', fontWeight: 700, marginBottom: 12 }}>Made in India 🇮🇳</h2>
          <p style={{ color: 'var(--text-secondary)', lineHeight: 1.8, marginBottom: 16 }}>
            Built for the Indian fashion market. Optimized for Indian affiliate programs, 
            Indian engagement patterns, and Indian social media usage.
          </p>
          <Link to="/dashboard" className="btn btn-primary">
            Try It Free <FiArrowRight size={16} />
          </Link>
        </div>
      </div>
    </div>
  );
}

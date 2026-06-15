import React from 'react';
import { Link } from 'react-router-dom';
import { FiArrowRight, FiCheckCircle, FiClock } from 'react-icons/fi';

const STEPS = [
  {
    step: 'Step 1', icon: '🛍️', title: 'Connect Affiliate Accounts',
    desc: 'Sign up for Amazon Associates, Meesho Affiliate, and Flipkart Affiliate (free). Add your affiliate IDs to the settings page. That\'s it — no coding, no complex setup.',
    details: ['Amazon Associates ID', 'Meesho Affiliate ID', 'Flipkart Affiliate ID'],
  },
  {
    step: 'Step 2', icon: '🔄', title: 'Connect Social Media Accounts',
    desc: 'Create a Telegram channel, Instagram business account, Facebook page, Pinterest business account, and Twitter/X account. Generate API keys from each platform and enter them in settings.',
    details: ['Telegram Bot Token', 'Meta Graph API Token', 'Pinterest Access Token', 'Twitter API Keys'],
  },
  {
    step: 'Step 3', icon: '⚡', title: 'Run the Seed Pipeline',
    desc: 'One click seeds your database with trending products and generates the first batch of content. The scheduler takes over from here — scraping, generating, posting 24/7.',
    details: ['Scrape products from all platforms', 'Generate AI captions & images', 'Queue for auto-publishing'],
  },
  {
    step: 'Step 4', icon: '🤖', title: 'Fully Automated Operation',
    desc: 'The scheduler runs 11 automated jobs on IST timing. Products are scraped every 6 hours, content generated every 2 hours, and posts published 24+ times daily across all platforms.',
    details: ['11 automated jobs', '24+ posts/day', 'Smart content recycling', 'Auto health checks'],
  },
  {
    step: 'Step 5', icon: '📊', title: 'Track & Optimize',
    desc: 'Monitor clicks, conversions, and commissions in real-time. See which platforms and products perform best. Optimize by adjusting caption templates or adding new affiliate programs.',
    details: ['Real-time analytics dashboard', 'Commission tracking', 'Platform performance', 'Revenue reports'],
  },
];

const SCHEDULE = [
  { time: '3:00 AM', job: '🛍️ Scrape Products', desc: 'Amazon + Meesho trending dresses' },
  { time: '4:00 AM', job: '🔄 Recycle Content', desc: 'Refresh captions for existing products' },
  { time: '6:00 AM', job: '✈️ Post to Telegram', desc: 'Morning fashion feed' },
  { time: '8:00 AM', job: '📌 Post to Pinterest', desc: 'Morning pins' },
  { time: '9:00 AM', job: '📸 Instagram + 🐦 Twitter', desc: 'Visual + text posts' },
  { time: '10:00 AM', job: '👍 Facebook', desc: 'Page post' },
  { time: '12:00 PM', job: '✈️ Telegram + 📌 Pinterest', desc: 'Midday batch' },
  { time: '2:00 PM', job: '✈️ Telegram + 👍 Facebook', desc: 'Afternoon engagement' },
  { time: '3:00 PM', job: '🐦 Twitter + 🛍️ Scrape', desc: 'Tweet + product refresh' },
  { time: '5:00 PM', job: '📌 Pinterest', desc: 'Evening pins' },
  { time: '6:00 PM', job: '✈️ Telegram', desc: 'Evening feed' },
  { time: '7:00 PM', job: '👍 Facebook', desc: 'Evening page post' },
  { time: '8:00 PM', job: '✈️ Telegram + 📸 Instagram', desc: 'Prime time posts' },
  { time: '9:00 PM', job: '🐦 Twitter', desc: 'Night tweet' },
  { time: '10:00 PM', job: '✈️ Telegram + 📌 Pinterest', desc: 'Late night batch' },
  { time: '12:00 AM', job: '💰 Sync Commissions', desc: 'Daily earnings sync' },
];

export default function HowItWorksPage() {
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
          <Link to="/dashboard" className="btn btn-primary btn-sm">Launch Dashboard <FiArrowRight size={14} /></Link>
        </div>
      </nav>

      <div className="landing-hero" style={{ minHeight: 'auto', paddingBottom: 40 }}>
        <div style={{ maxWidth: 800, margin: '0 auto', padding: '120px 24px 40px', textAlign: 'center' }}>
          <h1 className="hero-title" style={{ fontSize: 'clamp(2rem, 5vw, 3.2rem)' }}>
            How It <span className="gradient-text">Works</span>
          </h1>
          <p className="hero-subtitle">5 simple steps to fully automated affiliate marketing — ₹0 setup, zero human work.</p>
        </div>
      </div>

      {/* Steps */}
      <div style={{ maxWidth: 800, margin: '0 auto', padding: '0 24px 60px' }}>
        {STEPS.map((s, i) => (
          <div key={i} className="glass-card" style={{ padding: '28px 32px', marginBottom: 16, position: 'relative' }}>
            <div style={{ display: 'flex', gap: 20, alignItems: 'flex-start', flexWrap: 'wrap' }}>
              <div style={{ fontSize: '2.5rem', lineHeight: 1 }}>{s.icon}</div>
              <div style={{ flex: 1, minWidth: 200 }}>
                <div style={{ fontSize: '0.75rem', color: 'var(--primary)', fontWeight: 600, marginBottom: 4, textTransform: 'uppercase', letterSpacing: '0.5px' }}>{s.step}</div>
                <h3 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: 8 }}>{s.title}</h3>
                <p style={{ color: 'var(--text-secondary)', lineHeight: 1.7, marginBottom: 12 }}>{s.desc}</p>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                  {s.details.map((d, j) => (
                    <span key={j} className="tag tag-primary"><FiCheckCircle size={12} /> {d}</span>
                  ))}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Daily Schedule */}
      <div className="landing-section landing-section-alt">
        <h2 className="section-heading">🗓️ Your Daily Schedule</h2>
        <p className="section-desc">24+ automated posts, 11 jobs — all running on IST. Here's a typical day:</p>
        <div style={{ maxWidth: 700, margin: '0 auto' }}>
          {SCHEDULE.map((s, i) => (
            <div key={i} style={{
              display: 'flex', gap: 16, padding: '10px 0',
              borderBottom: i < SCHEDULE.length - 1 ? '1px solid var(--border)' : 'none',
              alignItems: 'center',
            }}>
              <span style={{ minWidth: 80, fontSize: '0.8rem', color: 'var(--primary)', fontWeight: 600, fontFamily: 'monospace' }}>{s.time}</span>
              <span style={{ flex: 1, fontSize: '0.9rem' }}>{s.job}</span>
              <span className="schedule-desc" style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{s.desc}</span>
            </div>
          ))}
        </div>
      </div>

      <div style={{ textAlign: 'center', padding: '40px 24px 80px' }}>
        <Link to="/dashboard" className="btn btn-primary btn-lg">
          Get Started Now <FiArrowRight size={18} />
        </Link>
      </div>
    </div>
  );
}

import React from 'react';
import { Link } from 'react-router-dom';
import { FiArrowRight, FiCheck } from 'react-icons/fi';

const PLANS = [
  {
    name: 'Starter', price: '₹0', period: '/month', color: '#2B86C5',
    desc: 'Perfect for beginners testing the waters.',
    features: [
      { included: true, text: '1 Telegram channel' },
      { included: true, text: '9 posts/day' },
      { included: true, text: 'Auto product scraping' },
      { included: true, text: 'Basic analytics' },
      { included: true, text: 'Community support' },
      { included: false, text: 'Instagram posting' },
      { included: false, text: 'Facebook posting' },
      { included: false, text: 'Pinterest posting' },
      { included: false, text: 'Twitter/X posting' },
      { included: false, text: 'Threads posting' },
      { included: false, text: 'AI content generation' },
      { included: false, text: 'Commission tracking' },
      { included: false, text: 'Priority support' },
    ],
    popular: false,
  },
  {
    name: 'Growth', price: '₹499', period: '/month', color: '#FF3CAC',
    desc: 'For serious affiliates scaling up.',
    features: [
      { included: true, text: 'All 6 platforms' },
      { included: true, text: '24+ posts/day' },
      { included: true, text: 'Auto product scraping' },
      { included: true, text: 'AI content generation' },
      { included: true, text: 'Image composition' },
      { included: true, text: 'Real-time analytics' },
      { included: true, text: 'Commission tracking' },
      { included: true, text: 'Smart scheduling' },
      { included: true, text: 'Content recycling' },
      { included: true, text: 'Platform health checks' },
      { included: true, text: 'Email support' },
      { included: false, text: 'Custom branding' },
      { included: false, text: 'WhatsApp notifications' },
      { included: false, text: 'Priority API access' },
    ],
    popular: true,
  },
  {
    name: 'Pro', price: '₹999', period: '/month', color: '#00D4AA',
    desc: 'Maximum reach & revenue potential.',
    features: [
      { included: true, text: 'All 6 platforms' },
      { included: true, text: '40+ posts/day' },
      { included: true, text: 'Auto product scraping' },
      { included: true, text: 'Priority AI generation' },
      { included: true, text: 'Image composition' },
      { included: true, text: 'Advanced analytics' },
      { included: true, text: 'Commission tracking' },
      { included: true, text: 'Smart scheduling' },
      { included: true, text: 'Content recycling' },
      { included: true, text: 'Platform health checks' },
      { included: true, text: 'Custom branding on images' },
      { included: true, text: 'WhatsApp notifications' },
      { included: true, text: 'Priority API access' },
      { included: true, text: 'Priority support (24h)' },
      { included: true, text: 'Early access to new features' },
    ],
    popular: false,
  },
];

export default function PricingPage() {
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
          <div className="hero-badge">💰 Simple Pricing</div>
          <h1 className="hero-title" style={{ fontSize: 'clamp(2rem, 5vw, 3.2rem)' }}>
            Start Free, <span className="gradient-text">Scale Up</span>
          </h1>
          <p className="hero-subtitle">No hidden fees. No contracts. Cancel anytime.</p>
        </div>
      </div>

      <div className="pricing-grid" style={{ maxWidth: 1100, margin: '0 auto', padding: '0 24px 60px' }}>
        {PLANS.map((plan, i) => (
          <div key={i} className={`pricing-card glass-card ${plan.popular ? 'popular' : ''}`}>
            {plan.popular && <div className="popular-badge">Most Popular</div>}
            <h3 className="pricing-name">{plan.name}</h3>
            <div className="pricing-amount">
              <span className="pricing-price">{plan.price}</span>
              <span className="pricing-period">{plan.period}</span>
            </div>
            <p className="pricing-desc">{plan.desc}</p>
            <ul className="pricing-features">
              {plan.features.map((f, j) => (
                <li key={j} className={f.included ? '' : 'muted'}>
                  <FiCheck size={14} color={f.included ? plan.color : 'var(--text-muted)'} />
                  {f.text}
                </li>
              ))}
            </ul>
            <Link to="/dashboard" className={`btn ${plan.popular ? 'btn-primary' : 'btn-secondary'}`} style={{ width: '100%', justifyContent: 'center' }}>
              {plan.name === 'Starter' ? 'Get Started Free' : `Start ${plan.name}`}
            </Link>
          </div>
        ))}
      </div>
    </div>
  );
}

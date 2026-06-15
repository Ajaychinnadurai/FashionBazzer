import React from 'react';
import { Link } from 'react-router-dom';
import {
  FiArrowRight, FiCheck, FiStar, FiTrendingUp, FiClock, FiSmartphone,
  FiShield, FiSend, FiBarChart2, FiGrid, FiDollarSign, FiMail,
  FiMessageCircle, FiInstagram, FiTwitter, FiFacebook, FiGithub,
  FiChevronRight, FiPlay, FiBookOpen, FiZap, FiUsers, FiAward,
} from 'react-icons/fi';

/* ──────────────────────────────────────────────
   SECTION COMPONENTS
   ────────────────────────────────────────────── */

function NavBar() {
  const [scrolled, setScrolled] = React.useState(false);
  const [mobileOpen, setMobileOpen] = React.useState(false);

  React.useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 40);
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  return (
    <nav style={{
      position: 'fixed', top: 0, left: 0, right: 0, zIndex: 1000,
      padding: scrolled ? '12px 24px' : '20px 24px',
      background: scrolled ? 'rgba(13,13,13,0.92)' : 'transparent',
      backdropFilter: scrolled ? 'blur(20px)' : 'none',
      borderBottom: scrolled ? '1px solid rgba(255,255,255,0.06)' : '1px solid transparent',
      transition: 'all 0.3s ease',
      display: 'flex', alignItems: 'center', justifyContent: 'space-between',
    }}>
      <Link to="/" style={{ display: 'flex', alignItems: 'center', gap: 10, textDecoration: 'none' }}>
        <span style={{ fontSize: '1.8rem' }}>👗</span>
        <span style={{
          fontSize: '1.2rem', fontWeight: 800,
          background: 'var(--gradient)', WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
        }}>
          FashionBazzer
        </span>
      </Link>

      {/* Desktop nav */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
        <div className="landing-nav-links" style={{
          display: 'flex', alignItems: 'center', gap: 4,
        }}>
          {[
            { to: '/features', label: 'Features' },
            { to: '/how-it-works', label: 'How It Works' },
            { to: '/pricing', label: 'Pricing' },
            { to: '/about', label: 'About' },
            { to: '/contact', label: 'Contact' },
          ].map(link => (
            <Link key={link.to} to={link.to} className="nav-link">
              {link.label}
            </Link>
          ))}
        </div>

        <Link to="/dashboard" className="btn btn-primary btn-sm" style={{ marginLeft: 12 }}>
          Dashboard <FiArrowRight size={14} />
        </Link>

        {/* Mobile toggle */}
        <button
          onClick={() => setMobileOpen(!mobileOpen)}
          className="mobile-menu-btn"
          style={{
            display: 'none', background: 'none', border: 'none',
            color: 'white', fontSize: '1.5rem', cursor: 'pointer', padding: 8,
          }}
        >
          {mobileOpen ? '✕' : '☰'}
        </button>
      </div>

      {/* Mobile menu */}
      {mobileOpen && (
        <div style={{
          position: 'fixed', top: 70, left: 0, right: 0,
          background: 'rgba(13,13,13,0.98)', backdropFilter: 'blur(20px)',
          borderBottom: '1px solid var(--border)', padding: '16px 24px',
          display: 'flex', flexDirection: 'column', gap: 12,
        }}>
          {[
            { to: '/features', label: 'Features' },
            { to: '/how-it-works', label: 'How It Works' },
            { to: '/pricing', label: 'Pricing' },
            { to: '/about', label: 'About' },
            { to: '/contact', label: 'Contact' },
            { to: '/dashboard', label: 'Dashboard →' },
          ].map(link => (
            <Link key={link.to} to={link.to}
              onClick={() => setMobileOpen(false)}
              style={{ color: 'var(--text)', textDecoration: 'none', padding: '8px 0', fontSize: '1rem' }}
            >
              {link.label}
            </Link>
          ))}
        </div>
      )}
    </nav>
  );
}

/* ── Hero ── */
function HeroSection() {
  return (
    <section className="landing-hero">
      <div className="hero-bg-glow" />
      <div style={{ position: 'relative', zIndex: 2, maxWidth: 1200, margin: '0 auto', padding: '160px 24px 80px', textAlign: 'center' }}>
        <div className="hero-badge">
          <FiZap size={12} /> Fully Automated — Zero Human Work
        </div>

        <h1 className="hero-title">
          Your AI-Powered{' '}
          <span className="gradient-text">Affiliate Marketing</span>{' '}
          Engine
        </h1>

        <p className="hero-subtitle">
          Auto-scrape trending dresses, generate AI captions + images, and post to{' '}
          <strong>6 platforms</strong> —<br />
          <strong>24+ times a day</strong>. ₹0 setup cost. No human involvement.
        </p>

        <div className="hero-cta">
          <Link to="/dashboard" className="btn btn-primary btn-lg">
            Launch Dashboard <FiArrowRight size={18} />
          </Link>
          <Link to="/how-it-works" className="btn btn-secondary btn-lg">
            <FiPlay size={16} /> See How It Works
          </Link>
        </div>

        {/* Stats bar */}
        <div className="hero-stats">
          {[
            { value: '24+', label: 'Posts / Day' },
            { value: '6', label: 'Platforms' },
            { value: '₹0', label: 'Setup Cost' },
            { value: '11', label: 'Auto Jobs' },
          ].map((s, i) => (
            <div key={i} className="hero-stat-item">
              <div className="hero-stat-value">{s.value}</div>
              <div className="hero-stat-label">{s.label}</div>
            </div>
          ))}
        </div>

        {/* Platform logos */}
        <div className="platform-bar">
          <span className="platform-bar-label">Posts to</span>
          <div className="platform-icons">
            {[
              { icon: '✈️', name: 'Telegram' },
              { icon: '📸', name: 'Instagram' },
              { icon: '👍', name: 'Facebook' },
              { icon: '📌', name: 'Pinterest' },
              { icon: '🐦', name: 'Twitter/X' },
              { icon: '🧵', name: 'Threads' },
            ].map((p, i) => (
              <div key={i} className="platform-chip">
                <span>{p.icon}</span> {p.name}
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}

/* ── Features Grid ── */
function FeaturesSection() {
  const features = [
    { icon: FiGrid, title: 'Auto Product Scraping', desc: 'Scrapes trending dresses from Amazon, Meesho & Flipkart every 6 hours. Always fresh inventory.', color: '#FF3CAC' },
    { icon: FiStar, title: 'AI Content Generation', desc: 'Gen Z captions, hashtags, and taglines via HuggingFace AI. 8 rotating styles — never repetitive.', color: '#784BA0' },
    { icon: FiSend, title: '6-Platform Auto Posting', desc: '25 posts/day across Telegram, Instagram, Facebook, Pinterest, Twitter & Threads. Set & forget.', color: '#2B86C5' },
    { icon: FiTrendingUp, title: 'Smart Scheduling', desc: 'IST-optimized posting times for max engagement. Posts during peak Indian browsing hours.', color: '#00D4AA' },
    { icon: FiBarChart2, title: 'Real-Time Analytics', desc: 'Track clicks, conversions, commissions, and platform health — all from one dashboard.', color: '#FFB800' },
    { icon: FiDollarSign, title: 'Commission Tracking', desc: 'Auto-sync earnings from all affiliate networks. See exactly how much you\'re making.', color: '#FF3CAC' },
    { icon: FiClock, title: 'Content Recycling', desc: 'Never run out of posts. Smart recycling re-generates content for existing products when queue is low.', color: '#784BA0' },
    { icon: FiShield, title: 'Platform Health Checks', desc: 'Automatically tests all API connections every 30 minutes. Get alerts when something breaks.', color: '#2B86C5' },
  ];

  return (
    <section className="landing-section" id="features">
      <div className="section-label">Everything Automated</div>
      <h2 className="section-heading">What FashionBazzer Does</h2>
      <p className="section-desc">11 automated jobs working 24/7 to grow your affiliate income — zero human effort required.</p>

      <div className="features-grid">
        {features.map((f, i) => {
          const Icon = f.icon;
          return (
            <div key={i} className="feature-card glass-card">
              <div className="feature-icon" style={{ background: `${f.color}20`, color: f.color }}>
                <Icon size={24} />
              </div>
              <h3 className="feature-title">{f.title}</h3>
              <p className="feature-desc">{f.desc}</p>
            </div>
          );
        })}
      </div>
    </section>
  );
}

/* ── How It Works ── */
function HowItWorksSection() {
  const steps = [
    { step: '01', title: 'Scrape', desc: 'Every 6 hours, FashionBazzer scrapes Amazon, Meesho & Flipkart for trending dresses under ₹1,500.', icon: '🛍️' },
    { step: '02', title: 'Generate', desc: 'AI creates platform-specific captions, hashtags, and composes beautiful 1080×1080 product images.', icon: '🤖' },
    { step: '03', title: 'Schedule', desc: 'Posts are queued and scheduled at peak engagement times — 24+ times per day across all 6 platforms.', icon: '📅' },
    { step: '04', title: 'Post & Earn', desc: 'Auto-posted to your channels. Track clicks, conversions, and commissions in real-time. Rinse & repeat.', icon: '💰' },
  ];

  return (
    <section className="landing-section landing-section-alt" id="how-it-works">
      <div className="section-label">Simple 4-Step Pipeline</div>
      <h2 className="section-heading">How It Works</h2>
      <p className="section-desc">From scraping to earning — completely automated. Here's the magic behind the scenes.</p>

      <div className="steps-container">
        {steps.map((s, i) => (
          <div key={i} className="step-row">
            <div className="step-content">
              <span className="step-number">{s.step}</span>
              <span className="step-icon">{s.icon}</span>
              <h3 className="step-title">{s.title}</h3>
              <p className="step-desc">{s.desc}</p>
            </div>
            {i < steps.length - 1 && (
              <div className="step-connector">
                <FiChevronRight size={24} />
              </div>
            )}
          </div>
        ))}
      </div>

      <div style={{ textAlign: 'center', marginTop: 40 }}>
        <Link to="/how-it-works" className="btn btn-secondary">
          <FiBookOpen size={16} /> Read Full Documentation
        </Link>
      </div>
    </section>
  );
}

/* ── Pricing ── */
function PricingSection() {
  const plans = [
    {
      name: 'Starter', price: '₹0', period: '/month', desc: 'Perfect for beginners testing the waters.',
      features: ['1 Telegram channel', '9 posts/day', 'Auto product scraping', 'Basic analytics', 'Community support'],
      cta: 'Get Started', popular: false, color: '#2B86C5',
    },
    {
      name: 'Growth', price: '₹499', period: '/month', desc: 'For serious affiliates scaling up.',
      features: ['All 6 platforms', '24+ posts/day', 'AI content generation', 'Real-time analytics', 'Commission tracking', 'Email support'],
      cta: 'Start Free Trial', popular: true, color: '#FF3CAC',
    },
    {
      name: 'Pro', price: '₹999', period: '/month', desc: 'Maximum reach & revenue potential.',
      features: ['All 6 platforms', '40+ posts/day', 'Priority AI generation', 'Advanced analytics', 'WhatsApp notifications', 'Priority support', 'Custom branding'],
      cta: 'Go Pro', popular: false, color: '#00D4AA',
    },
  ];

  return (
    <section className="landing-section" id="pricing">
      <div className="section-label">Simple Pricing</div>
      <h2 className="section-heading">Start Free, Scale Up</h2>
      <p className="section-desc">No hidden fees. No contracts. Upgrade when you're ready to scale.</p>

      <div className="pricing-grid">
        {plans.map((plan, i) => (
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
                <li key={j}><FiCheck size={14} color={plan.color} /> {f}</li>
              ))}
            </ul>
            <Link to="/contact" className={`btn ${plan.popular ? 'btn-primary' : 'btn-secondary'}`} style={{ width: '100%' }}>
              {plan.cta}
            </Link>
          </div>
        ))}
      </div>
    </section>
  );
}

/* ── Newsletter ── */
function NewsletterSection() {
  const [email, setEmail] = React.useState('');
  const [status, setStatus] = React.useState('idle'); // idle | loading | success | error

  async function handleSubmit(e) {
    e.preventDefault();
    if (!email) return;
    setStatus('loading');
    try {
      const api = (await import('../services/api')).default;
      await api.post('/marketing/subscribe/', { email });
      setStatus('success');
      setEmail('');
      setTimeout(() => setStatus('idle'), 4000);
    } catch {
      setStatus('error');
      setTimeout(() => setStatus('idle'), 3000);
    }
  }

  return (
    <section className="landing-section landing-section-alt">
      <div className="newsletter-card">
        <div className="newsletter-content">
          <FiMail size={32} color="#FF3CAC" />
          <h2>Stay Ahead of the Curve</h2>
          <p>Get tips, updates, and new platform integrations delivered to your inbox.</p>

          <form onSubmit={handleSubmit} className="newsletter-form">
            <input
              type="email"
              placeholder="your@email.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="newsletter-input"
            />
            <button type="submit" className="btn btn-primary" disabled={status === 'loading'}>
              {status === 'loading' ? 'Subscribing…' : 'Subscribe'}
            </button>
          </form>

          {status === 'success' && (
            <div className="newsletter-feedback success">✅ You're subscribed! Welcome aboard.</div>
          )}
          {status === 'error' && (
            <div className="newsletter-feedback error">❌ Something went wrong. Try again later.</div>
          )}

          <span className="newsletter-note">No spam. Unsubscribe anytime.</span>
        </div>
      </div>
    </section>
  );
}

/* ── FAQ ── */
function FAQSection() {
  const [open, setOpen] = React.useState(null);
  const faqs = [
    { q: 'Do I need any technical skills?', a: 'Zero. The dashboard is point-and-click. Connect your affiliate IDs and social accounts, and everything runs automatically.' },
    { q: 'Which platforms do you support?', a: 'Telegram, Instagram, Facebook, Pinterest, Twitter/X, and Threads. More platforms coming soon.' },
    { q: 'How much can I earn?', a: 'With 24+ posts/day driving traffic to affiliate links, users report ₹500–₹2,000 in month 1, scaling to ₹30,000+ by month 6.' },
    { q: 'Do I need API keys for everything?', a: 'Most features work with free tiers. Telegram, Meta, and Pinterest APIs are free. AI generation uses HuggingFace\'s free inference API.' },
    { q: 'Can I customize the captions?', a: 'Yes! Each platform has 3–8 caption template styles. You can edit the templates or add your own branding.' },
    { q: 'What if a platform connection breaks?', a: 'The system checks all connections every 30 minutes and logs errors. You\'ll see the status clearly in the dashboard.' },
  ];

  return (
    <section className="landing-section" id="faq">
      <div className="section-label">Got Questions?</div>
      <h2 className="section-heading">Frequently Asked</h2>

      <div className="faq-list">
        {faqs.map((faq, i) => (
          <div key={i} className={`faq-item ${open === i ? 'open' : ''}`} onClick={() => setOpen(open === i ? null : i)}>
            <div className="faq-question">
              <span>{faq.q}</span>
              <span className="faq-arrow">{open === i ? '−' : '+'}</span>
            </div>
            {open === i && <div className="faq-answer">{faq.a}</div>}
          </div>
        ))}
      </div>
    </section>
  );
}

/* ── Footer ── */
function Footer() {
  return (
    <footer className="landing-footer">
      <div className="footer-grid">
        <div className="footer-brand">
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 16 }}>
            <span style={{ fontSize: '1.5rem' }}>👗</span>
            <span style={{ fontSize: '1.1rem', fontWeight: 800, background: 'var(--gradient)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
              FashionBazzer
            </span>
          </div>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', lineHeight: 1.7, maxWidth: 300 }}>
            Fully automated affiliate marketing engine for trending dresses. Zero human work, 24+ posts/day.
          </p>
          <div className="footer-social" style={{ display: 'flex', gap: 8, marginTop: 16 }}>
            {[
              { icon: FiInstagram, href: '#' },
              { icon: FiTwitter, href: '#' },
              { icon: FiFacebook, href: '#' },
              { icon: FiGithub, href: '#' },
            ].map((Social, i) => (
              <a key={i} href={Social.href} className="social-link" target="_blank" rel="noreferrer">
                <Social.icon size={16} />
              </a>
            ))}
          </div>
        </div>

        <div className="footer-links">
          <h4>Product</h4>
          <Link to="/features">Features</Link>
          <Link to="/how-it-works">How It Works</Link>
          <Link to="/pricing">Pricing</Link>
          <Link to="/dashboard">Dashboard</Link>
        </div>

        <div className="footer-links">
          <h4>Company</h4>
          <Link to="/about">About Us</Link>
          <Link to="/contact">Contact</Link>
          <a href="#">Privacy Policy</a>
          <a href="#">Terms of Service</a>
        </div>

        <div className="footer-links">
          <h4>Platforms</h4>
          <span>Telegram</span>
          <span>Instagram</span>
          <span>Facebook</span>
          <span>Pinterest</span>
        </div>
      </div>

      <div className="footer-bottom">
        <span>© {new Date().getFullYear()} FashionBazzer. Built with ❤️ for affiliate marketers.</span>
        <span>Made in India 🇮🇳</span>
      </div>
    </footer>
  );
}

/* ── WhatsApp Floating Button ── */
function WhatsAppButton() {
  const phone = '911234567890'; // placeholder — user should set their own
  const message = encodeURIComponent(
    'Hey! I just checked out FashionBazzer — an AI-powered affiliate marketing engine. Want to see how it works? 👗🔥'
  );

  return (
    <a
      href={`https://wa.me/${phone}?text=${message}`}
      target="_blank"
      rel="noreferrer"
      className="whatsapp-fab"
      title="Chat with us on WhatsApp"
    >
      <FiMessageCircle size={28} />
    </a>
  );
}

/* ──────────────────────────────────────────────
   MAIN LANDING PAGE
   ────────────────────────────────────────────── */
export default function Landing() {
  React.useEffect(() => {
    window.scrollTo(0, 0);
  }, []);

  return (
    <div className="landing-page">
      <NavBar />
      <HeroSection />
      <FeaturesSection />
      <HowItWorksSection />
      <PricingSection />
      <NewsletterSection />
      <FAQSection />
      <Footer />
      <WhatsAppButton />
    </div>
  );
}

import React from 'react';
import { Link } from 'react-router-dom';
import { FiArrowRight, FiMail, FiMessageCircle, FiTwitter, FiSend } from 'react-icons/fi';
import toast from 'react-hot-toast';

export default function ContactPage() {
  React.useEffect(() => { window.scrollTo(0, 0); }, []);

  const [form, setForm] = React.useState({ name: '', email: '', message: '' });
  const [sending, setSending] = React.useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    if (!form.name || !form.email || !form.message) return;
    setSending(true);
    try {
      const api = (await import('../services/api')).default;
      await api.post('/marketing/contact/', form);
      toast.success('Message sent! We\'ll get back to you soon.');
      setForm({ name: '', email: '', message: '' });
    } catch {
      toast.error('Failed to send. Try emailing us directly.');
    } finally {
      setSending(false);
    }
  }

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
            Get in <span className="gradient-text">Touch</span>
          </h1>
          <p className="hero-subtitle">Have a question or need help? We're here for you.</p>
        </div>
      </div>

      <div style={{ maxWidth: 700, margin: '0 auto', padding: '0 24px 60px', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24 }}>
        {/* Contact form */}
        <div className="glass-card" style={{ padding: '28px' }}>
          <h3 style={{ fontSize: '1.1rem', fontWeight: 600, marginBottom: 20 }}>Send us a message</h3>
          <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
            <input
              type="text" placeholder="Your name" value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
              required
              className="newsletter-input"
            />
            <input
              type="email" placeholder="your@email.com" value={form.email}
              onChange={(e) => setForm({ ...form, email: e.target.value })}
              required
              className="newsletter-input"
            />
            <textarea
              placeholder="Tell us what's on your mind..."
              value={form.message} rows={4}
              onChange={(e) => setForm({ ...form, message: e.target.value })}
              required
              className="newsletter-input"
              style={{ resize: 'vertical', minHeight: 100, fontFamily: 'Inter, sans-serif' }}
            />
            <button type="submit" className="btn btn-primary" disabled={sending}>
              <FiSend size={14} /> {sending ? 'Sending…' : 'Send Message'}
            </button>
          </form>
        </div>

        {/* Contact info */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          {[
            { icon: FiMail, label: 'Email', value: 'hello@fashionbazzer.com', action: 'Send an email' },
            { icon: FiMessageCircle, label: 'WhatsApp', value: '+91 12345 67890', action: 'Chat on WhatsApp' },
            { icon: FiTwitter, label: 'Twitter/X', value: '@fashionbazzer', action: 'Follow us' },
          ].map((item, i) => (
            <div key={i} className="glass-card" style={{ padding: '20px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 8 }}>
                <item.icon size={20} color="#FF3CAC" />
                <span style={{ fontWeight: 600 }}>{item.label}</span>
              </div>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: 8 }}>{item.value}</p>
              <span style={{ color: 'var(--primary)', fontSize: '0.85rem', cursor: 'pointer' }}>{item.action} →</span>
            </div>
          ))}

          <div className="glass-card" style={{ padding: '20px', textAlign: 'center' }}>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>
              ⏱️ We typically respond within 24 hours on business days.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

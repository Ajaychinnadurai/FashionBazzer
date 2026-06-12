import React from 'react';
import { FiSave, FiClock, FiCalendar, FiDollarSign } from 'react-icons/fi';
import toast from 'react-hot-toast';

export default function Settings() {
  const [settings, setSettings] = React.useState({
    siteName: 'FashionBazzer',
    postsPerDay: 19,
    minRating: '4.0',
    maxPrice: '1500',
    minReviews: '50',
    timezone: 'Asia/Kolkata',
    autoPost: true,
    generateContent: true,
  });

  function handleChange(key, value) {
    setSettings(prev => ({ ...prev, [key]: value }));
  }

  function handleSave() {
    toast.success('Settings saved! ✅');
  }

  return (
    <div style={{ maxWidth: 600 }}>
      <div className="glass-card" style={{ padding: '24px' }}>
        <h3 style={{ fontSize: '1.1rem', fontWeight: 600, marginBottom: 24 }}>
          ⚙️ General Settings
        </h3>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
          {/* Site Name */}
          <div>
            <label style={{ display: 'block', fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: 6 }}>
              Site Name
            </label>
            <input
              type="text"
              value={settings.siteName}
              onChange={(e) => handleChange('siteName', e.target.value)}
              style={inputStyle}
            />
          </div>

          {/* Posts Per Day */}
          <div>
            <label style={{ display: 'block', fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: 6 }}>
              <FiClock size={14} style={{ marginRight: 4 }} /> Posts Per Day
            </label>
            <input
              type="number"
              value={settings.postsPerDay}
              onChange={(e) => handleChange('postsPerDay', parseInt(e.target.value))}
              style={inputStyle}
            />
          </div>

          {/* Min Rating */}
          <div>
            <label style={{ display: 'block', fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: 6 }}>
              ⭐ Minimum Rating
            </label>
            <input
              type="number"
              step="0.1"
              value={settings.minRating}
              onChange={(e) => handleChange('minRating', e.target.value)}
              style={inputStyle}
            />
          </div>

          {/* Max Price */}
          <div>
            <label style={{ display: 'block', fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: 6 }}>
              💰 Max Product Price (₹)
            </label>
            <input
              type="number"
              value={settings.maxPrice}
              onChange={(e) => handleChange('maxPrice', e.target.value)}
              style={inputStyle}
            />
          </div>

          {/* Min Reviews */}
          <div>
            <label style={{ display: 'block', fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: 6 }}>
              👥 Minimum Reviews
            </label>
            <input
              type="number"
              value={settings.minReviews}
              onChange={(e) => handleChange('minReviews', e.target.value)}
              style={inputStyle}
            />
          </div>

          {/* Toggles */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            <ToggleOption
              label="Auto-publish posts"
              checked={settings.autoPost}
              onChange={(v) => handleChange('autoPost', v)}
            />
            <ToggleOption
              label="Auto-generate AI content"
              checked={settings.generateContent}
              onChange={(v) => handleChange('generateContent', v)}
            />
          </div>
        </div>

        <button className="btn btn-primary" onClick={handleSave} style={{ marginTop: 24, width: '100%' }}>
          <FiSave size={16} /> Save Settings
        </button>
      </div>
    </div>
  );
}

function ToggleOption({ label, checked, onChange }) {
  return (
    <div style={{
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '10px 12px',
      borderRadius: 8,
      background: 'rgba(255,255,255,0.03)',
    }}>
      <span style={{ fontSize: '0.9rem' }}>{label}</span>
      <button
        onClick={() => onChange(!checked)}
        style={{
          width: 48,
          height: 26,
          borderRadius: 13,
          border: 'none',
          background: checked ? 'var(--success)' : 'rgba(255,255,255,0.15)',
          cursor: 'pointer',
          position: 'relative',
          transition: 'var(--transition)',
          boxShadow: 'inset 0 1px 3px rgba(0,0,0,0.3)',
        }}
      >
        <div style={{
          width: 20,
          height: 20,
          borderRadius: '50%',
          background: '#fff',
          position: 'absolute',
          top: 3,
          left: checked ? 26 : 2,
          transition: 'var(--transition)',
          boxShadow: '0 1px 3px rgba(0,0,0,0.3)',
        }} />
      </button>
    </div>
  );
}

const inputStyle = {
  width: '100%',
  background: 'rgba(255,255,255,0.05)',
  border: '1px solid var(--border)',
  borderRadius: 'var(--radius-sm)',
  color: 'var(--text)',
  padding: '10px 14px',
  fontSize: '0.9rem',
  outline: 'none',
  fontFamily: 'Inter',
  transition: 'var(--transition)',
};

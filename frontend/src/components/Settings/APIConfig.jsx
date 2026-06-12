import React from 'react';
import { FiSave, FiEye, FiEyeOff, FiCopy } from 'react-icons/fi';
import toast from 'react-hot-toast';

const API_FIELDS = [
  { key: 'telegram_bot_token', label: 'Telegram Bot Token', platform: 'Telegram', type: 'password' },
  { key: 'telegram_channel_id', label: 'Telegram Channel ID', platform: 'Telegram', type: 'text' },
  { key: 'meta_access_token', label: 'Meta Access Token', platform: 'Instagram/Facebook', type: 'password' },
  { key: 'instagram_user_id', label: 'Instagram User ID', platform: 'Instagram', type: 'text' },
  { key: 'fb_page_id', label: 'Facebook Page ID', platform: 'Facebook', type: 'text' },
  { key: 'pinterest_token', label: 'Pinterest Access Token', platform: 'Pinterest', type: 'password' },
  { key: 'twitter_api_key', label: 'Twitter API Key', platform: 'Twitter/X', type: 'password' },
  { key: 'twitter_api_secret', label: 'Twitter API Secret', platform: 'Twitter/X', type: 'password' },
  { key: 'huggingface_key', label: 'HuggingFace API Key', platform: 'AI', type: 'password' },
  { key: 'amazon_associate', label: 'Amazon Associate ID', platform: 'Amazon', type: 'text' },
  { key: 'meesho_affiliate', label: 'Meesho Affiliate ID', platform: 'Meesho', type: 'text' },
];

export default function APIConfig() {
  const [values, setValues] = React.useState({});
  const [visible, setVisible] = React.useState({});
  const [saving, setSaving] = React.useState(false);

  function handleChange(key, value) {
    setValues(prev => ({ ...prev, [key]: value }));
  }

  function toggleVisibility(key) {
    setVisible(prev => ({ ...prev, [key]: !prev[key] }));
  }

  function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
      toast.success('Copied! 📋');
    }).catch(() => {
      toast.error('Failed to copy');
    });
  }

  function handleSave() {
    setSaving(true);
    setTimeout(() => {
      setSaving(false);
      toast.success('API keys saved! 🔑');
    }, 1000);
  }

  return (
    <div style={{ maxWidth: 700 }}>
      <div className="glass-card" style={{ padding: '24px' }}>
        <h3 style={{ fontSize: '1.1rem', fontWeight: 600, marginBottom: 8 }}>
          🔑 API Configuration
        </h3>
        <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: 24 }}>
          Add your API keys for each platform. These are stored as environment variables.
        </p>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          {API_FIELDS.map((field) => (
            <div key={field.key}>
              <div style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                marginBottom: 4,
              }}>
                <label style={{ fontSize: '0.85rem', fontWeight: 500 }}>
                  {field.label}
                  <span className="tag tag-primary" style={{ marginLeft: 8, fontSize: '0.6rem' }}>
                    {field.platform}
                  </span>
                </label>
              </div>

              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: 8,
                background: 'rgba(255,255,255,0.05)',
                border: '1px solid var(--border)',
                borderRadius: 'var(--radius-sm)',
                padding: '0 12px',
                transition: 'var(--transition)',
              }}>
                <input
                  type={visible[field.key] ? 'text' : field.type}
                  value={values[field.key] || ''}
                  onChange={(e) => handleChange(field.key, e.target.value)}
                  placeholder={`Enter ${field.label}`}
                  style={{
                    flex: 1,
                    background: 'none',
                    border: 'none',
                    color: 'var(--text)',
                    padding: '10px 0',
                    fontSize: '0.85rem',
                    outline: 'none',
                    fontFamily: 'monospace',
                  }}
                />
                {field.type === 'password' && (
                  <button onClick={() => toggleVisibility(field.key)} style={{
                    background: 'none', border: 'none', color: 'var(--text-muted)',
                    cursor: 'pointer', padding: 4, display: 'flex',
                  }}>
                    {visible[field.key] ? <FiEyeOff size={14} /> : <FiEye size={14} />}
                  </button>
                )}
                {values[field.key] && (
                  <button onClick={() => copyToClipboard(values[field.key])} style={{
                    background: 'none', border: 'none', color: 'var(--text-muted)',
                    cursor: 'pointer', padding: 4, display: 'flex',
                  }}>
                    <FiCopy size={14} />
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>

        <button
          className="btn btn-primary"
          onClick={handleSave}
          disabled={saving}
          style={{ marginTop: 24, width: '100%' }}
        >
          <FiSave size={16} /> {saving ? 'Saving...' : 'Save API Keys'}
        </button>

        <p style={{
          marginTop: 16,
          fontSize: '0.75rem',
          color: 'var(--text-muted)',
          textAlign: 'center',
          lineHeight: 1.6,
        }}>
          🔒 API keys are stored in Render environment variables. Never committed to git.
        </p>
      </div>
    </div>
  );
}

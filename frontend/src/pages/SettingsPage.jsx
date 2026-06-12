import React from 'react';
import Settings from '../components/Settings/Settings';
import APIConfig from '../components/Settings/APIConfig';
import PlatformToggle from '../components/Platforms/PlatformToggle';
import { FiSettings, FiKey, FiToggleLeft } from 'react-icons/fi';

export default function SettingsPage() {
  const [tab, setTab] = React.useState('general');

  return (
    <div className="fade-in" style={{ paddingBottom: 40 }}>
      <div className="page-header">
        <div>
          <h1>⚙️ Settings</h1>
          <p>Configure your FashionBazzer affiliate engine</p>
        </div>
      </div>

      {/* Tab Navigation */}
      <div style={{
        display: 'flex',
        gap: 4,
        padding: '16px 24px',
        borderBottom: '1px solid var(--border)',
      }}>
        {[
          { key: 'general', label: 'General', icon: FiSettings },
          { key: 'api', label: 'API Keys', icon: FiKey },
          { key: 'platforms', label: 'Platforms', icon: FiToggleLeft },
        ].map((t) => {
          const Icon = t.icon;
          return (
            <button
              key={t.key}
              onClick={() => setTab(t.key)}
              className={`btn btn-sm ${tab === t.key ? 'btn-primary' : 'btn-secondary'}`}
            >
              <Icon size={14} /> {t.label}
            </button>
          );
        })}
      </div>

      {/* Tab Content */}
      <div style={{ padding: '24px' }}>
        {tab === 'general' && <Settings />}
        {tab === 'api' && <APIConfig />}
        {tab === 'platforms' && (
          <div style={{ maxWidth: 500 }}>
            <div className="glass-card" style={{ padding: '24px' }}>
              <h3 style={{ fontSize: '1.1rem', fontWeight: 600, marginBottom: 20 }}>
                🔄 Platform Toggle
              </h3>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: 20 }}>
                Enable or disable specific social platforms for auto-posting.
              </p>
              <PlatformToggle />
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

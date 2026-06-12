import React from 'react';
import PostQueue from '../components/Posts/PostQueue';
import PostHistory from '../components/Posts/PostHistory';
import { FiClock, FiCheckCircle, FiSend } from 'react-icons/fi';

export default function PostsPage() {
  const [tab, setTab] = React.useState('queue');

  return (
    <div className="fade-in">
      <div className="page-header">
        <div>
          <h1>📤 Posts & Queue</h1>
          <p>Manage your automated social media posts — 19 posts/day</p>
        </div>
      </div>

      {/* Tab Switcher */}
      <div style={{
        display: 'flex',
        gap: 4,
        padding: '16px 24px',
        borderBottom: '1px solid var(--border)',
      }}>
        {[
          { key: 'queue', label: 'Post Queue', icon: FiClock },
          { key: 'history', label: 'History', icon: FiCheckCircle },
          { key: 'preview', label: 'Preview', icon: FiSend },
        ].map((tabItem) => {
          const Icon = tabItem.icon;
          return (
            <button
              key={tabItem.key}
              onClick={() => setTab(tabItem.key)}
              className={`btn btn-sm ${tab === tabItem.key ? 'btn-primary' : 'btn-secondary'}`}
            >
              <Icon size={14} /> {tabItem.label}
            </button>
          );
        })}
      </div>

      {/* Tab Content */}
      <div style={{ marginTop: 8 }}>
        {tab === 'queue' && <PostQueue />}
        {tab === 'history' && (
          <div style={{ padding: '24px' }}>
            <h2 className="section-title">
              <span className="icon">📜</span> Post History
            </h2>
            <PostHistory />
          </div>
        )}
        {tab === 'preview' && (
          <div style={{ padding: '24px' }}>
            <div className="glass-card" style={{ padding: '24px', textAlign: 'center' }}>
              <div style={{ fontSize: '3rem', marginBottom: 16 }}>👁️</div>
              <h3 style={{ marginBottom: 8 }}>Post Preview</h3>
              <p style={{ color: 'var(--text-muted)', marginBottom: 16 }}>
                Select a post from the queue to preview how it will look on each platform.
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

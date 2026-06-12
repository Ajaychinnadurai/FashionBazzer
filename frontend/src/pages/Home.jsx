import React from 'react';
import Dashboard from '../components/Dashboard/Dashboard';
import PlatformStatus from '../components/Platforms/PlatformStatus';

export default function Home() {
  return (
    <div className="fade-in" style={{ paddingBottom: 40 }}>
      <div className="page-header">
        <div>
          <h1>👋 Dashboard Overview</h1>
          <p>Your FashionBazzer affiliate marketing at a glance</p>
        </div>
        <div style={{ display: 'flex', gap: 8 }}>
          <button className="btn btn-primary btn-sm" onClick={() => window.location.reload()}>
            🔄 Refresh
          </button>
        </div>
      </div>

      <Dashboard />

      <div style={{ padding: '0 24px', marginTop: 24 }}>
        <h2 className="section-title">
          <span className="icon">📡</span> Platform Status
        </h2>
        <PlatformStatus />
      </div>
    </div>
  );
}

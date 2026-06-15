import React from 'react';
import { NavLink } from 'react-router-dom';
import { FiHome, FiGrid, FiSend, FiBarChart2, FiSettings } from 'react-icons/fi';

const NAV_ITEMS = [
  { path: '/dashboard', icon: FiHome, label: 'Overview' },
  { path: '/products', icon: FiGrid, label: 'Products' },
  { path: '/posts', icon: FiSend, label: 'Posts & Queue' },
  { path: '/analytics', icon: FiBarChart2, label: 'Analytics' },
  { path: '/settings', icon: FiSettings, label: 'Settings' },
];

export default function Sidebar({ isOpen, onToggle }) {
  return (
    <aside style={{
      position: 'fixed',
      left: 0,
      top: 0,
      bottom: 0,
      width: 260,
      background: 'rgba(13, 13, 13, 0.95)',
      backdropFilter: 'blur(20px)',
      borderRight: '1px solid var(--border)',
      display: 'flex',
      flexDirection: 'column',
      zIndex: 200,
      transform: isOpen ? 'translateX(0)' : 'translateX(-260px)',
      transition: 'transform 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
    }}>
      {/* Brand Header */}
      <div style={{
        padding: '24px 20px',
        borderBottom: '1px solid var(--border)',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <span style={{ fontSize: '2rem' }}>👗</span>
          <div>
            <h1 style={{
              fontSize: '1.2rem',
              fontWeight: 800,
              background: 'var(--gradient)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              lineHeight: 1.2,
            }}>
              FashionBazzer
            </h1>
            <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
              Affiliate Engine
            </span>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav style={{ flex: 1, padding: '12px 8px' }}>
        {NAV_ITEMS.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.path}
              to={item.path}
              end={item.path === '/dashboard'}
              style={({ isActive }) => ({
                display: 'flex',
                alignItems: 'center',
                gap: 12,
                padding: '12px 16px',
                borderRadius: 'var(--radius-sm)',
                textDecoration: 'none',
                color: isActive ? 'var(--text)' : 'var(--text-muted)',
                background: isActive ? 'rgba(255, 60, 172, 0.1)' : 'transparent',
                border: isActive ? '1px solid rgba(255, 60, 172, 0.2)' : '1px solid transparent',
                fontSize: '0.9rem',
                fontWeight: isActive ? 600 : 400,
                transition: 'var(--transition)',
                marginBottom: 4,
              })}
              onMouseEnter={(e) => {
                if (!e.currentTarget.classList.contains('active')) {
                  e.currentTarget.style.background = 'rgba(255,255,255,0.04)';
                }
              }}
              onMouseLeave={(e) => {
                if (!e.currentTarget.classList.contains('active')) {
                  e.currentTarget.style.background = 'transparent';
                }
              }}
            >
              <Icon size={18} />
              {item.label}
            </NavLink>
          );
        })}
      </nav>

      {/* Footer */}
      <div style={{
        padding: '16px 20px',
        borderTop: '1px solid var(--border)',
      }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          fontSize: '0.75rem',
          color: 'var(--text-muted)',
        }}>
          <span>19 posts/day</span>
          <span>Zero human work</span>
        </div>
      </div>
    </aside>
  );
}

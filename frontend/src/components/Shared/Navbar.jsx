import React from 'react';
import { FiMenu, FiBell, FiRefreshCw, FiLogOut } from 'react-icons/fi';
import { useAuth } from '../../context/AuthContext';
import { useNavigate } from 'react-router-dom';

export default function Navbar({ onMenuClick }) {
  const [time, setTime] = React.useState(new Date());
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  React.useEffect(() => {
    const timer = setInterval(() => setTime(new Date()), 60000);
    return () => clearInterval(timer);
  }, []);

  async function handleLogout() {
    logout();
    navigate('/login');
  }

  return (
    <nav style={{
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '16px 24px',
      borderBottom: '1px solid var(--border)',
      background: 'rgba(13, 13, 13, 0.9)',
      backdropFilter: 'blur(20px)',
      position: 'sticky',
      top: 0,
      zIndex: 100,
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
        <button
          onClick={onMenuClick}
          style={{
            background: 'none',
            border: 'none',
            color: 'var(--text)',
            cursor: 'pointer',
            fontSize: '1.3rem',
            padding: 4,
            display: 'flex',
          }}
        >
          <FiMenu />
        </button>
        <div>
          <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Dashboard</span>
          <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', margin: '0 8px' }}>/</span>
          <span style={{ fontSize: '0.85rem', fontWeight: 500 }}>Overview</span>
        </div>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
        <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
          {time.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' })}
        </span>

        <button style={{
          background: 'rgba(255,255,255,0.06)',
          border: '1px solid var(--border)',
          color: 'var(--text-muted)',
          borderRadius: '50%',
          width: 36,
          height: 36,
          cursor: 'pointer',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          transition: 'var(--transition)',
        }}>
          <FiRefreshCw size={14} />
        </button>

        <button style={{
          background: 'rgba(255,255,255,0.06)',
          border: '1px solid var(--border)',
          color: 'var(--text-muted)',
          borderRadius: '50%',
          width: 36,
          height: 36,
          cursor: 'pointer',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          position: 'relative',
          transition: 'var(--transition)',
        }}>
          <FiBell size={14} />
          <span style={{
            position: 'absolute',
            top: -2,
            right: -2,
            width: 8,
            height: 8,
            background: 'var(--primary)',
            borderRadius: '50%',
          }} />
        </button>

        {/* User avatar */}
        <div
          title={user?.username}
          style={{
            width: 36, height: 36, borderRadius: '50%',
            background: 'var(--gradient)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontSize: '0.8rem', fontWeight: 700, cursor: 'pointer',
            position: 'relative',
          }}
        >
          {user?.username?.charAt(0).toUpperCase() || 'U'}
        </div>

        {/* Logout button */}
        <button
          onClick={handleLogout}
          title="Sign Out"
          style={{
            background: 'rgba(255,71,87,0.08)',
            border: '1px solid rgba(255,71,87,0.15)',
            color: '#FF4757',
            borderRadius: 'var(--radius-sm)',
            padding: '8px 12px',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: 6,
            fontSize: '0.75rem',
            fontWeight: 500,
            transition: 'var(--transition)',
          }}
          onMouseEnter={(e) => e.currentTarget.style.background = 'rgba(255,71,87,0.15)'}
          onMouseLeave={(e) => e.currentTarget.style.background = 'rgba(255,71,87,0.08)'}
        >
          <FiLogOut size={12} />
          Sign Out
        </button>
      </div>
    </nav>
  );
}

import React from 'react';
import ProductList from '../components/Products/ProductList';
import { FiTrendingUp, FiGrid } from 'react-icons/fi';

export default function ProductsPage() {
  const [view, setView] = React.useState('all');

  return (
    <div className="fade-in">
      <div className="page-header">
        <div>
          <h1>📦 Products</h1>
          <p>Trending dress products from affiliate platforms</p>
        </div>
        <div style={{ display: 'flex', gap: 8 }}>
          <button
            className={`btn btn-sm ${view === 'all' ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => setView('all')}
          >
            <FiGrid size={14} /> All Products
          </button>
          <button
            className={`btn btn-sm ${view === 'trending' ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => setView('trending')}
          >
            <FiTrendingUp size={14} /> Trending
          </button>
        </div>
      </div>

      <div style={{
        display: 'flex',
        gap: 16,
        padding: '20px 24px 0',
        flexWrap: 'wrap',
      }}>
        <div className="glass-card" style={{ padding: '16px', flex: 1, minWidth: 200 }}>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: 4 }}>Total Products</div>
          <div style={{ fontSize: '1.8rem', fontWeight: 800, color: 'var(--primary)' }}>156</div>
        </div>
        <div className="glass-card" style={{ padding: '16px', flex: 1, minWidth: 200 }}>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: 4 }}>Trending Now</div>
          <div style={{ fontSize: '1.8rem', fontWeight: 800, color: 'var(--success)' }}>23</div>
        </div>
        <div className="glass-card" style={{ padding: '16px', flex: 1, minWidth: 200 }}>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: 4 }}>Last Scraped</div>
          <div style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--text-muted)' }}>2 hours ago</div>
        </div>
        <div className="glass-card" style={{ padding: '16px', flex: 1, minWidth: 200 }}>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: 4 }}>With AI Content</div>
          <div style={{ fontSize: '1.8rem', fontWeight: 800, color: '#FFB800' }}>89</div>
        </div>
      </div>

      <ProductList currentPage={view} />
    </div>
  );
}

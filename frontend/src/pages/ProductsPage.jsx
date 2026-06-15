import React from 'react';
import ProductList from '../components/Products/ProductList';
import api from '../services/api';
import { FiTrendingUp, FiGrid } from 'react-icons/fi';

export default function ProductsPage() {
  const [view, setView] = React.useState('all');
  const [stats, setStats] = React.useState(null);
  const [loading, setLoading] = React.useState(true);

  React.useEffect(() => {
    fetchStats();
  }, []);

  async function fetchStats() {
    try {
      const res = await api.get('/products/');
      const products = res.data.results || res.data || [];
      const total = products.length;
      const trending = products.filter(p => p.is_trending).length;
      const withContent = products.filter(p => p.ai_tagline).length;

      // Calculate last scraped time from most recent product
      let lastScraped = 'N/A';
      if (products.length > 0) {
        const dates = products
          .filter(p => p.last_scraped)
          .map(p => new Date(p.last_scraped));
        if (dates.length > 0) {
          const mostRecent = new Date(Math.max(...dates));
          const diffMs = Date.now() - mostRecent.getTime();
          const diffMins = Math.floor(diffMs / 60000);
          if (diffMins < 60) {
            lastScraped = `${diffMins} min ago`;
          } else {
            const diffHours = Math.floor(diffMins / 60);
            lastScraped = `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
          }
        }
      }

      setStats({ total, trending, withContent, lastScraped });
    } catch (err) {
      console.error('Failed to fetch product stats:', err);
      setStats({ total: 0, trending: 0, withContent: 0, lastScraped: 'N/A' });
    } finally {
      setLoading(false);
    }
  }

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
          <div style={{ fontSize: '1.8rem', fontWeight: 800, color: 'var(--primary)' }}>
            {loading ? '-' : stats?.total?.toLocaleString() || '0'}
          </div>
        </div>
        <div className="glass-card" style={{ padding: '16px', flex: 1, minWidth: 200 }}>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: 4 }}>Trending Now</div>
          <div style={{ fontSize: '1.8rem', fontWeight: 800, color: 'var(--success)' }}>
            {loading ? '-' : stats?.trending || '0'}
          </div>
        </div>
        <div className="glass-card" style={{ padding: '16px', flex: 1, minWidth: 200 }}>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: 4 }}>Last Scraped</div>
          <div style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--text-muted)' }}>
            {loading ? '-' : stats?.lastScraped || 'N/A'}
          </div>
        </div>
        <div className="glass-card" style={{ padding: '16px', flex: 1, minWidth: 200 }}>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: 4 }}>With AI Content</div>
          <div style={{ fontSize: '1.8rem', fontWeight: 800, color: '#FFB800' }}>
            {loading ? '-' : stats?.withContent || '0'}
          </div>
        </div>
      </div>

      <ProductList currentPage={view} />
    </div>
  );
}

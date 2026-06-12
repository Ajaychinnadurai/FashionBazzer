import React from 'react';
import { FiSearch, FiRefreshCw } from 'react-icons/fi';
import ProductCard from './ProductCard';
import Loader from '../Shared/Loader';
import toast from 'react-hot-toast';
import api from '../../services/api';

export default function ProductList({ currentPage = 'all' }) {
  const [products, setProducts] = React.useState([]);
  const [loading, setLoading] = React.useState(true);
  const [search, setSearch] = React.useState('');
  const [platformFilter, setPlatformFilter] = React.useState('all');

  React.useEffect(() => {
    fetchProducts();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function fetchProducts() {
    try {
      setLoading(true);
      const endpoint = currentPage === 'trending'
        ? '/products/trending/'
        : '/products/';
      const res = await api.get(endpoint);
      setProducts(res.data.results || res.data || []);
    } catch (err) {
      console.error('Products fetch error:', err);
      setProducts([]);
    } finally {
      setLoading(false);
    }
  }

  const filteredProducts = products.filter(p => {
    const matchesSearch = p.name?.toLowerCase().includes(search.toLowerCase());
    const matchesPlatform = platformFilter === 'all' || p.platform === platformFilter;
    return matchesSearch && matchesPlatform;
  });

  async function handleGenerate(productId) {
    try {
      await api.post('/queue/generate/', { product_id: productId });
      toast.success('Content generation started! 🎉');
    } catch (err) {
      toast.error('Failed to generate content');
    }
  }

  if (loading) return <Loader text="Loading products..." />;

  return (
    <div style={{ padding: '24px' }}>
      {/* Filters */}
      <div style={{
        display: 'flex',
        flexWrap: 'wrap',
        gap: 12,
        marginBottom: 24,
        alignItems: 'center',
      }}>
        <div style={{
          flex: 1,
          minWidth: 250,
          display: 'flex',
          alignItems: 'center',
          gap: 8,
          background: 'rgba(255,255,255,0.05)',
          border: '1px solid var(--border)',
          borderRadius: 'var(--radius-sm)',
          padding: '8px 16px',
        }}>
          <FiSearch size={16} color="var(--text-muted)" />
          <input
            type="text"
            placeholder="Search products by name, category..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            style={{
              background: 'none',
              border: 'none',
              color: 'var(--text)',
              outline: 'none',
              width: '100%',
              fontSize: '0.9rem',
              fontFamily: 'Inter',
            }}
          />
        </div>

        <select
          value={platformFilter}
          onChange={(e) => setPlatformFilter(e.target.value)}
          style={{
            background: 'rgba(255,255,255,0.05)',
            border: '1px solid var(--border)',
            borderRadius: 'var(--radius-sm)',
            color: 'var(--text)',
            padding: '8px 16px',
            fontSize: '0.9rem',
            outline: 'none',
            cursor: 'pointer',
            fontFamily: 'Inter',
          }}
        >
          <option value="all">All Platforms</option>
          <option value="meesho">Meesho</option>
          <option value="amazon">Amazon</option>
          <option value="flipkart">Flipkart</option>
        </select>

        <button className="btn btn-secondary btn-sm" onClick={fetchProducts}>
          <FiRefreshCw size={14} /> Refresh
        </button>
      </div>

      {/* Product Grid */}
      {filteredProducts.length === 0 ? (
        <div className="empty-state">
          <div className="emoji">🔍</div>
          <h3>No products found</h3>
          <p>Try adjusting your filters or wait for the next product scrape cycle.</p>
        </div>
      ) : (
        <div className="dashboard-grid" style={{ gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))' }}>
          {filteredProducts.map((product, i) => (
            <ProductCard
              key={product.id || i}
              product={product}
              onGenerate={handleGenerate}
            />
          ))}
        </div>
      )}
    </div>
  );
}


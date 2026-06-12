import React from 'react';
import { FiSearch, FiFilter, FiRefreshCw } from 'react-icons/fi';
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
      // Demo data
      setProducts(getDemoProducts());
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

function getDemoProducts() {
  return [
    {
      id: 1, name: 'Trendy Co-ord Set - Latest Collection', platform: 'meesho',
      original_price: 1299, sale_price: 399, discount_percent: 69,
      rating: 4.7, review_count: 5800, category: 'co-ord',
      affiliate_url: '#', image_url: '',
      ai_tagline: '💖 This co-ord set is giving main character energy! 🔥',
    },
    {
      id: 2, name: 'Women Casual Bodycon Mini Dress', platform: 'amazon',
      original_price: 1999, sale_price: 449, discount_percent: 78,
      rating: 4.5, review_count: 3200, category: 'bodycon',
      affiliate_url: '#', image_url: '',
      ai_tagline: '✨ Your new fav dress is here and it is only ₹449! 💫',
    },
    {
      id: 3, name: 'Designer Indo-Western Fusion Dress', platform: 'flipkart',
      original_price: 1899, sale_price: 699, discount_percent: 63,
      rating: 4.8, review_count: 2100, category: 'indo-western',
      affiliate_url: '#', image_url: '',
      ai_tagline: '💃 Slay every moment in this stunning fusion dress! 🔥',
    },
    {
      id: 4, name: 'Printed Maxi Dress - Summer Special', platform: 'meesho',
      original_price: 999, sale_price: 299, discount_percent: 70,
      rating: 4.3, review_count: 12000, category: 'cottagecore',
      affiliate_url: '#', image_url: '',
      ai_tagline: '🌸 Obsessed is an understatement! Get this look for ₹299 ✨',
    },
    {
      id: 5, name: 'Party Wear Cut-out Dress - Trending Now', platform: 'amazon',
      original_price: 2499, sale_price: 699, discount_percent: 72,
      rating: 4.6, review_count: 890, category: 'cut-out',
      affiliate_url: '#', image_url: '',
      ai_tagline: '⭐ 4.6/5 stars — and we totally get why! Grab yours at ₹699 💕',
    },
    {
      id: 6, name: 'Elegant Y2K Revival Mini Dress', platform: 'flipkart',
      original_price: 1599, sale_price: 549, discount_percent: 66,
      rating: 4.4, review_count: 4500, category: 'y2k',
      affiliate_url: '#', image_url: '',
      ai_tagline: '🎯 This is THE dress everyone is talking about! ₹549 only! 💥',
    },
  ];
}

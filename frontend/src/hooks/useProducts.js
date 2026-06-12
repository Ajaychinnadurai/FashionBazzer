import { useState, useEffect, useCallback } from 'react';
import api from '../services/api';

export function useProducts(initialEndpoint = '/products/') {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchProducts = useCallback(async (endpoint = initialEndpoint) => {
    try {
      setLoading(true);
      setError(null);
      const res = await api.get(endpoint);
      setProducts(res.data.results || res.data || []);
    } catch (err) {
      console.error('Failed to fetch products:', err);
      setError('Failed to load products');
    } finally {
      setLoading(false);
    }
  }, [initialEndpoint]);

  useEffect(() => {
    fetchProducts();
  }, [fetchProducts]);

  const getTrendingProducts = useCallback(() => {
    return products.filter(p => p.is_trending);
  }, [products]);

  const getProductsByPlatform = useCallback((platform) => {
    return products.filter(p => p.platform === platform);
  }, [products]);

  return {
    products,
    loading,
    error,
    refresh: fetchProducts,
    getTrendingProducts,
    getProductsByPlatform,
  };
}

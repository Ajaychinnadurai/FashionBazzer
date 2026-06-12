import { useState, useEffect, useCallback } from 'react';
import api from '../services/api';

export function useAnalytics() {
  const [stats, setStats] = useState(null);
  const [clicks, setClicks] = useState([]);
  const [earnings, setEarnings] = useState([]);
  const [platformStatus, setPlatformStatus] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchAll = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const [overviewRes, clicksRes, earningsRes, statusRes] = await Promise.all([
        api.get('/analytics/overview/'),
        api.get('/analytics/clicks/?days=30'),
        api.get('/analytics/earnings/?days=30'),
        api.get('/analytics/status/'),
      ]);

      setStats(overviewRes.data);
      setClicks(clicksRes.data?.by_platform || clicksRes.data || []);
      setEarnings(earningsRes.data || []);
      setPlatformStatus(statusRes.data || []);
    } catch (err) {
      console.error('Analytics fetch error:', err);
      setError('Failed to load analytics');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchAll();
  }, [fetchAll]);

  return {
    stats,
    clicks,
    earnings,
    platformStatus,
    loading,
    error,
    refresh: fetchAll,
  };
}

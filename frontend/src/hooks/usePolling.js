/**
 * Auto-refresh hook — polls an API function at a given interval.
 * Returns { data, loading, error, refresh, lastUpdated }.
 */
import { useState, useEffect, useCallback, useRef } from 'react';

export function usePolling(fetchFn, intervalMs = 30000, immediate = true) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(immediate);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);
  const intervalRef = useRef(null);
  const mountedRef = useRef(true);

  const refresh = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const result = await fetchFn();
      if (mountedRef.current) {
        setData(result);
        setLastUpdated(new Date());
      }
    } catch (err) {
      if (mountedRef.current) {
        setError(err?.message || 'Failed to fetch');
      }
    } finally {
      if (mountedRef.current) {
        setLoading(false);
      }
    }
  }, [fetchFn]);

  useEffect(() => {
    mountedRef.current = true;
    if (immediate) refresh();

    intervalRef.current = setInterval(refresh, intervalMs);

    return () => {
      mountedRef.current = false;
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [refresh, intervalMs, immediate]);

  return { data, loading, error, refresh, lastUpdated };
}

import React, { useCallback } from 'react';
import {
  FiMousePointer, FiDollarSign, FiSend, FiShoppingCart,
  FiRefreshCw,
} from 'react-icons/fi';
import StatsCard from './StatsCard';
import RevenueChart from './RevenueChart';
import LiveActivityFeed from './LiveActivityFeed';
import Loader from '../Shared/Loader';
import api from '../../services/api';
import { usePolling } from '../../hooks/usePolling';

export default function Dashboard() {
  const [seedLoading, setSeedLoading] = React.useState(false);

  // ── Auto-polling every 30 seconds ──
  const fetchOverview = useCallback(() =>
    api.get('/dashboard/overview/').then(r => r.data), []);
  const fetchEarnings = useCallback(() =>
    api.get('/analytics/earnings/?days=30').then(r => r.data), []);
  const fetchQueue = useCallback(() =>
    api.get('/queue/').then(r => r.data?.results || r.data || []), []);

  const {
    data: overviewData,
    loading,
    refresh: refreshOverview,
    lastUpdated,
  } = usePolling(fetchOverview, 30000, true);

  const { data: earningsRaw, refresh: refreshEarnings } = usePolling(fetchEarnings, 30000, true);
  const { data: recentPosts, refresh: refreshQueue } = usePolling(fetchQueue, 45000, true);

  const refreshAll = useCallback(() => {
    refreshOverview();
    refreshEarnings();
    refreshQueue();
  }, [refreshOverview, refreshEarnings, refreshQueue]);

  async function handleSeed() {
    try {
      setSeedLoading(true);
      await api.get('/dashboard/seed/');
      refreshAll();
    } catch (e) {
      console.error('Seed error:', e);
    } finally {
      setSeedLoading(false);
    }
  }

  // ── Parse stats ──
  const statsFromApi = overviewData?.stats && typeof overviewData.stats === 'object'
    ? overviewData.stats : {};

  const totalClicks = statsFromApi.total_clicks ?? 0;
  const todayClicks = statsFromApi.today_clicks ?? 0;
  const totalEarnings = statsFromApi.total_earnings ?? 0;
  const todayEarnings = statsFromApi.today_earnings ?? 0;
  const totalPosts = statsFromApi.total_posts ?? 0;
  const totalConversions = statsFromApi.total_conversions ?? 0;
  const totalProducts = statsFromApi.total_products ?? 0;

  const calcChange = (today, total) => {
    if (total <= 0) return 0;
    const avgDaily = total / 30;
    if (avgDaily <= 0) return today > 0 ? 100 : 0;
    return Math.min(Math.max(Math.round(((today - avgDaily) / avgDaily) * 100), -100), 999);
  };

  // Earnings array
  const earningsArray = Array.isArray(earningsRaw)
    ? earningsRaw
    : (Array.isArray(earningsRaw?.results) ? earningsRaw.results : []);

  const revenueData = earningsArray.map((e) => ({
    name: e?.platform ?? 'Unknown',
    earnings: parseFloat(e?.total_earnings) || 0,
  }));

  // ── Generate stable sparkline data from available numbers ──
  // Using useMemo + seeded pseudo-random to avoid flickering on every poll
  const makeSparkline = useCallback((total) => {
    if (!total || total <= 0) return null;
    const base = Math.max(Math.floor(total / 30), 1);
    // Generate deterministic bars using a seed based on the total value
    // so sparklines don't change randomly between refreshes
    return Array.from({ length: 14 }, (_, i) => {
      const pseudoRand = ((total * (i + 1) * 7) % 100) / 100;
      return Math.max(0, base + Math.floor((pseudoRand - 0.3) * base * 0.6));
    });
  }, []);

  // ── Loading / Error states ──
  if (loading && !overviewData) return <Loader text="Loading dashboard..." />;

  if (!overviewData) {
    return (
      <div style={{ padding: '24px' }}>
        <div className="empty-state">
          <div className="emoji">📡</div>
          <h3>Could not load dashboard data</h3>
          <p>The server may still be starting up. Real data will appear once scraping completes.</p>
          <div style={{ display: 'flex', gap: 12, marginTop: 12, flexWrap: 'wrap' }}>
            <button className="btn btn-primary" onClick={refreshAll}>Retry</button>
            <button className="btn btn-secondary" onClick={handleSeed} disabled={seedLoading}>
              {seedLoading ? 'Seeding...' : 'Run Seed'}
            </button>
          </div>
        </div>
      </div>
    );
  }

  const statCards = [
    {
      title: 'Total Clicks',
      value: Number(totalClicks).toLocaleString(),
      change: calcChange(todayClicks, totalClicks),
      subtitle: `${Number(todayClicks)} today`,
      icon: <FiMousePointer size={22} />,
      color: '#FF3CAC',
      sparklineData: makeSparkline(totalClicks),
    },
    {
      title: 'Earnings',
      value: `₹${Number(totalEarnings).toLocaleString('en-IN', { maximumFractionDigits: 0 })}`,
      change: calcChange(todayEarnings, totalEarnings),
      subtitle: `₹${Number(todayEarnings).toLocaleString('en-IN', { maximumFractionDigits: 0 })} today`,
      icon: <FiDollarSign size={22} />,
      color: '#00D4AA',
      sparklineData: makeSparkline(totalEarnings),
    },
    {
      title: 'Posts Sent',
      value: String(totalPosts),
      change: totalPosts > 0 ? Math.round((totalPosts / 30) * 100) : 0,
      subtitle: 'Total published',
      icon: <FiSend size={22} />,
      color: '#2B86C5',
      sparklineData: makeSparkline(totalPosts),
    },
    {
      title: 'Conversions',
      value: String(totalConversions),
      change: totalConversions > 0 ? Math.round(((totalConversions - 3) / 3) * 100) : 0,
      subtitle: `${Number(totalProducts)} products`,
      icon: <FiShoppingCart size={22} />,
      color: '#FFB800',
      sparklineData: makeSparkline(totalConversions),
    },
  ];

  return (
    <div style={{ padding: '24px' }}>
      {/* Status bar */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          padding: '0 0 16px',
          flexWrap: 'wrap',
          gap: 8,
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <span className="live-indicator">
            <span className="live-dot" />
            Auto-refreshing
          </span>
          {lastUpdated && (
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
              Updated {Math.floor((Date.now() - lastUpdated.getTime()) / 1000)}s ago
            </span>
          )}
        </div>
        <div style={{ display: 'flex', gap: 8 }}>
          <button className="btn btn-secondary btn-sm" onClick={handleSeed} disabled={seedLoading}>
            {seedLoading ? 'Seeding...' : 'Run Seed'}
          </button>
          <button className="btn btn-secondary btn-sm" onClick={refreshAll} title="Refresh now">
            <FiRefreshCw size={14} className={loading ? 'spin' : ''} />
          </button>
        </div>
      </div>

      {/* Stats Grid with sparklines */}
      <div className="dashboard-grid">
        {statCards.map((card, i) => (
          <StatsCard key={i} {...card} />
        ))}
      </div>

      {/* Charts row */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))',
          gap: 20,
          marginTop: 20,
          padding: '0 24px',
        }}
      >
        <RevenueChart data={revenueData} />
        <LiveActivityFeed posts={recentPosts} />
      </div>
    </div>
  );
}

import React from 'react';
import { FiMousePointer, FiDollarSign, FiSend, FiShoppingCart } from 'react-icons/fi';
import StatsCard from './StatsCard';
import RevenueChart from './RevenueChart';
import Loader from '../Shared/Loader';
import api from '../../services/api';

export default function Dashboard() {
  const [stats, setStats] = React.useState(null);
  const [loading, setLoading] = React.useState(true);
  const [seedLoading, setSeedLoading] = React.useState(false);
  const [, setError] = React.useState(null);
  const [revenueData, setRevenueData] = React.useState([]);


  React.useEffect(() => {
    fetchDashboardData();
  }, []);

  async function fetchDashboardData() {
    try {
      setLoading(true);

      const [overviewRes, earningsRes] = await Promise.all([
        api.get('/dashboard/overview/'),
        api.get('/analytics/earnings/?days=30'),
      ]);

      const data = overviewRes?.data || {};
      const statsFromApi = data.stats && typeof data.stats === 'object' ? data.stats : {};

      const totalClicks = statsFromApi.total_clicks ?? 0;
      const todayClicks = statsFromApi.today_clicks ?? 0;
      const totalEarnings = statsFromApi.total_earnings ?? 0;
      const todayEarnings = statsFromApi.today_earnings ?? 0;
      const totalPosts = statsFromApi.total_posts ?? 0;
      const totalConversions = statsFromApi.total_conversions ?? 0;
      const totalProducts = statsFromApi.total_products ?? 0;

      setStats({
        clicks: {
          value: Number(totalClicks).toLocaleString(),
          change: Number(todayClicks) > 0 ? 23 : 0,
          subtitle: `${Number(todayClicks)} today`,
        },
        earnings: {
          value: `₹${totalEarnings}`,
          change: 15,
          subtitle: `₹${todayEarnings} today`,
        },
        posts: {
          value: String(totalPosts),
          change: 8,
          subtitle: 'Total published',
        },
        conversions: {
          value: String(totalConversions),
          change: -3,
          subtitle: `${Number(totalProducts)} products`,
        },
      });

      // earnings endpoint shape can be either array [{platform,total_earnings}, ...]
      // or an object wrapping it. Normalize safely.
      const earningsRaw = earningsRes?.data;
      const earningsArray = Array.isArray(earningsRaw)
        ? earningsRaw
        : (Array.isArray(earningsRaw?.results) ? earningsRaw.results : []);

      setRevenueData(
        earningsArray.map((e) => ({
          name: e?.platform ?? 'Unknown',
          earnings: parseFloat(e?.total_earnings) || 0,
        }))
      );

      setError(null);
    } catch (err) {
      console.error('Dashboard fetch error:', err);
      setError('Failed to load dashboard data');
      setStats(null);
      setRevenueData([]);
    } finally {
      setLoading(false);
    }
  }

  async function handleSeed() {
    try {
      setSeedLoading(true);
      await api.get('/dashboard/seed/');
      await fetchDashboardData();
    } catch (e) {
      console.error('Seed error:', e);
    } finally {
      setSeedLoading(false);
    }
  }


  if (loading) return <Loader text="Loading dashboard..." />;

  // If stats is null after loading, API call failed
  if (!stats) {
    return (
      <div style={{ padding: '24px' }}>
        <div className="empty-state">
          <div className="emoji">📡</div>
          <h3>Could not load dashboard data</h3>
          <p>The server may still be starting up. You can also run the seed pipeline.</p>
          <div style={{ display: 'flex', gap: 12, marginTop: 12, flexWrap: 'wrap' }}>
            <button className="btn btn-primary" onClick={fetchDashboardData}>
              Retry
            </button>
            <button
              className="btn btn-secondary"
              onClick={handleSeed}
              disabled={seedLoading}
            >
              {seedLoading ? 'Seeding...' : 'Run Seed'}
            </button>
          </div>
        </div>
      </div>
    );
  }


  const statCards = [
    { title: 'Total Clicks', ...stats.clicks, icon: <FiMousePointer size={22} />, color: '#FF3CAC' },
    { title: 'Earnings Today', ...stats.earnings, icon: <FiDollarSign size={22} />, color: '#00D4AA' },
    { title: 'Posts Sent', ...stats.posts, icon: <FiSend size={22} />, color: '#2B86C5' },
    { title: 'Conversions', ...stats.conversions, icon: <FiShoppingCart size={22} />, color: '#FFB800' },
  ];

  return (
    <div style={{ padding: '24px' }}>
      <div style={{ display: 'flex', justifyContent: 'flex-end', padding: '0 24px 12px' }}>
        <button className="btn btn-secondary" onClick={handleSeed} disabled={seedLoading}>
          {seedLoading ? 'Seeding...' : 'Run Seed'}
        </button>
      </div>

      {/* Stats Grid */}
      <div className="dashboard-grid">

        {statCards.map((card, i) => (
          <StatsCard key={i} {...card} />
        ))}
      </div>

      {/* Revenue Chart */}
      <div style={{ marginTop: 20, padding: '0 24px' }}>
        <RevenueChart data={revenueData} />
      </div>
    </div>
  );
}

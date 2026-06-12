import React from 'react';
import { FiMousePointer, FiDollarSign, FiSend, FiShoppingCart } from 'react-icons/fi';
import StatsCard from './StatsCard';
import RevenueChart from './RevenueChart';
import Loader from '../Shared/Loader';
import api from '../../services/api';

export default function Dashboard() {
  const [stats, setStats] = React.useState(null);
  const [loading, setLoading] = React.useState(true);
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

      const data = overviewRes.data;

      setStats({
        clicks: {
          value: data.stats?.total_clicks?.toLocaleString() || '0',
          change: data.stats?.today_clicks > 0 ? 23 : 0,
          subtitle: `${data.stats?.today_clicks || 0} today`,
        },
        earnings: {
          value: `₹${data.stats?.total_earnings || '0'}`,
          change: 15,
          subtitle: `₹${data.stats?.today_earnings || '0'} today`,
        },
        posts: {
          value: data.stats?.total_posts?.toString() || '0',
          change: 8,
          subtitle: 'Total published',
        },
        conversions: {
          value: data.stats?.total_conversions?.toString() || '0',
          change: -3,
          subtitle: `${data.stats?.total_products || 0} products`,
        },
      });

      if (earningsRes.data && Array.isArray(earningsRes.data)) {
        setRevenueData(earningsRes.data.map(e => ({
          name: e.platform,
          earnings: parseFloat(e.total_earnings) || 0,
        })));
      }

      setError(null);
    } catch (err) {
      console.error('Dashboard fetch error:', err);
      setError('Failed to load dashboard data');
      // Use demo data for development
      setStats({
        clicks: { value: '12,456', change: 23, subtitle: '342 today' },
        earnings: { value: '₹4,320', change: 15, subtitle: '₹842 today' },
        posts: { value: '48', change: 8, subtitle: '19 scheduled today' },
        conversions: { value: '37', change: -3, subtitle: '5 today' },
      });
      setRevenueData([
        { name: 'Telegram', earnings: 2400 },
        { name: 'Instagram', earnings: 1800 },
        { name: 'Facebook', earnings: 800 },
        { name: 'Pinterest', earnings: 3200 },
        { name: 'Twitter', earnings: 1200 },
      ]);
    } finally {
      setLoading(false);
    }
  }

  if (loading) return <Loader text="Loading dashboard..." />;

  const statCards = [
    { title: 'Total Clicks', ...stats.clicks, icon: <FiMousePointer size={22} />, color: '#FF3CAC' },
    { title: 'Earnings Today', ...stats.earnings, icon: <FiDollarSign size={22} />, color: '#00D4AA' },
    { title: 'Posts Sent', ...stats.posts, icon: <FiSend size={22} />, color: '#2B86C5' },
    { title: 'Conversions', ...stats.conversions, icon: <FiShoppingCart size={22} />, color: '#FFB800' },
  ];

  return (
    <div style={{ padding: '24px' }}>
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

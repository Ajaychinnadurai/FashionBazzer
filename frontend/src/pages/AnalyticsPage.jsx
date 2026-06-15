import React from 'react';
import ClicksChart from '../components/Analytics/ClicksChart';
import ConversionTable from '../components/Analytics/ConversionTable';
import EarningsTracker from '../components/Analytics/EarningsTracker';
import { FiRefreshCw } from 'react-icons/fi';
import api from '../services/api';

export default function AnalyticsPage() {
  const [data, setData] = React.useState(null);
  const [, setLoading] = React.useState(true);
  const [timeRange, setTimeRange] = React.useState(30);

  React.useEffect(() => {
    fetchData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [timeRange]);

  async function fetchData() {
    try {
      setLoading(true);
      const [overviewRes, clicksRes, earningsRes] = await Promise.all([
        api.get('/analytics/overview/'),
        api.get(`/analytics/clicks/?days=${timeRange}`),
        api.get(`/analytics/earnings/?days=${timeRange}`),
      ]);

      setData({
        stats: overviewRes.data,
        clicks: clicksRes.data,
        earnings: earningsRes.data,
      });
    } catch (err) {
      console.error('Analytics fetch error:', err);
      setData({
        stats: null,
        clicks: null,
        earnings: null,
      });
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="fade-in" style={{ paddingBottom: 40 }}>
      <div className="page-header">
        <div>
          <h1>📊 Analytics</h1>
          <p>Track clicks, conversions, and earnings across all platforms</p>
        </div>
        <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
          <select
            value={timeRange}
            onChange={(e) => setTimeRange(parseInt(e.target.value))}
            style={{
              background: 'rgba(255,255,255,0.05)',
              border: '1px solid var(--border)',
              borderRadius: 8,
              color: 'var(--text)',
              padding: '8px 12px',
              fontSize: '0.85rem',
              outline: 'none',
              fontFamily: 'Inter',
            }}
          >
            <option value={7}>Last 7 days</option>
            <option value={30}>Last 30 days</option>
            <option value={90}>Last 90 days</option>
          </select>
          <button className="btn btn-secondary btn-sm" onClick={fetchData}>
            <FiRefreshCw size={14} />
          </button>
        </div>
      </div>

      {/* Stats bar */}
      <div style={{
        display: 'flex',
        gap: 16,
        padding: '20px 24px',
        flexWrap: 'wrap',
      }}>
        {[
          { label: 'Total Clicks', value: data?.stats?.total_clicks?.toLocaleString() || '0', color: '#FF3CAC' },
          { label: 'Conversion Rate', value: data?.stats?.conversion_rate ? `${data.stats.conversion_rate}%` : '0%', color: '#00D4AA' },
          { label: 'Total Revenue', value: data?.stats?.total_earnings ? `₹${data.stats.total_earnings}` : '₹0', color: '#2B86C5' },
          { label: 'Top Products', value: data?.stats?.total_products?.toString() || '0', color: '#FFB800' },
        ].map((stat, i) => (
          <div key={i} className="glass-card" style={{
            padding: '16px 20px',
            flex: 1,
            minWidth: 150,
          }}>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: 4 }}>
              {stat.label}
            </div>
            <div style={{
              fontSize: '1.5rem',
              fontWeight: 800,
              color: stat.color,
            }}>
              {stat.value}
            </div>
          </div>
        ))}
      </div>

      {/* Charts & Tables */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))',
        gap: 20,
        padding: '0 24px',
      }}>
        <ClicksChart data={data?.clicks?.by_platform?.map(c => ({
          name: c.platform,
          value: c.clicks
        })) || []} />
        <EarningsTracker data={data?.earnings || []} />
      </div>

      <div style={{ padding: '20px 24px 0' }}>
        <ConversionTable data={data?.clicks?.top_products || []} />
      </div>
    </div>
  );
}

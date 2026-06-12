import React from 'react';
import { FiClock, FiCheckCircle, FiXCircle, FiPlay } from 'react-icons/fi';
import toast from 'react-hot-toast';
import api from '../../services/api';

export default function PostQueue() {
  const [queue, setQueue] = React.useState([]);
  const [loading, setLoading] = React.useState(true);

  React.useEffect(() => {
    fetchQueue();
  }, []);

  async function fetchQueue() {
    try {
      const res = await api.get('/queue/');
      setQueue(res.data.results || res.data || []);
    } catch {
      setQueue(getDemoQueue());
    } finally {
      setLoading(false);
    }
  }

  async function handlePublishNow(postId) {
    try {
      await api.post('/queue/publish-now/', { post_id: postId });
      toast.success('Post published! 🎉');
      fetchQueue();
    } catch {
      toast.error('Failed to publish');
    }
  }

  if (loading) {
    return (
      <div style={{ padding: 24 }}>
        {[1, 2, 3].map(i => (
          <div key={i} className="skeleton" style={{ height: 120, marginBottom: 12 }} />
        ))}
      </div>
    );
  }

  return (
    <div style={{ padding: '24px' }}>
      {/* Queue Stats */}
      <div style={{
        display: 'flex',
        gap: 16,
        marginBottom: 24,
        flexWrap: 'wrap',
      }}>
        {[
          { label: 'Pending', count: queue.filter(p => p.status === 'pending').length, color: '#FFB800' },
          { label: 'Published', count: queue.filter(p => p.status === 'published').length, color: '#00D4AA' },
          { label: 'Failed', count: queue.filter(p => p.status === 'failed').length, color: '#FF4757' },
          { label: 'Total', count: queue.length, color: '#FF3CAC' },
        ].map((stat, i) => (
          <div key={i} className="glass-card" style={{
            padding: '16px 24px',
            display: 'flex',
            alignItems: 'center',
            gap: 12,
            minWidth: 140,
          }}>
            <span style={{ fontSize: '2rem', fontWeight: 800, color: stat.color }}>
              {stat.count}
            </span>
            <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
              {stat.label}
            </span>
          </div>
        ))}
      </div>

      {/* Queue List */}
      {queue.length === 0 ? (
        <div className="empty-state">
          <div className="emoji">📪</div>
          <h3>No posts in queue</h3>
          <p>Generate content from products to see them here.</p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          {queue.map((post, i) => (
            <div key={post.id || i} className="glass-card" style={{
              padding: '16px 20px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              gap: 16,
              flexWrap: 'wrap',
            }}>
              <div style={{ flex: 1, minWidth: 200 }}>
                <h4 style={{ fontSize: '0.9rem', fontWeight: 600, marginBottom: 4 }}>
                  {post.product_name || `Product #${post.product}`}
                </h4>
                <span className={`tag ${post.status === 'published' ? 'tag-success' : post.status === 'failed' ? 'tag-error' : 'tag-warning'}`}>
                  {post.status === 'published' ? <FiCheckCircle size={12} /> : post.status === 'failed' ? <FiXCircle size={12} /> : <FiClock size={12} />}
                  {post.status}
                </span>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                {post.scheduled_time && (
                  <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                    {new Date(post.scheduled_time).toLocaleString('en-IN')}
                  </span>
                )}

                {post.status === 'pending' && (
                  <button
                    className="btn btn-success btn-sm"
                    onClick={() => handlePublishNow(post.id)}
                  >
                    <FiPlay size={12} /> Publish Now
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function getDemoQueue() {
  return [
    { id: 1, product: 1, product_name: 'Trendy Co-ord Set', status: 'pending', scheduled_time: new Date(Date.now() + 3600000).toISOString() },
    { id: 2, product: 2, product_name: 'Bodycon Mini Dress', status: 'pending', scheduled_time: new Date(Date.now() + 7200000).toISOString() },
    { id: 3, product: 3, product_name: 'Indo-Western Fusion Dress', status: 'published', scheduled_time: new Date(Date.now() - 3600000).toISOString() },
    { id: 4, product: 4, product_name: 'Printed Maxi Dress', status: 'pending', scheduled_time: new Date(Date.now() + 14400000).toISOString() },
    { id: 5, product: 5, product_name: 'Party Cut-out Dress', status: 'failed', scheduled_time: new Date(Date.now() - 7200000).toISOString() },
  ];
}

import React from 'react';
import PostQueue from '../components/Posts/PostQueue';
import PostHistory from '../components/Posts/PostHistory';
import PostPreview from '../components/Posts/PostPreview';
import { FiClock, FiCheckCircle, FiSend, FiSearch } from 'react-icons/fi';
import api from '../services/api';

export default function PostsPage() {
  const [tab, setTab] = React.useState('queue');
  const [allPosts, setAllPosts] = React.useState([]);
  const [selectedPost, setSelectedPost] = React.useState(null);
  const [searchTerm, setSearchTerm] = React.useState('');
  const [loadingPosts, setLoadingPosts] = React.useState(false);

  React.useEffect(() => {
    if (tab === 'preview') fetchAllPosts();
  }, [tab]);

  async function fetchAllPosts() {
    try {
      setLoadingPosts(true);
      const res = await api.get('/queue/');
      setAllPosts(res.data.results || res.data || []);
    } catch {
      setAllPosts([]);
    } finally {
      setLoadingPosts(false);
    }
  }

  const filteredPosts = allPosts.filter(p => {
    const name = (p.product_name || '').toLowerCase();
    const term = searchTerm.toLowerCase();
    return name.includes(term) || p.status?.includes(term) || p.caption_style?.includes(term);
  });

  return (
    <div className="fade-in">
      <div className="page-header">
        <div>
          <h1>📤 Posts & Queue</h1>
          <p>Manage your automated social media posts — 19 posts/day</p>
        </div>
      </div>

      {/* Tab Switcher */}
      <div style={{
        display: 'flex',
        gap: 4,
        padding: '16px 24px',
        borderBottom: '1px solid var(--border)',
      }}>
        {[
          { key: 'queue', label: 'Post Queue', icon: FiClock },
          { key: 'history', label: 'History', icon: FiCheckCircle },
          { key: 'preview', label: 'Preview', icon: FiSend },
        ].map((tabItem) => {
          const Icon = tabItem.icon;
          return (
            <button
              key={tabItem.key}
              onClick={() => setTab(tabItem.key)}
              className={`btn btn-sm ${tab === tabItem.key ? 'btn-primary' : 'btn-secondary'}`}
            >
              <Icon size={14} /> {tabItem.label}
            </button>
          );
        })}
      </div>

      {/* Tab Content */}
      <div style={{ marginTop: 8 }}>
        {tab === 'queue' && <PostQueue onPreview={(post) => { setSelectedPost(post); setTab('preview'); }} />}
        {tab === 'history' && (
          <div style={{ padding: '24px' }}>
            <h2 className="section-title">
              <span className="icon">📜</span> Post History
            </h2>
            <PostHistory />
          </div>
        )}
        {tab === 'preview' && (
          <div style={{ padding: '24px' }}>
            {/* Post selector */}
            <div className="glass-card" style={{ padding: '16px 20px', marginBottom: 20 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 12, flexWrap: 'wrap' }}>
                <div style={{ position: 'relative', flex: 1, minWidth: 200 }}>
                  <FiSearch size={14} style={{
                    position: 'absolute', left: 12, top: '50%', transform: 'translateY(-50%)',
                    color: 'var(--text-muted)',
                  }} />
                  <input
                    type="text"
                    placeholder="Search posts..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    style={{
                      width: '100%', padding: '8px 12px 8px 36px',
                      background: 'rgba(255,255,255,0.05)',
                      border: '1px solid var(--border)',
                      borderRadius: 8,
                      color: 'var(--text)',
                      fontSize: '0.85rem',
                      outline: 'none',
                      fontFamily: 'Inter',
                    }}
                  />
                </div>
                <button className="btn btn-secondary btn-sm" onClick={fetchAllPosts}>
                  <FiSend size={12} /> Refresh
                </button>
                <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                  {filteredPosts.length} posts
                </span>
              </div>
            </div>

            {loadingPosts ? (
              <div style={{ padding: 40, textAlign: 'center', color: 'var(--text-muted)' }}>Loading...</div>
            ) : filteredPosts.length === 0 ? (
              <div className="glass-card" style={{ padding: '40px 24px', textAlign: 'center' }}>
                <div style={{ fontSize: '3rem', marginBottom: 16 }}>👁️</div>
                <h3 style={{ marginBottom: 8 }}>Post Preview</h3>
                <p style={{ color: 'var(--text-muted)', marginBottom: 16 }}>
                  {searchTerm ? 'No posts match your search.' : 'No posts in queue yet. Generate content from products first.'}
                </p>
              </div>
            ) : (
              <>
                {/* Post grid */}
                <div style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
                  gap: 12,
                  marginBottom: 20,
                }}>
                  {filteredPosts.slice(0, 20).map((post) => (
                    <div
                      key={post.id}
                      onClick={() => setSelectedPost(post)}
                      className="glass-card"
                      style={{
                        padding: '12px 16px',
                        cursor: 'pointer',
                        border: selectedPost?.id === post.id ? '2px solid #FF3CAC' : '1px solid var(--border)',
                        transition: 'var(--transition)',
                      }}
                      onMouseEnter={(e) => e.currentTarget.style.borderColor = '#FF3CAC66'}
                      onMouseLeave={(e) => e.currentTarget.style.borderColor = selectedPost?.id === post.id ? '#FF3CAC' : 'var(--border)'}
                    >
                      <div style={{ fontSize: '0.85rem', fontWeight: 500, marginBottom: 4, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                        {post.product_name || `Post #${post.id}`}
                      </div>
                      <div style={{ display: 'flex', gap: 6, alignItems: 'center' }}>
                        <span className={`tag ${post.status === 'published' ? 'tag-success' : post.status === 'failed' ? 'tag-error' : 'tag-warning'}`} style={{ fontSize: '0.65rem' }}>
                          {post.status}
                        </span>
                        {post.caption_style && (
                          <span style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>
                            🎨 {post.caption_style}
                          </span>
                        )}
                      </div>
                      <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)', marginTop: 6 }}>
                        {post.scheduled_time ? new Date(post.scheduled_time).toLocaleDateString('en-IN') : ''}
                      </div>
                    </div>
                  ))}
                </div>

              </>
            )}
          </div>
        )}
      </div>

      {/* Modal preview - rendered once at root level */}
      {selectedPost && tab === 'preview' && (
        <PostPreview post={selectedPost} onClose={() => setSelectedPost(null)} />
      )}
    </div>
  );
}

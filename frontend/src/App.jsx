import React from 'react';
import { Routes, Route } from 'react-router-dom';
import Navbar from './components/Shared/Navbar';
import Sidebar from './components/Shared/Sidebar';
import Home from './pages/Home';
import ProductsPage from './pages/ProductsPage';
import PostsPage from './pages/PostsPage';
import AnalyticsPage from './pages/AnalyticsPage';
import SettingsPage from './pages/SettingsPage';
import { Toaster } from 'react-hot-toast';
import './App.css';

export default function App() {
  const [sidebarOpen, setSidebarOpen] = React.useState(true);

  return (
    <div className="app-layout">
      <Sidebar isOpen={sidebarOpen} onToggle={() => setSidebarOpen(!sidebarOpen)} />
      <div className={`main-content ${!sidebarOpen ? 'expanded' : ''}`}>
        <Navbar onMenuClick={() => setSidebarOpen(!sidebarOpen)} />
        <div className="page-content">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/products" element={<ProductsPage />} />
            <Route path="/posts" element={<PostsPage />} />
            <Route path="/analytics" element={<AnalyticsPage />} />
            <Route path="/settings" element={<SettingsPage />} />
          </Routes>
        </div>
      </div>
      <Toaster
        position="top-right"
        toastOptions={{
          style: {
            background: '#1A1A2E',
            color: '#fff',
            border: '1px solid rgba(255,255,255,0.1)',
            borderRadius: '12px',
          },
          success: { iconTheme: { primary: '#00D4AA', secondary: '#1A1A2E' } },
          error: { iconTheme: { primary: '#FF4757', secondary: '#1A1A2E' } },
        }}
      />
    </div>
  );
}

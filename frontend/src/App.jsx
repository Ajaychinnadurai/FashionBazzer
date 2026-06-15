import React from 'react';
import { Routes, Route, useLocation } from 'react-router-dom';
import Navbar from './components/Shared/Navbar';
import Sidebar from './components/Shared/Sidebar';
import Landing from './pages/Landing';
import FeaturesPage from './pages/FeaturesPage';
import HowItWorksPage from './pages/HowItWorksPage';
import PricingPage from './pages/PricingPage';
import AboutPage from './pages/AboutPage';
import ContactPage from './pages/ContactPage';
import Home from './pages/Home';
import ProductsPage from './pages/ProductsPage';
import PostsPage from './pages/PostsPage';
import AnalyticsPage from './pages/AnalyticsPage';
import SettingsPage from './pages/SettingsPage';
import { Toaster } from 'react-hot-toast';
import './App.css';
import './Landing.css';

// Routes that use the marketing landing layout (no sidebar)
const MARKETING_ROUTES = ['/', '/features', '/how-it-works', '/pricing', '/about', '/contact'];

export default function App() {
  const location = useLocation();
  const isLanding = MARKETING_ROUTES.includes(location.pathname);
  const [sidebarOpen, setSidebarOpen] = React.useState(true);

  // Dashboard layout (with sidebar)
  if (!isLanding) {
    return (
      <div className="app-layout">
        <Sidebar isOpen={sidebarOpen} onToggle={() => setSidebarOpen(!sidebarOpen)} />
        <div className={`main-content ${!sidebarOpen ? 'expanded' : ''}`}>
          <Navbar onMenuClick={() => setSidebarOpen(!sidebarOpen)} />
          <div className="page-content">
            <Routes>
              <Route path="/dashboard" element={<Home />} />
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

  // Landing/marketing layout (no sidebar, full-width pages)
  return (
    <>
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/features" element={<FeaturesPage />} />
        <Route path="/how-it-works" element={<HowItWorksPage />} />
        <Route path="/pricing" element={<PricingPage />} />
        <Route path="/about" element={<AboutPage />} />
        <Route path="/contact" element={<ContactPage />} />
      </Routes>
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
    </>
  );
}

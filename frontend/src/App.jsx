import React from 'react';
import { Routes, Route, useLocation } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import ProtectedRoute from './components/Shared/ProtectedRoute';
import Navbar from './components/Shared/Navbar';
import Sidebar from './components/Shared/Sidebar';
import Landing from './pages/Landing';
import FeaturesPage from './pages/FeaturesPage';
import HowItWorksPage from './pages/HowItWorksPage';
import PricingPage from './pages/PricingPage';
import AboutPage from './pages/AboutPage';
import ContactPage from './pages/ContactPage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import Home from './pages/Home';
import ProductsPage from './pages/ProductsPage';
import PostsPage from './pages/PostsPage';
import AnalyticsPage from './pages/AnalyticsPage';
import SettingsPage from './pages/SettingsPage';
import DataQualityPage from './pages/DataQualityPage';
import { Toaster } from 'react-hot-toast';
import './App.css';
import './Landing.css';

function AppContent() {
  const location = useLocation();

  // Routes that are full-page auth/marketing (no sidebar)
  const FULL_PAGE_ROUTES = ['/', '/features', '/how-it-works', '/pricing', '/about', '/contact', '/login', '/register'];
  const isFullPage = FULL_PAGE_ROUTES.includes(location.pathname);
  const [sidebarOpen, setSidebarOpen] = React.useState(true);

  // Full-page layout (landing + auth pages — no sidebar)
  if (isFullPage) {
    return (
      <>
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route path="/features" element={<FeaturesPage />} />
          <Route path="/how-it-works" element={<HowItWorksPage />} />
          <Route path="/pricing" element={<PricingPage />} />
          <Route path="/about" element={<AboutPage />} />
          <Route path="/contact" element={<ContactPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
        </Routes>
      </>
    );
  }

  // Dashboard layout (with sidebar + auth)
  return (
    <div className="app-layout">
      <Sidebar isOpen={sidebarOpen} onToggle={() => setSidebarOpen(!sidebarOpen)} />
      <div className={`main-content ${!sidebarOpen ? 'expanded' : ''}`}>
        <Navbar onMenuClick={() => setSidebarOpen(!sidebarOpen)} />
        <div className="page-content">
          <Routes>
            <Route path="/dashboard" element={<ProtectedRoute><Home /></ProtectedRoute>} />
            <Route path="/products" element={<ProtectedRoute><ProductsPage /></ProtectedRoute>} />
            <Route path="/data-quality" element={<ProtectedRoute adminOnly={true}><DataQualityPage /></ProtectedRoute>} />
            <Route path="/posts" element={<ProtectedRoute><PostsPage /></ProtectedRoute>} />
            <Route path="/analytics" element={<ProtectedRoute><AnalyticsPage /></ProtectedRoute>} />
            <Route path="/settings" element={<ProtectedRoute><SettingsPage /></ProtectedRoute>} />
          </Routes>
        </div>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <AppContent />
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
    </AuthProvider>
  );
}

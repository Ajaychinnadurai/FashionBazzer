import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import api from '../services/api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // ── Helper: attempt token refresh ──
  const tryRefresh = useCallback(async () => {
    const refresh = localStorage.getItem('refresh_token');
    if (!refresh) return false;
    try {
      const res = await api.post('/auth/refresh/', { refresh });
      const { access } = res.data;
      localStorage.setItem('access_token', access);
      api.defaults.headers.common['Authorization'] = `Bearer ${access}`;
      return true;
    } catch {
      return false;
    }
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    delete api.defaults.headers.common['Authorization'];
    setUser(null);
  }, []);

  // ── Helper: fetch current user profile ──
  const fetchUser = useCallback(async () => {
    try {
      const res = await api.get('/auth/me/');
      setUser(res.data);
    } catch {
      const refreshed = await tryRefresh();
      if (refreshed) {
        try {
          const res = await api.get('/auth/me/');
          setUser(res.data);
        } catch {
          logout();
        }
      } else {
        logout();
      }
    } finally {
      setLoading(false);
    }
  }, [tryRefresh, logout]);

  // ── On mount: restore session if token exists ──
  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token) {
      api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      fetchUser();
    } else {
      setLoading(false);
    }
  }, [fetchUser]);

  const login = useCallback(async (username, password) => {
    const res = await api.post('/auth/login/', { username, password });
    const { access, refresh, user: userData } = res.data;
    localStorage.setItem('access_token', access);
    localStorage.setItem('refresh_token', refresh);
    api.defaults.headers.common['Authorization'] = `Bearer ${access}`;
    setUser(userData);
    return userData;
  }, []);

  const register = useCallback(async (username, password, email) => {
    const res = await api.post('/auth/register/', { username, password, email });
    const { access, refresh, user: userData } = res.data;
    localStorage.setItem('access_token', access);
    localStorage.setItem('refresh_token', refresh);
    api.defaults.headers.common['Authorization'] = `Bearer ${access}`;
    setUser(userData);
    return userData;
  }, []);

  const isAdmin = user?.is_staff || user?.is_superuser;

  return (
    <AuthContext.Provider value={{
      user, loading, login, register, logout, isAdmin, fetchUser,
    }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}

export default AuthContext;

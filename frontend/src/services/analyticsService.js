/**
 * Analytics data processing utilities.
 */
import api from './api';

export async function fetchDashboardStats() {
  try {
    const response = await api.get('/dashboard/overview/');
    return response.data;
  } catch (error) {
    console.error('Failed to fetch dashboard stats:', error);
    return null;
  }
}

export async function fetchClicksByPlatform(days = 30) {
  try {
    const response = await api.get(`/analytics/clicks/?days=${days}`);
    return response.data;
  } catch (error) {
    console.error('Failed to fetch click data:', error);
    return [];
  }
}

export async function fetchEarnings(days = 30) {
  try {
    const response = await api.get(`/analytics/earnings/?days=${days}`);
    return response.data;
  } catch (error) {
    console.error('Failed to fetch earnings:', error);
    return [];
  }
}

export async function fetchPlatformStatus() {
  try {
    const response = await api.get('/analytics/status/');
    return response.data;
  } catch (error) {
    console.error('Failed to fetch platform status:', error);
    return [];
  }
}

export function calculateGrowth(current, previous) {
  if (!previous || previous === 0) return 100;
  return Math.round(((current - previous) / previous) * 100);
}

export function formatCurrency(amount) {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0,
  }).format(amount);
}

/**
 * Dashboard service for triggering data seeding and pipeline operations.
 */
import api from './api';

export async function seedDatabase() {
  const response = await api.get('/dashboard/seed/');
  return response.data;
}

export async function fetchDashboardOverview() {
  const response = await api.get('/dashboard/overview/');
  return response.data;
}

export async function fetchEarnings(days = 30) {
  const response = await api.get(`/analytics/earnings/?days=${days}`);
  return response.data;
}

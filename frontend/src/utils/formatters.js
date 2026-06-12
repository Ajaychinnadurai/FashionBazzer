/**
 * Formatting utilities for FashionBazzer frontend.
 */

/**
 * Format a number with Indian locale (e.g., 12,34,567)
 */
export function formatNumber(num) {
  if (num === null || num === undefined) return '0';
  return Number(num).toLocaleString('en-IN');
}

/**
 * Format currency in INR
 */
export function formatINR(amount) {
  if (amount === null || amount === undefined) return '₹0';
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0,
  }).format(amount);
}

/**
 * Format a date string to Indian locale
 */
export function formatDateTime(dateStr) {
  if (!dateStr) return '-';
  return new Date(dateStr).toLocaleString('en-IN', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

/**
 * Format a date string to relative time (e.g., "2 hours ago")
 */
export function timeAgo(dateStr) {
  if (!dateStr) return '';
  const now = new Date();
  const date = new Date(dateStr);
  const seconds = Math.floor((now - date) / 1000);

  if (seconds < 60) return 'just now';
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  if (days < 30) return `${days}d ago`;
  const months = Math.floor(days / 30);
  return `${months}mo ago`;
}

/**
 * Format percentage
 */
export function formatPercent(value) {
  if (value === null || value === undefined) return '0%';
  return `${Number(value).toFixed(1)}%`;
}

/**
 * Truncate text with ellipsis
 */
export function truncate(text, maxLength = 50) {
  if (!text) return '';
  if (text.length <= maxLength) return text;
  return text.slice(0, maxLength) + '...';
}

/**
 * Format discount display
 */
export function formatDiscount(original, sale) {
  if (!original || !sale) return '';
  const discount = Math.round((1 - sale / original) * 100);
  return `${discount}% OFF`;
}

/**
 * Convert platform name to display name
 */
export function platformDisplayName(platform) {
  const names = {
    telegram: 'Telegram',
    instagram: 'Instagram',
    facebook: 'Facebook',
    pinterest: 'Pinterest',
    twitter: 'Twitter/X',
    threads: 'Threads',
    meesho: 'Meesho',
    amazon: 'Amazon',
    flipkart: 'Flipkart',
  };
  return names[platform] || platform;
}

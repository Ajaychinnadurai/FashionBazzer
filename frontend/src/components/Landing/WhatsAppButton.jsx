import React from 'react';
import { FiMessageCircle } from 'react-icons/fi';

export default function WhatsAppButton({ phone = '911234567890', message }) {
  const text = encodeURIComponent(
    message || 'Hey! I just checked out FashionBazzer — an AI-powered affiliate marketing engine. Want to see how it works? 👗🔥'
  );

  return (
    <a
      href={`https://wa.me/${phone}?text=${text}`}
      target="_blank"
      rel="noreferrer"
      className="whatsapp-fab"
      title="Chat with us on WhatsApp"
      aria-label="Chat on WhatsApp"
    >
      <FiMessageCircle size={28} />
    </a>
  );
}

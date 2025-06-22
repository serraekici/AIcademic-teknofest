import React from 'react';

const TercihChatbot = () => {
  return (
    <iframe
      src="/tercihchatbot.html"
      title="Üniversite Tercih Asistanı"
      allow="popup" // 🌟 Bu satır eklendi
      style={{
        width: '100%',
        minHeight: '100vh',
        border: 'none',
        display: 'block'
      }}
    />
  );
};

export default TercihChatbot;

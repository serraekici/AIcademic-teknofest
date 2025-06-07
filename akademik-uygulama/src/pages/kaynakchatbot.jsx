import React, { useState, useRef } from "react";

// HER KUTUCUK için kullanılacak bileşen
function ResourceCard({ html, onStarClick, isFavorited }) {
  return (
    <div style={{
      border: "1px solid #ccc",
      borderRadius: 14,
      padding: 12,
      marginBottom: 10,
      background: "#fafafa",
      position: "relative"
    }}>
      <div
        style={{ position: "absolute", top: 10, right: 10, cursor: "pointer", fontSize: 20 }}
        onClick={onStarClick}
        title={isFavorited ? "Favorilerden çıkar" : "Favorilere ekle"}
      >
        {isFavorited ? "⭐" : "☆"}
      </div>
      <div dangerouslySetInnerHTML={{ __html: html }} />
    </div>
  );
}

export default function KaynakChatbot({ favorites, setFavorites }) {
  const [messages, setMessages] = useState([
    { sender: "bot", text: "🎓 Hoş geldin!<br>📘 Kitap ya da makale önerisi almak için bir konu yaz. (Örnek: kitap önerisi: yapay zeka)" }
  ]);
  const [input, setInput] = useState("");
  const chatRef = useRef(null);

  React.useEffect(() => {
    if (chatRef.current) chatRef.current.scrollTop = chatRef.current.scrollHeight;
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim()) return;
    const userMessage = { sender: "user", text: input };
    setMessages(msgs => [...msgs, userMessage, { sender: "bot", text: "🔍 Cevap hazırlanıyor..." }]);
    setInput("");

    try {
      const response = await fetch("http://127.0.0.1:5000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: input })
      });
      const data = await response.json();

      setMessages(msgs => {
        const newMsgs = [...msgs];
        const lastBotIdx = newMsgs.map(m => m.sender).lastIndexOf("bot");
        if (data.reply) {
          newMsgs[lastBotIdx] = { sender: "bot", text: data.reply };
        } else {
          newMsgs[lastBotIdx] = { sender: "bot", text: "❌ Bir sonuç alınamadı." };
        }
        return newMsgs;
      });
    } catch (e) {
      setMessages(msgs => {
        const newMsgs = [...msgs];
        const lastBotIdx = newMsgs.map(m => m.sender).lastIndexOf("bot");
        newMsgs[lastBotIdx] = { sender: "bot", text: `⚠️ Sunucu hatası: ${e.message}` };
        return newMsgs;
      });
    }
  };

  const handleKeyDown = e => {
    if (e.key === "Enter") sendMessage();
  };

  return (
    <div style={{
      fontFamily: "Arial, sans-serif",
      backgroundColor: "#ece5dd",
      maxWidth: 500,
      margin: "0 auto",
      borderRadius: 16,
      boxShadow: "0 0 8px rgba(0,0,0,0.1)",
      padding: 16
    }}>
      <h2 style={{ textAlign: "center" }}>📚 Akademik Kaynak Asistanı</h2>
      <div
        ref={chatRef}
        style={{
          border: "none",
          padding: 15,
          height: 350,
          overflowY: "auto",
          backgroundColor: "#fff",
          marginBottom: 10,
          borderRadius: 16,
          display: "flex",
          flexDirection: "column",
          gap: 8
        }}>
        {messages.map((msg, i) => {
        if (msg.sender === "user") {
          // Kullanıcı mesajı balon gibi gösterilecek
          return (
            <div
              key={i}
              style={{
                maxWidth: "70%",
                padding: "8px 12px",
                borderRadius: 20,
                fontSize: 14,
                alignSelf: "flex-end",
                backgroundColor: "#34b7f1",
                color: "#fff",
                marginBottom: 6
              }}
              dangerouslySetInnerHTML={{ __html: msg.text }}
            />
          );
        } else {
          // Bot mesajı: Eğer içinde <div> varsa, bunları kutucuklara ayır
          const cards = msg.text.split('<div').slice(1).map((src, idx) => (
            <ResourceCard
  key={`${i}-${idx}`}
  html={`<div${src}`}
  onStarClick={() => {
    if (favorites.includes(`<div${src}`)) {
      setFavorites(favorites.filter(fav => fav !== `<div${src}`));
    } else {
      setFavorites([...favorites, `<div${src}`]);
    }
  }}
  isFavorited={favorites.includes(`<div${src}`)}
/>

          ));
          // Eğer hiç <div> yoksa, düz baloncuk olarak göster
          if (cards.length === 0)
            return (
              <div
                key={i}
                style={{
                  maxWidth: "70%",
                  padding: "8px 12px",
                  borderRadius: 20,
                  fontSize: 14,
                  alignSelf: "flex-start",
                  backgroundColor: "#dcf8c6",
                  color: "#000",
                  marginBottom: 6
                }}
                dangerouslySetInnerHTML={{ __html: msg.text }}
              />
            );
          // Kaynak kartları
          return <React.Fragment key={i}>{cards}</React.Fragment>;
        }
      })}

      </div>
      <div style={{ display: "flex", width: "100%", gap: 8 }}>
        <input
          type="text"
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Mesajını yaz..."
          style={{
            flexGrow: 1,
            padding: 10,
            border: "1px solid #ccc",
            borderRadius: 20,
            fontSize: 14
          }}
        />
        <button
          onClick={sendMessage}
          style={{
            padding: "10px 16px",
            border: "none",
            backgroundColor: "#25d366",
            color: "white",
            borderRadius: 20,
            fontSize: 14,
            cursor: "pointer"
          }}
        >
          Gönder
        </button>
      </div>
    </div>
  );
}

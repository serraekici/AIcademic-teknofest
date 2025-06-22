import React, { useState, useRef, useEffect } from "react";

// HER KUTUCUK için kullanılacak bileşen
function ResourceCard({ html, onStarClick, isFavorited }) {
  return (
    <div style={{
      border: "1px solid #e0e0e0",
      borderRadius: 14,
      padding: 16,
      marginBottom: 12,
      background: "#ffffff",
      position: "relative",
      boxShadow: "0 2px 8px rgba(0,0,0,0.05)"
    }}>
      <div
        style={{
          position: "absolute",
          top: 12,
          right: 16,
          cursor: "pointer",
          fontSize: 24,
          color: isFavorited ? "#f5b301" : "#ccc",
          transition: "transform 0.2s"
        }}
        onClick={onStarClick}
        title={isFavorited ? "Favorilerden çıkar" : "Favorilere ekle"}
      >
        {isFavorited ? "⭐" : "☆"}
      </div>
      <div
        className="html-content"
        style={{
          fontSize: "15px",
          lineHeight: 1.5,
          color: "#333"
        }}
        dangerouslySetInnerHTML={{ __html: html }}
      />

    </div>
  );
}

export default function KaynakChatbot({ favorites, setFavorites }) {
  const [messages, setMessages] = useState([
    {
      sender: "bot",
      text: "🎓 Hoş geldin!<br>📘 Kitap ya da makale önerisi almak için bir konu yaz. (Örnek: kitap önerisi: yapay zeka)"
    }
  ]);
  const [input, setInput] = useState("");
  const chatRef = useRef(null);

  useEffect(() => {
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
        newMsgs[lastBotIdx] = {
          sender: "bot",
          text: data.reply || "❌ Bir sonuç alınamadı."
        };
        return newMsgs;
      });
    } catch (e) {
      setMessages(msgs => {
        const newMsgs = [...msgs];
        const lastBotIdx = newMsgs.map(m => m.sender).lastIndexOf("bot");
        newMsgs[lastBotIdx] = {
          sender: "bot",
          text: `⚠️ Sunucu hatası: ${e.message}`
        };
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
      background: "linear-gradient(to right, #f3e5f5, #e3f2fd)",
      maxWidth: 600,
      margin: "30px auto",
      borderRadius: 16,
      boxShadow: "0 4px 16px rgba(0,0,0,0.1)",
      padding: 24
    }}>
      <h2 style={{
        textAlign: "center",
        fontSize: 22,
        color: "#4a148c",
        marginBottom: 20
      }}>
        📚 Akademik Kaynak Asistanı
      </h2>

      <div
        ref={chatRef}
        style={{
          border: "none",
          padding: 15,
          height: 400,
          overflowY: "auto",
          backgroundColor: "#ffffff",
          marginBottom: 16,
          borderRadius: 16,
          boxShadow: "inset 0 0 6px rgba(0,0,0,0.05)",
          display: "flex",
          flexDirection: "column",
          gap: 8
        }}
      >
        {messages.map((msg, i) => {
          if (msg.sender === "user") {
            return (
              <div
                key={i}
                style={{
                  maxWidth: "70%",
                  padding: "8px 12px",
                  borderRadius: 20,
                  fontSize: 14,
                  alignSelf: "flex-end",
                  backgroundColor: "#8e24aa",
                  color: "#fff",
                  marginBottom: 6
                }}
                dangerouslySetInnerHTML={{ __html: msg.text }}
              />
            );
          } else {
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
            if (cards.length === 0) {
              return (
                <div
                  key={i}
                  style={{
                    maxWidth: "70%",
                    padding: "8px 12px",
                    borderRadius: 20,
                    fontSize: 14,
                    alignSelf: "flex-start",
                    backgroundColor: "#e0f7fa",
                    color: "#004d40",
                    marginBottom: 6
                  }}
                  dangerouslySetInnerHTML={{ __html: msg.text }}
                />
              );
            }
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
            padding: 12,
            border: "1px solid #ccc",
            borderRadius: 20,
            fontSize: 15
          }}
        />
        <button
          onClick={sendMessage}
          style={{
            padding: "12px 20px",
            border: "none",
            backgroundColor: "#6a1b9a",
            color: "white",
            borderRadius: 20,
            fontSize: 14,
            fontWeight: "bold",
            cursor: "pointer"
          }}
        >
          Gönder
        </button>
      </div>
    </div>
  );
}

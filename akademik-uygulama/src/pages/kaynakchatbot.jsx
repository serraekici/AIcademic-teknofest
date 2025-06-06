import React, { useState, useRef } from "react";

export default function KaynakChatbot() {
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
        {messages.map((msg, i) =>
          <div
            key={i}
            className={msg.sender}
            style={{
              maxWidth: "70%",
              padding: "8px 12px",
              borderRadius: 20,
              fontSize: 14,
              lineHeight: 1.3,
              alignSelf: msg.sender === "user" ? "flex-end" : "flex-start",
              backgroundColor: msg.sender === "user" ? "#34b7f1" : "#dcf8c6",
              color: msg.sender === "user" ? "#fff" : "#000",
              wordWrap: "break-word"
            }}
            dangerouslySetInnerHTML={{ __html: msg.text }}
          />
        )}
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

import { useState } from "react";
import axios from "axios";

function Chat() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([]);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage = { sender: "user", text: input };
    setMessages((prev) => [...prev, userMessage]);

    try {
      const res = await axios.post("http://localhost:5000/chat", { message: input });
      const botMessage = { sender: "bot", text: res.data.reply };
      setMessages((prev) => [...prev, botMessage]);
    } catch (err) {
      const errorMsg = { sender: "bot", text: "❌ Sunucuya ulaşılamadı." };
      setMessages((prev) => [...prev, errorMsg]);
    }

    setInput("");
  };

  return (
    <div className="p-6 max-w-2xl mx-auto">
      <h1 className="text-2xl font-bold mb-4 text-center">🎓 GPT Akademik Asistan</h1>
      <div className="h-96 overflow-y-scroll border rounded p-4 bg-gray-50 space-y-2">
        {messages.map((msg, i) => (
          <div
            key={i}
            className={`text-sm ${msg.sender === "user" ? "text-blue-700 text-right" : "text-green-700 text-left"}`}
          >
            <strong>{msg.sender === "user" ? "Sen:" : "Asistan:"}</strong> {msg.text}
          </div>
        ))}
      </div>
      <div className="mt-4 flex gap-2">
        <input
          className="flex-1 p-2 border rounded"
          type="text"
          value={input}
          placeholder="Bir konu yaz..."
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && sendMessage()}
        />
        <button className="bg-blue-600 text-white px-4 py-2 rounded" onClick={sendMessage}>
          Gönder
        </button>
      </div>
    </div>
  );
}

export default Chat;

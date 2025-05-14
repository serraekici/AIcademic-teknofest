// Chat.jsx
import { useState, useEffect, useRef } from "react";
import axios from "axios";

function Chat() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([]);
  const chatRef = useRef(null);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage = { sender: "user", text: input };
    setMessages((prev) => [...prev, userMessage]);

    try {
      const res = await axios.post("http://localhost:5000/chat", { message: input });
      const botMessage = { sender: "bot", text: res.data.reply };
      setMessages((prev) => [...prev, botMessage]);
    } catch {
      const errorMsg = { sender: "bot", text: "❌ Sunucuya ulaşılamadı." };
      setMessages((prev) => [...prev, errorMsg]);
    }

    setInput("");
  };

  useEffect(() => {
    if (chatRef.current) {
      chatRef.current.scrollTop = chatRef.current.scrollHeight;
    }
  }, [messages]);

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-100 px-4">
      <div className="w-full max-w-2xl bg-white shadow-lg rounded-lg overflow-hidden">
        <div className="bg-blue-600 text-white text-center py-4 text-xl font-bold">
          🎓 GPT Akademik Asistan
        </div>
        <div ref={chatRef} className="h-96 overflow-y-auto p-4 space-y-3 bg-gray-50">
          {messages.map((msg, i) => (
            <div
              key={i}
              className={`p-3 rounded max-w-xs whitespace-pre-wrap ${
                msg.sender === "user"
                  ? "bg-blue-100 self-end text-right ml-auto"
                  : "bg-green-100 self-start text-left mr-auto"
              }`}
            >
              <div className="text-sm text-gray-700 font-semibold">
                {msg.sender === "user" ? "Sen:" : "Asistan:"}
              </div>
              <div
                className="text-gray-900 text-sm"
                dangerouslySetInnerHTML={{ __html: msg.text }}
              />
            </div>
          ))}
        </div>
        <div className="flex p-4 border-t">
          <input
            className="flex-1 border border-gray-300 rounded-l px-3 py-2 focus:outline-none"
            type="text"
            value={input}
            placeholder="Bir konu yaz..."
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && sendMessage()}
          />
          <button
            className="bg-blue-600 text-white px-4 py-2 rounded-r"
            onClick={sendMessage}
          >
            Gönder
          </button>
        </div>
      </div>
    </div>
  );
}

export default Chat;

import React, { useState } from "react";

const studyMethods = [
  { value: "pomodoro", label: "Pomodoro (25 dk çalışma + 5 dk mola)" },
  { value: "blok", label: "Blok (Uzun süreli, odaklanmış seanslar)" },
  { value: "klasik", label: "Klasik (Derse göre gün ayırma)" },
  { value: "yoğun tekrar", label: "Yoğun Tekrar (Sınava yakın sık tekrar)" },
];

const ChatbotPlan = () => {
  const [selectedMethod, setSelectedMethod] = useState("pomodoro");
  const [customRequest, setCustomRequest] = useState("");
  const [planResult, setPlanResult] = useState("");
  const [isLoadingPlan, setIsLoadingPlan] = useState(false);

  const handlePlanRequest = async () => {
    setIsLoadingPlan(true);
    setPlanResult("");
    try {
      const jwt_token = localStorage.getItem("access");
      const res = await fetch("http://localhost:5000/api/generate-study-plan/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          study_method: selectedMethod,
          custom_request: customRequest,
          jwt_token: jwt_token,
        }),
      });
      const data = await res.json();
      if (data.plan) {
        setPlanResult(data.plan);
        localStorage.setItem("studyPlan", data.plan);
      } else {
        setPlanResult("Bir hata oluştu: " + (data.error || "Bilinmeyen hata"));
      }
    } catch (err) {
      setPlanResult("Bir hata oluştu: " + err.message);
    }
    setIsLoadingPlan(false);
  };

  return (
    <div
      style={{
        maxWidth: 600,
        margin: "40px auto",
        background: "linear-gradient(to right, #f3e5f5, #e3f2fd)", // 🌈 geçişli arka plan
        borderRadius: 16,
        boxShadow: "0 4px 20px rgba(0,0,0,0.08)",
        padding: 32,
        fontFamily: "Arial, sans-serif",
        color: "#4a148c",
      }}
    >
      <h2 style={{ textAlign: "center", marginBottom: 24, color: "#6a1b9a" }}>
        📅 GPT ile Çalışma Planı Oluştur
      </h2>

      <label style={{ display: "block", marginBottom: 12 }}>
        <strong>📌 Çalışma Yöntemi Seç:</strong>
        <select
          value={selectedMethod}
          onChange={(e) => setSelectedMethod(e.target.value)}
          style={{
            marginTop: 6,
            width: "100%",
            padding: "10px",
            borderRadius: 10,
            border: "1px solid #ce93d8",
            fontSize: 14,
            background: "#fffff",
            color: "#4a148c",
          }}
        >
          {studyMethods.map((method) => (
            <option key={method.value} value={method.value}>
              {method.label}
            </option>
          ))}
        </select>
      </label>

      <label style={{ display: "block", marginBottom: 20 }}>
        <strong>✏️ Özel İsteklerin:</strong>
        <textarea
          value={customRequest}
          onChange={(e) => setCustomRequest(e.target.value)}
          placeholder="(örneğin: haftaya matematik sınavım var, sabahları daha verimliyim...)"
          style={{
            marginTop: 6,
            width: "100%",
            height: 80,
            padding: 12,
            borderRadius: 10,
            border: "1px solid #ce93d8",
            fontSize: 14,
            fontFamily: "inherit",
            background: "#fffff",
            resize: "vertical",
            color: "#4a148c",
          }}
        />
      </label>

      <button
        type="button"
        onClick={handlePlanRequest}
        disabled={isLoadingPlan}
        style={{
          width: "100%",
          padding: "12px 0",
          borderRadius: 12,
          border: "none",
          background: "#8e24aa",
          color: "#fff",
          fontWeight: "bold",
          fontSize: 15,
          cursor: "pointer",
          marginBottom: 20,
          transition: "background 0.3s",
        }}
      >
        {isLoadingPlan ? "⏳ Plan Oluşturuluyor..." : "Planı Oluştur"}
      </button>

      {planResult && (
        <div
          style={{
            whiteSpace: "pre-line",
            background: "#fff3fc",
            padding: "20px",
            borderRadius: 14,
            boxShadow: "0 2px 8px rgba(0,0,0,0.06)",
            border: "1px solid #f3c4f7",
            color: "#4a148c",
          }}
        >
          <strong>📘 Oluşturulan Plan:</strong>
          <br />
          {planResult}
        </div>
      )}
    </div>
  );
};

export default ChatbotPlan;

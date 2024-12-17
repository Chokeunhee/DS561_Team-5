import React, { useState } from "react";
import axios from "axios";
import "./App.css";

interface Message {
  sender: "User" | "Bot";
  text: string;
  image?: string; // 이미지 URL 추가
}

const App: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");

  const sendMessage = async () => {
    if (!input.trim()) return;

    setMessages([...messages, { sender: "User", text: input }]);

    try {
      const response = await axios.post("http://localhost:3001/chat", {
        message: input,
      });

      const { reply, image } = response.data;

      setMessages((prev) => [
        ...prev,
        {
          sender: "Bot",
          text: reply,
          image: image ? `http://localhost:3001${image}` : undefined,
        },
      ]);
    } catch (error) {
      console.error("Error sending message:", error);
      setMessages((prev) => [
        ...prev,
        { sender: "Bot", text: "Error communicating with the server." },
      ]);
    }

    setInput("");
  };

  return (
    <div className="app-container">
      {/* 타이틀과 이미지 컨테이너 */}
      <div className="title-container">
        <img
          src="/image1.png" // 첫 번째 이미지 경로
          alt="Logo 1"
          className="title-image"
        />
        <h1 className="title">목동 파크 봇</h1>
        <img
          src="/image2.png" // 두 번째 이미지 경로
          alt="Logo 2"
          className="title-image"
        />
      </div>

      {/* 채팅 컨테이너 */}
      <div className="chat-container">
        {messages.map((message, index) => (
          <div
            key={index}
            className={`message ${message.sender === "User" ? "user" : "bot"}`}
          >
            <div
              className="bubble"
              dangerouslySetInnerHTML={{ __html: message.text }}
            />
            {message.image && (
              <img src={message.image} alt="Route" className="chat-image" />
            )}
          </div>
        ))}
      </div>

      {/* 입력 컨테이너 */}
      <div className="input-container">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type your message..."
        />
        <button onClick={sendMessage}>전송</button>
      </div>
    </div>
  );
};

export default App;
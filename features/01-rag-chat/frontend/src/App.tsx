import { FormEvent, useState } from "react";
import "./App.css";

type ChatRole = "user" | "ai";

type ChatMessage = {
  id: number;
  role: ChatRole;
  text: string;
};

type ChatApiResponse = {
  response: string;
};

const API_URL = "http://localhost:5197/api/chat";

export default function App() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: 1,
      role: "ai",
      text: "Hi! Ask me something and I will reply with a mock RAG response."
    }
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const trimmedInput = input.trim();

    if (!trimmedInput || isLoading) {
      return;
    }

    const userMessage: ChatMessage = {
      id: Date.now(),
      role: "user",
      text: trimmedInput
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      const response = await fetch(API_URL, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ message: trimmedInput })
      });

      if (!response.ok) {
        throw new Error(`Request failed with status ${response.status}`);
      }

      const data = (await response.json()) as ChatApiResponse;
      const aiMessage: ChatMessage = {
        id: Date.now() + 1,
        role: "ai",
        text: data.response
      };

      setMessages((prev) => [...prev, aiMessage]);
    } catch {
      const errorMessage: ChatMessage = {
        id: Date.now() + 1,
        role: "ai",
        text: "Sorry, I could not reach the API. Make sure the backend is running on http://localhost:5197."
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <main className="app">
      <section className="chat-card">
        <header className="chat-header">RAG Chat Demo</header>

        <div className="chat-window">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`message-row ${
                message.role === "user" ? "user-row" : "ai-row"
              }`}
            >
              <div
                className={`message-bubble ${
                  message.role === "user" ? "user-bubble" : "ai-bubble"
                }`}
              >
                {message.text}
              </div>
            </div>
          ))}

          {isLoading && (
            <div className="message-row ai-row">
              <div className="message-bubble ai-bubble loading">AI is typing...</div>
            </div>
          )}
        </div>

        <form className="chat-input-row" onSubmit={handleSubmit}>
          <input
            type="text"
            placeholder="Type your message..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={isLoading}
          />
          <button type="submit" disabled={!input.trim() || isLoading}>
            {isLoading ? "Sending..." : "Send"}
          </button>
        </form>
      </section>
    </main>
  );
}

// chatbot-frontend/src/App.jsx

import React, { useState, useRef, useEffect } from 'react';
import './App.css';
import SendIcon from './components/SendIcon';
import BotMessage from './components/BotMessage';
import UserMessage from './components/UserMessage';

function App() {
  const [messages, setMessages] = useState([
    { role: 'bot', content: 'Hello! How can I help you today?', chunks: [] }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Auto scroll to bottom of messages
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Focus input on load
  useEffect(() => {
    inputRef.current.focus();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    // Add user message
    const userMessage = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      // Call your FastAPI endpoint
      const response = await fetch('http://localhost:8000/ask', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question: input }),
      });

      if (!response.ok) {
        throw new Error(`Error: ${response.status}`);
      }

      const data = await response.json();
      
      // Add bot response
      setMessages(prev => [...prev, { 
        role: 'bot', 
        content: data.answer,
        chunks: data.chunks || [] 
      }]);
    } catch (error) {
      console.error('Error:', error);
      setMessages(prev => [...prev, { 
        role: 'bot', 
        content: 'Sorry, I encountered an error. Please try again.',
        chunks: [] 
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="app-container">
      <div className="chat-container">
        <header className="chat-header">
          <h1>News FactChecker</h1>
        </header>
        
        <div className="messages-container">
          {messages.map((message, index) => (
            <div key={index}>
              {message.role === 'bot' ? (
                <BotMessage content={message.content} chunks={message.chunks} />
              ) : (
                <UserMessage content={message.content} />
              )}
            </div>
          ))}
          {isLoading && (
            <div className="bot-message">
              <div className="bot-avatar"></div>
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
        
        <form onSubmit={handleSubmit} className="input-form">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask me anything..."
            ref={inputRef}
            disabled={isLoading}
          />
          <button type="submit" disabled={!input.trim() || isLoading}>
            <SendIcon />
          </button>
        </form>
      </div>
    </div>
  );
}

export default App;
// chatbot-frontend/src/components/BotMessage.jsx

import React from 'react';
import { marked } from 'marked';

const BotMessage = ({ content, chunks }) => {
  // Convert markdown to HTML
  const createMarkup = (text) => {
    return { __html: marked(text) };
  };

  return (
    <div className="bot-message">
      <div className="bot-avatar"></div>
      <div className="message-content">
        <div 
          className="markdown-content" 
          dangerouslySetInnerHTML={createMarkup(content)} 
        />
        
        {chunks && chunks.length > 0 && (
          <div className="chunks-container">
            <p className="chunks-title">Sources:</p>
            {chunks.map((chunk, index) => (
              <div key={index} className="chunk">
                <div className="chunk-header">
                  <p className="chunk-title">{chunk.title}</p>
                  <p className="chunk-score">Relevance: {(1 - chunk.distance).toFixed(2)}</p>
                </div>
                {chunk.link && <a href={chunk.link} target="_blank" rel="noopener noreferrer">{chunk.link}</a>}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default BotMessage;

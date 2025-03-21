// chatbot-frontend/src/components/UserMessage.jsx

import React from 'react';

const UserMessage = ({ content }) => {
  return (
    <div className="user-message">
      <div className="message-content">
        <p>{content}</p>
      </div>
      <div className="user-avatar"></div>
    </div>
  );
};

export default UserMessage;
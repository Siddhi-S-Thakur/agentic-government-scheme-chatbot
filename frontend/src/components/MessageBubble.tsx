import React from 'react';
import { useTranslation } from 'react-i18next';
import type { Message } from '../types/api';
import SchemeResults from './SchemeResults';

interface MessageBubbleProps {
  message: Message;
  onMCQSelect: (value: string) => void;
}

function formatTime(date: Date): string {
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

const TypingIndicator: React.FC = () => (
  <div className="typing-indicator">
    <div className="typing-dot" />
    <div className="typing-dot" />
    <div className="typing-dot" />
  </div>
);

const OPTION_KEYS = ['A', 'B', 'C', 'D', 'E', 'F'];

const MessageBubble: React.FC<MessageBubbleProps> = ({ message, onMCQSelect }) => {
  const { t } = useTranslation();
  const isUser = message.role === 'user';

  return (
    <div className={`message-wrapper ${message.role}`}>
      <div className={`msg-avatar ${message.role}`}>
        {isUser ? '👤' : '🤖'}
      </div>
      <div className="msg-body">
        {message.isLoading ? (
          <TypingIndicator />
        ) : (
          <>
            <div className="msg-bubble">{message.content}</div>

            {/* MCQ Options */}
            {!isUser && message.mcq_options && message.mcq_options.length > 0 && (
              <div className="mcq-options">
                {message.mcq_options.map((opt, i) => (
                  <button
                    key={opt.value}
                    id={`mcq-option-${message.id}-${i}`}
                    className="mcq-option-btn"
                    onClick={() => onMCQSelect(opt.label)}
                    aria-label={`Option ${OPTION_KEYS[i]}: ${opt.label}`}
                  >
                    <span className="mcq-option-key">{OPTION_KEYS[i] ?? i + 1}</span>
                    {opt.label}
                  </button>
                ))}
              </div>
            )}

            {/* Scheme Recommendation Cards */}
            {!isUser && message.recommendations && message.recommendations.length > 0 && (
              <SchemeResults recommendations={message.recommendations} />
            )}

            <div className="msg-time">
              {isUser ? t('you') : t('assistant')} · {formatTime(message.timestamp)}
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default MessageBubble;

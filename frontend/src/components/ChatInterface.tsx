import React, { useRef, useEffect, useState, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import type {
  Message,
  Language,
  InteractionMode,
  SessionState,
  UserProfile,
} from '../types/api';
import { sendChatMessage } from '../api/client';
import MessageBubble from './MessageBubble';
import LanguageSwitcher from './LanguageSwitcher';
import ProfilePanel from './ProfilePanel';

function genId() {
  return Math.random().toString(36).slice(2);
}

const WELCOME_CHIPS_KEY = 'suggestedQuestions';

const ChatInterface: React.FC = () => {
  const { t, i18n } = useTranslation();

  // ── State ────────────────────────────────────────────────
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [language, setLanguage] = useState<Language>('en');
  const [mode, setMode] = useState<InteractionMode>('text');
  const [profile, setProfile] = useState<UserProfile>({});
  const [sessionState, setSessionState] = useState<SessionState | undefined>(undefined);
  const [apiError, setApiError] = useState<string | null>(null);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // ── Auto-scroll ──────────────────────────────────────────
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // ── Auto-resize textarea ─────────────────────────────────
  useEffect(() => {
    const ta = textareaRef.current;
    if (!ta) return;
    ta.style.height = 'auto';
    ta.style.height = `${Math.min(ta.scrollHeight, 120)}px`;
  }, [inputText]);

  // ── Send message ─────────────────────────────────────────
  const sendMessage = useCallback(
    async (text: string) => {
      const trimmed = text.trim();
      if (!trimmed || isLoading) return;

      setApiError(null);

      // Append user message
      const userMsg: Message = {
        id: genId(),
        role: 'user',
        content: trimmed,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, userMsg]);
      setInputText('');

      // Append loading placeholder
      const loadingId = genId();
      setMessages((prev) => [
        ...prev,
        {
          id: loadingId,
          role: 'assistant',
          content: '',
          timestamp: new Date(),
          isLoading: true,
        },
      ]);
      setIsLoading(true);

      try {
        const response = await sendChatMessage({
          message: trimmed,
          session_state: sessionState,
        });

        // Update session state & profile
        setSessionState(response.session_state);
        setProfile(response.profile);
        if (response.detected_language) setLanguage(response.detected_language);

        // Replace loading placeholder with real response
        const assistantMsg: Message = {
          id: loadingId,
          role: 'assistant',
          content: response.response,
          timestamp: new Date(),
          mcq_options: response.mcq_options ?? undefined,
          recommendations: response.recommendations ?? [],
        };
        setMessages((prev) =>
          prev.map((m) => (m.id === loadingId ? assistantMsg : m))
        );
      } catch (err: unknown) {
        const errMsg =
          err instanceof Error ? err.message : t('errorFallback');
        setApiError(errMsg);
        setMessages((prev) => prev.filter((m) => m.id !== loadingId));
      } finally {
        setIsLoading(false);
        textareaRef.current?.focus();
      }
    },
    [isLoading, sessionState, t]
  );

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage(inputText);
    }
  };

  const handleNewChat = () => {
    setMessages([]);
    setProfile({});
    setSessionState(undefined);
    setApiError(null);
    setInputText('');
    textareaRef.current?.focus();
  };

  const handleLanguageChange = (lang: Language) => {
    setLanguage(lang);
    i18n.changeLanguage(lang);
  };

  const handleModeChange = (m: InteractionMode) => {
    setMode(m);
  };

  const suggestedQuestions = t(WELCOME_CHIPS_KEY, { returnObjects: true }) as string[];

  // ── Render ───────────────────────────────────────────────
  return (
    <div className="app-layout">
      {/* ── Sidebar ─────────────────────────────────────── */}
      <aside className="sidebar">
        {/* Logo */}
        <div className="sidebar-header">
          <div className="logo">
            <div className="logo-icon">🏛️</div>
            <div>
              <div className="logo-title">{t('appName')}</div>
            </div>
          </div>
          <div className="logo-subtitle">{t('appSubtitle')}</div>
        </div>

        {/* Language Switcher */}
        <LanguageSwitcher currentLang={language} onChange={handleLanguageChange} />

        {/* Profile Panel */}
        <ProfilePanel profile={profile} />

        {/* Mode Toggle */}
        <div className="mode-toggle">
          <div className="mode-toggle-label">{t('modeLabel')}</div>
          <div className="mode-toggle-btns" role="group" aria-label="Interaction mode">
            <button
              id="mode-btn-text"
              className={`mode-btn ${mode === 'text' ? 'active' : ''}`}
              onClick={() => handleModeChange('text')}
              aria-pressed={mode === 'text'}
            >
              {t('modeText')}
            </button>
            <button
              id="mode-btn-mcq"
              className={`mode-btn ${mode === 'mcq' ? 'active' : ''}`}
              onClick={() => handleModeChange('mcq')}
              aria-pressed={mode === 'mcq'}
            >
              {t('modeMCQ')}
            </button>
          </div>
        </div>

        {/* New Chat */}
        <button id="new-chat-btn" className="new-chat-btn" onClick={handleNewChat}>
          ✏️ {t('newChat')}
        </button>
      </aside>

      {/* ── Main Content ────────────────────────────────── */}
      <main className="main-content">
        {/* Header */}
        <header className="chat-header">
          <div>
            <div className="chat-header-title">{t('appName')}</div>
            <div className="chat-header-sub">{t('appSubtitle')}</div>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <div className="status-dot" title={t('online')} aria-label="System online" />
            <span style={{ fontSize: 'var(--font-size-xs)', color: 'var(--c-text-muted)' }}>
              {t('online')}
            </span>
          </div>
        </header>

        {/* Messages */}
        <div className="messages-container" id="messages-container" role="log" aria-live="polite">
          {messages.length === 0 ? (
            /* Welcome screen */
            <div className="welcome-screen">
              <div className="welcome-hero" aria-hidden="true">🏛️</div>
              <h1 className="welcome-title">{t('welcomeTitle')}</h1>
              <p className="welcome-desc">{t('welcomeDesc')}</p>
              <div className="welcome-chips" role="list" aria-label="Suggested questions">
                {suggestedQuestions.map((q, i) => (
                  <button
                    key={i}
                    id={`welcome-chip-${i}`}
                    className="welcome-chip"
                    role="listitem"
                    onClick={() => sendMessage(q)}
                  >
                    {q}
                  </button>
                ))}
              </div>
            </div>
          ) : (
            messages.map((msg) => (
              <MessageBubble
                key={msg.id}
                message={msg}
                onMCQSelect={sendMessage}
              />
            ))
          )}

          {/* Error notice */}
          {apiError && (
            <div
              role="alert"
              style={{
                padding: '10px 16px',
                background: 'rgba(239,68,68,0.1)',
                border: '1px solid rgba(239,68,68,0.3)',
                borderRadius: 'var(--r-md)',
                color: 'var(--c-danger-400)',
                fontSize: 'var(--font-size-sm)',
                margin: '0 auto',
                maxWidth: 600,
              }}
            >
              ⚠️ {apiError}
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="input-area">
          <div className="input-wrapper">
            <textarea
              ref={textareaRef}
              id="chat-input"
              className="chat-input"
              placeholder={t('inputPlaceholder')}
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyDown={handleKeyDown}
              rows={1}
              aria-label="Chat message input"
              aria-multiline="true"
              disabled={isLoading}
            />
            <button
              id="send-btn"
              className="send-btn"
              onClick={() => sendMessage(inputText)}
              disabled={isLoading || !inputText.trim()}
              aria-label="Send message"
              title="Send"
            >
              {isLoading ? (
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <circle cx="12" cy="12" r="10" strokeDasharray="60" strokeDashoffset="60">
                    <animateTransform attributeName="transform" type="rotate" from="0 12 12" to="360 12 12" dur="1s" repeatCount="indefinite"/>
                  </circle>
                </svg>
              ) : (
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                  <line x1="22" y1="2" x2="11" y2="13" />
                  <polygon points="22 2 15 22 11 13 2 9 22 2" />
                </svg>
              )}
            </button>
          </div>
          <div className="input-hint">{t('inputHint')}</div>
        </div>
      </main>
    </div>
  );
};

export default ChatInterface;

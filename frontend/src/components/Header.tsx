import React from 'react';
import { useTranslation } from 'react-i18next';
import type { Language } from '../types/api';

interface HeaderProps {
  currentLang: Language;
  onLanguageChange: (lang: Language) => void;
  fontScale: number;
  onFontScaleChange: (scale: number) => void;
  onOpenHelpline: () => void;
  onToggleSidebar?: () => void;
  onOpenDashboard?: () => void;
  userAvatarUrl?: string;
  userName?: string;
}

const Header: React.FC<HeaderProps> = ({
  currentLang,
  onLanguageChange,
  fontScale,
  onFontScaleChange,
  onOpenHelpline,
  onToggleSidebar,
  onOpenDashboard,
  userAvatarUrl = 'https://lh3.googleusercontent.com/aida/AEtjO1XJvmXuP3wOf8CwGdCMqkbDCrXFQHxT6GzUgfW0RTyz4xV8UJtv6k97SWtCOShgULogpynYAGlkTjmu8bEpAU0nCCOgShDywZhPc7YPKoj1bLpW_C6yDlrUJcmEUDWH40FnNda91JXbaxSROe0uPDYGzLM_S_czTlaXUMLjlwxrWr3Eug8BRlNzzBeIyFlxfEtXgXwB4RbC8Rif-Ch5sMufbZXLTy_2nbdt4pRevGUd',
  userName = 'Priya Sharma',
}) => {
  const { t } = useTranslation();

  return (
    <header className="gov-header">
      {/* Left pill & mobile toggle */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
        <button
          type="button"
          className="mobile-nav-toggle"
          onClick={onToggleSidebar}
          aria-label="Toggle navigation menu"
        >
          <span className="material-symbols-outlined">menu</span>
        </button>

        <div className="header-portal-pill">
          <span className="material-symbols-outlined">assured_workload</span>
          <span>{t('portalTitle', 'National Digital Scheme Portal • AI Orchestrator')}</span>
        </div>
      </div>

      {/* Right controls */}
      <div className="header-actions">
        {/* Language dropdown */}
        <div className="header-lang-select">
          <span className="material-symbols-outlined" style={{ fontSize: 18, color: 'var(--on-surface-variant)' }}>
            translate
          </span>
          <select
            value={currentLang}
            onChange={(e) => onLanguageChange(e.target.value as Language)}
            aria-label="Select Language"
          >
            <option value="en">English</option>
            <option value="hi">हिंदी (Hindi)</option>
            <option value="mr">मराठी (Marathi)</option>
          </select>
        </div>

        {/* Font size zoom buttons */}
        <div className="header-font-controls" role="group" aria-label="Font size controls">
          <button
            type="button"
            className={`font-btn ${fontScale === 0.9 ? 'active' : ''}`}
            onClick={() => onFontScaleChange(0.9)}
            aria-label="Decrease font size"
            title="Smaller font"
          >
            A-
          </button>
          <button
            type="button"
            className={`font-btn ${fontScale === 1 ? 'active' : ''}`}
            onClick={() => onFontScaleChange(1)}
            aria-label="Default font size"
            title="Default font"
          >
            A
          </button>
          <button
            type="button"
            className={`font-btn ${fontScale === 1.15 ? 'active' : ''}`}
            onClick={() => onFontScaleChange(1.15)}
            aria-label="Increase font size"
            title="Larger font"
          >
            A+
          </button>
        </div>

        {/* Help & Helplines button */}
        <button
          type="button"
          className="header-help-btn"
          onClick={onOpenHelpline}
          title="Official Helpline Numbers"
        >
          <span className="material-symbols-outlined" style={{ fontSize: 18 }}>
            support_agent
          </span>
          <span style={{ display: 'inline' }}>{t('header.help', 'Help & Helplines')}</span>
        </button>

        {/* Profile Avatar */}
        <div
          className="header-avatar-wrap"
          title={`Logged in as ${userName} — Click to view Dashboard`}
          style={{ cursor: 'pointer' }}
          onClick={onOpenDashboard}
        >
          <img
            src={userAvatarUrl}
            alt={userName}
            className="header-avatar"
            onError={(e) => {
              (e.currentTarget as HTMLElement).style.display = 'none';
              const parent = e.currentTarget.parentElement;
              if (parent && !parent.querySelector('.avatar-fallback')) {
                const span = document.createElement('div');
                span.className = 'header-avatar avatar-fallback';
                span.innerText = 'PS';
                parent.insertBefore(span, parent.firstChild);
              }
            }}
          />
          <span className="header-avatar-badge" />
        </div>
      </div>
    </header>
  );
};

export default Header;

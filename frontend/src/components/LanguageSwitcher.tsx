import React from 'react';
import { useTranslation } from 'react-i18next';
import type { Language } from '../types/api';

interface LanguageSwitcherProps {
  currentLang: Language;
  onChange: (lang: Language) => void;
}

const LANGS: { code: Language; label: string; native: string }[] = [
  { code: 'en', label: 'EN', native: 'English' },
  { code: 'hi', label: 'HI', native: 'हिन्दी' },
  { code: 'mr', label: 'MR', native: 'मराठी' },
];

const LanguageSwitcher: React.FC<LanguageSwitcherProps> = ({ currentLang, onChange }) => {
  const { i18n } = useTranslation();

  const handleChange = (lang: Language) => {
    onChange(lang);
    i18n.changeLanguage(lang);
  };

  return (
    <div className="lang-switcher" role="group" aria-label="Language selection">
      {LANGS.map((l) => (
        <button
          key={l.code}
          id={`lang-btn-${l.code}`}
          className={`lang-btn ${currentLang === l.code ? 'active' : ''}`}
          onClick={() => handleChange(l.code)}
          title={l.native}
          aria-pressed={currentLang === l.code}
        >
          {l.native}
        </button>
      ))}
    </div>
  );
};

export default LanguageSwitcher;

import React from 'react';
import { useTranslation } from 'react-i18next';
import type { UserProfile } from '../types/api';

interface ProfilePanelProps {
  profile: UserProfile;
}

const FIELD_ICONS: Record<string, string> = {
  age: '🎂',
  annual_income: '💰',
  state: '📍',
  district: '🗺️',
  occupation: '💼',
  education_level: '🎓',
  caste_category: '🏷️',
  gender: '👤',
  marital_status: '💍',
  is_differently_abled: '♿',
  landholding_acres: '🌾',
};

const FIELD_LABELS: Record<string, string> = {
  age: 'Age',
  annual_income: 'Annual Income',
  state: 'State',
  district: 'District',
  occupation: 'Occupation',
  education_level: 'Education',
  caste_category: 'Category',
  gender: 'Gender',
  marital_status: 'Marital Status',
  is_differently_abled: 'Differently Abled',
  landholding_acres: 'Land (acres)',
};

const HIDDEN_FIELDS = new Set(['preferred_language', 'interaction_mode']);

function formatValue(key: string, value: unknown): string {
  if (typeof value === 'boolean') return value ? 'Yes' : 'No';
  if (key === 'annual_income' && typeof value === 'number') {
    if (value >= 100000) return `₹${(value / 100000).toFixed(1)}L`;
    return `₹${value.toLocaleString('en-IN')}`;
  }
  if (key === 'age' && typeof value === 'number') return `${value} yrs`;
  if (key === 'landholding_acres' && typeof value === 'number') return `${value} ac`;
  return String(value);
}

const ProfilePanel: React.FC<ProfilePanelProps> = ({ profile }) => {
  const { t } = useTranslation();

  const filledFields = Object.entries(profile).filter(
    ([key, v]) =>
      !HIDDEN_FIELDS.has(key) &&
      v !== null &&
      v !== undefined &&
      v !== ''
  );

  return (
    <div className="profile-panel">
      <div className="profile-panel-title">{t('profileTitle')}</div>

      {filledFields.length === 0 ? (
        <div className="profile-empty">
          <div className="profile-empty-icon">👤</div>
          <div>{t('profileEmpty')}</div>
        </div>
      ) : (
        filledFields.map(([key, value]) => (
          <div key={key} className="profile-field">
            <span className="profile-field-label">
              {FIELD_ICONS[key] ?? '•'} {FIELD_LABELS[key] ?? key}
            </span>
            <span className="profile-field-value">{formatValue(key, value)}</span>
          </div>
        ))
      )}
    </div>
  );
};

export default ProfilePanel;

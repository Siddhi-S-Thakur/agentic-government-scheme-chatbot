import React from 'react';
import type { UserProfile } from '../types/api';

interface ProfileDossierProps {
  profile: UserProfile;
  onRefresh?: () => void;
  onPromptAttribute?: (attributeName: string) => void;
  onOpenVaultModal?: () => void;
  onOpenEditProfile?: () => void;
  eligibleCount?: number;
}

function calculateCompletion(profile: UserProfile): { pct: number; pendingCount: number } {
  const trackedKeys = [
    'age',
    'gender',
    'occupation',
    'state',
    'annual_income',
    'landholding_acres',
    'caste_category',
  ];

  let filled = 0;
  for (const k of trackedKeys) {
    const val = (profile as Record<string, unknown>)[k];
    if (val !== undefined && val !== null && val !== '') {
      filled++;
    }
  }

  const pct = Math.round((filled / trackedKeys.length) * 100);
  const pendingCount = trackedKeys.length - filled;
  return { pct, pendingCount };
}

function formatIncome(inc?: number): string {
  if (inc === undefined || inc === null) return 'Unknown';
  if (inc >= 100000) {
    return `₹${(inc / 100000).toFixed(1)} Lakhs / year`;
  }
  return `₹${inc.toLocaleString('en-IN')} / year`;
}

const ProfileDossier: React.FC<ProfileDossierProps> = ({
  profile,
  onRefresh,
  onPromptAttribute,
  onOpenVaultModal,
  onOpenEditProfile,
  eligibleCount = 0,
}) => {
  const { pct, pendingCount } = calculateCompletion(profile);

  // Dynamic values derived from actual profile (no mock fallbacks)
  const ageDisplay = profile.age ? `${profile.age} Years` : null;
  const genderDisplay = profile.gender || null;
  const occDisplay = profile.occupation || null;
  const stateDistDisplay = profile.state
    ? `${profile.state}${profile.district ? ` (${profile.district})` : ''}`
    : null;
  const incomeDisplay = profile.annual_income !== undefined && profile.annual_income !== null
    ? formatIncome(profile.annual_income)
    : null;
  const landDisplay = profile.landholding_acres !== undefined && profile.landholding_acres !== null
    ? `${profile.landholding_acres} Acres`
    : null;
  const casteDisplay = profile.caste_category || null;

  return (
    <aside className="dossier-column" aria-label="Citizen Profile Dossier">
      {/* 1. Main Dossier Card */}
      <div className="dossier-card">
        {/* Header */}
        <div className="dossier-header">
          <div>
            <div className="dossier-title-row">
              <h2 className="dossier-title">Citizen Profile</h2>
              <span className="dossier-badge-live">Saved</span>
            </div>
            <p className="dossier-subtitle">Synchronized with your registered account</p>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
            <button
              type="button"
              className="dossier-refresh-btn"
              onClick={onOpenEditProfile}
              title="Edit Profile Attributes"
              aria-label="Edit Profile"
            >
              <span className="material-symbols-outlined" style={{ fontSize: 18 }}>
                edit
              </span>
            </button>
            <button
              type="button"
              className="dossier-refresh-btn"
              onClick={onRefresh}
              title="Refresh profile state"
              aria-label="Refresh Profile"
            >
              <span className="material-symbols-outlined" style={{ fontSize: 18 }}>
                sync
              </span>
            </button>
          </div>
        </div>

        {/* Profile Completion Index Bar */}
        <div className="profile-completion-box">
          <div className="completion-label-row">
            <span className="completion-label">Eligibility Match Readiness</span>
            <span className="completion-pct">{pct}% Complete</span>
          </div>
          <div className="completion-bar-track">
            <div className="completion-bar-fill" style={{ width: `${pct}%` }} />
          </div>
          <span className="completion-hint">
            {pendingCount > 0
              ? `${pendingCount} parameter${pendingCount > 1 ? 's' : ''} pending for comprehensive scheme matching`
              : 'All primary parameters recorded in your profile'}
          </span>
        </div>

        {/* Profile Attributes List */}
        <div className="profile-attributes-list">
          {/* Age */}
          <div className={`profile-attr-row ${ageDisplay ? '' : 'pending'}`}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.625rem' }}>
              <div className="attr-icon-box">
                <span className="material-symbols-outlined">
                  {ageDisplay ? 'check_circle' : 'pending'}
                </span>
              </div>
              <div className="attr-meta">
                <span className="attr-name">Age</span>
                <span className="attr-value">{ageDisplay || 'Not specified'}</span>
              </div>
            </div>
            {ageDisplay ? (
              <span className="attr-badge">Verified</span>
            ) : (
              <button
                type="button"
                className="attr-ask-btn"
                onClick={onOpenEditProfile}
              >
                + Add
              </button>
            )}
          </div>

          {/* Gender */}
          <div className={`profile-attr-row ${genderDisplay ? '' : 'pending'}`}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.625rem' }}>
              <div className="attr-icon-box">
                <span className="material-symbols-outlined">
                  {genderDisplay ? 'check_circle' : 'pending'}
                </span>
              </div>
              <div className="attr-meta">
                <span className="attr-name">Gender</span>
                <span className="attr-value">{genderDisplay || 'Not specified'}</span>
              </div>
            </div>
            {genderDisplay ? (
              <span className="attr-badge">Recorded</span>
            ) : (
              <button
                type="button"
                className="attr-ask-btn"
                onClick={onOpenEditProfile}
              >
                + Add
              </button>
            )}
          </div>

          {/* Occupation */}
          <div className={`profile-attr-row ${occDisplay ? '' : 'pending'}`}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.625rem' }}>
              <div className="attr-icon-box">
                <span className="material-symbols-outlined">
                  {occDisplay ? 'check_circle' : 'pending'}
                </span>
              </div>
              <div className="attr-meta">
                <span className="attr-name">Occupation</span>
                <span className="attr-value">{occDisplay || 'Not specified'}</span>
              </div>
            </div>
            {occDisplay ? (
              <span className="attr-badge">Recorded</span>
            ) : (
              <button
                type="button"
                className="attr-ask-btn"
                onClick={onOpenEditProfile}
              >
                + Add
              </button>
            )}
          </div>

          {/* State & District */}
          <div className={`profile-attr-row ${stateDistDisplay ? '' : 'pending'}`}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.625rem' }}>
              <div className="attr-icon-box">
                <span className="material-symbols-outlined">
                  {stateDistDisplay ? 'check_circle' : 'pending'}
                </span>
              </div>
              <div className="attr-meta">
                <span className="attr-name">State &amp; District</span>
                <span className="attr-value">{stateDistDisplay || 'Not specified'}</span>
              </div>
            </div>
            {stateDistDisplay ? (
              <span className="attr-badge">Jurisdiction</span>
            ) : (
              <button
                type="button"
                className="attr-ask-btn"
                onClick={onOpenEditProfile}
              >
                + Add
              </button>
            )}
          </div>

          {/* Annual Household Income */}
          <div className={`profile-attr-row ${incomeDisplay ? '' : 'pending'}`}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.625rem' }}>
              <div className="attr-icon-box">
                <span className="material-symbols-outlined">
                  {incomeDisplay ? 'check_circle' : 'pending'}
                </span>
              </div>
              <div className="attr-meta">
                <span className="attr-name">Annual Household Income</span>
                <span className="attr-value">{incomeDisplay || 'Not specified'}</span>
              </div>
            </div>
            {incomeDisplay ? (
              <span className="attr-badge highlight">Declared</span>
            ) : (
              <button
                type="button"
                className="attr-ask-btn"
                onClick={onOpenEditProfile}
              >
                + Add
              </button>
            )}
          </div>

          {/* Land Holding */}
          <div className={`profile-attr-row ${landDisplay ? '' : 'pending'}`}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.625rem' }}>
              <div className="attr-icon-box">
                <span className="material-symbols-outlined">
                  {landDisplay ? 'check_circle' : 'pending'}
                </span>
              </div>
              <div className="attr-meta">
                <span className="attr-name">Land Holding</span>
                <span className="attr-value">{landDisplay || 'Not specified (optional)'}</span>
              </div>
            </div>
            {landDisplay ? (
              <span className="attr-badge">Recorded</span>
            ) : (
              <button
                type="button"
                className="attr-ask-btn"
                onClick={() => onPromptAttribute?.('agricultural landholding')}
              >
                Ask AI
              </button>
            )}
          </div>

          {/* Social Category */}
          <div className={`profile-attr-row ${casteDisplay ? '' : 'pending'}`}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.625rem' }}>
              <div className="attr-icon-box">
                <span className="material-symbols-outlined">
                  {casteDisplay ? 'check_circle' : 'pending'}
                </span>
              </div>
              <div className="attr-meta">
                <span className="attr-name">Social Category</span>
                <span className="attr-value">{casteDisplay || 'Not specified'}</span>
              </div>
            </div>
            {casteDisplay ? (
              <span className="attr-badge">Declared</span>
            ) : (
              <button
                type="button"
                className="attr-ask-btn"
                onClick={() => onPromptAttribute?.('social category (General, OBC, SC, ST, EWS)')}
              >
                Ask AI
              </button>
            )}
          </div>
        </div>

        {/* DBT Highway Readiness Status Box */}
        <div className="dbt-readiness-card">
          <div className="dbt-readiness-head">
            <span className="dbt-readiness-title">
              <span className="material-symbols-outlined">account_balance</span>
              DBT Highway Connectivity
            </span>
            <span className="dbt-readiness-pct">
              {pct >= 60 ? 'Profile Ready' : 'Setup in Progress'}
            </span>
          </div>
          <div className="dbt-pillars-grid">
            <div className="dbt-pillar-item">
              <span className="material-symbols-outlined">verified_user</span>
              <span className="pillar-name">Citizen Account</span>
              <span className="pillar-sub">Active Session</span>
            </div>
            <div className="dbt-pillar-item">
              <span className="material-symbols-outlined">payments</span>
              <span className="pillar-name">DBT Seeding</span>
              <span className="pillar-sub">NPCI Ready</span>
            </div>
            <div className="dbt-pillar-item">
              <span className="material-symbols-outlined">cloud_done</span>
              <span className="pillar-name">Profile Context</span>
              <span className="pillar-sub">{pct}% Mapped</span>
            </div>
          </div>
        </div>

        {/* Kisan & Citizen Advisory Helpline Tile */}
        <div className="helpline-tile">
          <div className="helpline-tile-left">
            <div className="helpline-icon-box">
              <span className="material-symbols-outlined">support_agent</span>
            </div>
            <div className="helpline-meta">
              <span className="helpline-label">National Scheme Helpline</span>
              <a href="tel:18001801551" className="helpline-number">
                1800-180-1551 (Toll-Free)
              </a>
            </div>
          </div>
          <span className="helpline-badge">24x7</span>
        </div>
      </div>

      {/* 2. Scheme Vault Synthesis Summary Card */}
      <div className="vault-synthesis-card">
        <div className="vault-card-head">
          <h3 className="vault-card-title">Scheme Discovery Summary</h3>
          <span className="vault-card-update">Live Context</span>
        </div>

        <div className="vault-metrics-list">
          <div className="vault-metric-row">
            <span>Directly Matched Schemes</span>
            <span className="vault-metric-val green">
              {eligibleCount > 0 ? `${eligibleCount} Schemes Qualified` : 'Inquire via Chat'}
            </span>
          </div>
          <div className="vault-metric-row">
            <span>Central &amp; State Schemes Indexed</span>
            <span className="vault-metric-val blue">148 Official Programs</span>
          </div>
          <div className="vault-metric-row">
            <span>Language Model Guidance</span>
            <span className="vault-metric-val muted">English • हिंदी • मराठी</span>
          </div>
        </div>

        <button
          type="button"
          className="btn-vault-view-all"
          onClick={onOpenVaultModal}
        >
          <span className="material-symbols-outlined" style={{ fontSize: 16 }}>
            visibility
          </span>
          <span>View All Indexed Schemes</span>
        </button>
      </div>
    </aside>
  );
};

export default ProfileDossier;

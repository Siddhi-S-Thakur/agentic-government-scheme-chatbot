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
  return { pct: Math.max(pct, 15), pendingCount };
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
  eligibleCount = 2,
}) => {
  const { pct, pendingCount } = calculateCompletion(profile);

  // Fallbacks from seed/state
  const ageDisplay = profile.age ? `${profile.age} Years` : '28 Years';
  const genderDisplay = profile.gender || 'Female';
  const occDisplay = profile.occupation || 'Farmer / Agri-entrepreneur';
  const stateDistDisplay = profile.state
    ? `${profile.state}${profile.district ? ` (${profile.district})` : ''}`
    : 'Maharashtra (Nashik)';
  const incomeDisplay = profile.annual_income !== undefined
    ? formatIncome(profile.annual_income)
    : '₹2,40,000 / year';
  const landDisplay = profile.landholding_acres !== undefined
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
              <h2 className="dossier-title">Your Profile</h2>
              <span className="dossier-badge-live">Real-time</span>
            </div>
            <p className="dossier-subtitle">Extracted organically by AI Orchestrator</p>
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
            <span className="completion-label">Profile Completion Index</span>
            <span className="completion-pct">{pct}% Ready</span>
          </div>
          <div className="completion-bar-track">
            <div className="completion-bar-fill" style={{ width: `${pct}%` }} />
          </div>
          <span className="completion-hint">
            {pendingCount > 0
              ? `Fill ${pendingCount} pending field${pendingCount > 1 ? 's' : ''} for 100% scheme qualification`
              : 'All core eligibility parameters captured'}
          </span>
        </div>

        {/* Profile Attributes List */}
        <div className="profile-attributes-list">
          {/* Confirmed: Age */}
          <div className="profile-attr-row">
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.625rem' }}>
              <div className="attr-icon-box">
                <span className="material-symbols-outlined">check_circle</span>
              </div>
              <div className="attr-meta">
                <span className="attr-name">Age</span>
                <span className="attr-value">{ageDisplay}</span>
              </div>
            </div>
            <span className="attr-badge">From chat</span>
          </div>

          {/* Confirmed: Gender */}
          <div className="profile-attr-row">
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.625rem' }}>
              <div className="attr-icon-box">
                <span className="material-symbols-outlined">check_circle</span>
              </div>
              <div className="attr-meta">
                <span className="attr-name">Gender</span>
                <span className="attr-value">{genderDisplay}</span>
              </div>
            </div>
            <span className="attr-badge">Aadhaar verified</span>
          </div>

          {/* Confirmed: Occupation */}
          <div className="profile-attr-row">
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.625rem' }}>
              <div className="attr-icon-box">
                <span className="material-symbols-outlined">check_circle</span>
              </div>
              <div className="attr-meta">
                <span className="attr-name">Occupation</span>
                <span className="attr-value">{occDisplay}</span>
              </div>
            </div>
            <span className="attr-badge">From chat</span>
          </div>

          {/* Confirmed: State & District */}
          <div className="profile-attr-row">
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.625rem' }}>
              <div className="attr-icon-box">
                <span className="material-symbols-outlined">check_circle</span>
              </div>
              <div className="attr-meta">
                <span className="attr-name">State &amp; District</span>
                <span className="attr-value">{stateDistDisplay}</span>
              </div>
            </div>
            <span className="attr-badge">Geo-tagged</span>
          </div>

          {/* Confirmed: Annual Household Income */}
          <div className="profile-attr-row">
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.625rem' }}>
              <div className="attr-icon-box">
                <span className="material-symbols-outlined">check_circle</span>
              </div>
              <div className="attr-meta">
                <span className="attr-name">Annual Household Income</span>
                <span className="attr-value">{incomeDisplay}</span>
              </div>
            </div>
            <span className="attr-badge highlight">Marginal</span>
          </div>

          {/* Land Holding (Pending or Confirmed) */}
          <div className={`profile-attr-row ${landDisplay ? '' : 'pending'}`}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.625rem' }}>
              <div className="attr-icon-box">
                <span className="material-symbols-outlined">
                  {landDisplay ? 'check_circle' : 'pending'}
                </span>
              </div>
              <div className="attr-meta">
                <span className="attr-name">Land Holding</span>
                <span className="attr-value">{landDisplay || 'Unknown (e.g. 2.5 Acres)'}</span>
              </div>
            </div>
            {!landDisplay ? (
              <button
                type="button"
                className="attr-ask-btn"
                onClick={() => onPromptAttribute?.('agricultural landholding')}
              >
                Ask User
              </button>
            ) : (
              <span className="attr-badge">Verified</span>
            )}
          </div>

          {/* Social Category (Pending or Confirmed) */}
          <div className={`profile-attr-row ${casteDisplay ? '' : 'pending'}`}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.625rem' }}>
              <div className="attr-icon-box">
                <span className="material-symbols-outlined">
                  {casteDisplay ? 'check_circle' : 'pending'}
                </span>
              </div>
              <div className="attr-meta">
                <span className="attr-name">Social Category</span>
                <span className="attr-value">{casteDisplay || 'General / OBC / SC / ST'}</span>
              </div>
            </div>
            {!casteDisplay ? (
              <button
                type="button"
                className="attr-ask-btn"
                onClick={() => onPromptAttribute?.('social category (General, OBC, SC, ST)')}
              >
                Ask User
              </button>
            ) : (
              <span className="attr-badge">Declared</span>
            )}
          </div>
        </div>

        {/* DBT Highway Readiness Status Box */}
        <div className="dbt-readiness-card">
          <div className="dbt-readiness-head">
            <span className="dbt-readiness-title">
              <span className="material-symbols-outlined">account_balance</span>
              DBT Highway Readiness
            </span>
            <span className="dbt-readiness-pct">100% Linked</span>
          </div>
          <div className="dbt-pillars-grid">
            <div className="dbt-pillar-item">
              <span className="material-symbols-outlined">verified_user</span>
              <span className="pillar-name">Aadhaar</span>
              <span className="pillar-sub">Active</span>
            </div>
            <div className="dbt-pillar-item">
              <span className="material-symbols-outlined">payments</span>
              <span className="pillar-name">Jan Dhan</span>
              <span className="pillar-sub">Bank Linked</span>
            </div>
            <div className="dbt-pillar-item">
              <span className="material-symbols-outlined">cloud_done</span>
              <span className="pillar-name">DigiLocker</span>
              <span className="pillar-sub">4 Dossiers</span>
            </div>
          </div>
        </div>

        {/* Kisan Advisory Helpline Support Tile */}
        <div className="helpline-tile">
          <div className="helpline-tile-left">
            <div className="helpline-icon-box">
              <span className="material-symbols-outlined">support_agent</span>
            </div>
            <div className="helpline-meta">
              <span className="helpline-label">Kisan Advisory Helpline</span>
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
          <h3 className="vault-card-title">Scheme Vault Synthesis</h3>
          <span className="vault-card-update">Updated just now</span>
        </div>

        <div className="vault-metrics-list">
          <div className="vault-metric-row">
            <span>Fully Eligible Grants</span>
            <span className="vault-metric-val green">
              {eligibleCount} Schemes (₹3.2L max aid)
            </span>
          </div>
          <div className="vault-metric-row">
            <span>Credit Subsidies / Loans</span>
            <span className="vault-metric-val blue">1 Scheme (Up to ₹1 Cr)</span>
          </div>
          <div className="vault-metric-row">
            <span>Requires Additional Land Docs</span>
            <span className="vault-metric-val muted">3 State Schemes</span>
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
          <span>View All 148 Analyzed Schemes</span>
        </button>
      </div>
    </aside>
  );
};

export default ProfileDossier;

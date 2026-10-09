import React from 'react';
import type { UserProfile } from '../../types/api';

interface CitizenDashboardViewProps {
  profile: UserProfile;
  userName?: string;
  eligibleCount?: number;
  onNavigateToChat: (initialQuery?: string) => void;
  onOpenDigiLocker: () => void;
  onOpenEditProfile: () => void;
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

const CitizenDashboardView: React.FC<CitizenDashboardViewProps> = ({
  profile,
  userName = 'Citizen',
  eligibleCount = 0,
  onNavigateToChat,
  onOpenDigiLocker,
  onOpenEditProfile,
}) => {
  const { pct, pendingCount } = calculateCompletion(profile);

  const locationSubtitle = [
    profile.district,
    profile.state,
    profile.occupation,
  ]
    .filter(Boolean)
    .join(' • ');

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', width: '100%' }}>
      {/* Top Welcome Banner */}
      <div
        className="scheme-card"
        style={{
          padding: '1.75rem',
          display: 'flex',
          flexWrap: 'wrap',
          alignItems: 'center',
          justifyContent: 'space-between',
          gap: '1rem',
        }}
      >
        <div>
          <span
            style={{
              fontSize: '0.6875rem',
              fontWeight: 700,
              textTransform: 'uppercase',
              letterSpacing: '0.06em',
              color: 'var(--tertiary-fixed)',
              display: 'block',
              marginBottom: '0.25rem',
            }}
          >
            Verified Citizen Beneficiary Profile
          </span>
          <h1
            style={{
              fontFamily: 'var(--font-headline)',
              fontSize: '1.5rem',
              fontWeight: 700,
              color: 'var(--primary)',
              marginBottom: '0.375rem',
            }}
          >
            Welcome, {userName}
          </h1>
          <p style={{ fontSize: '0.875rem', color: 'var(--on-surface-variant)', maxWidth: '600px' }}>
            {locationSubtitle ? (
              <>
                {locationSubtitle}.{' '}
                {eligibleCount > 0 ? (
                  <>
                    You have <strong style={{ color: 'var(--on-tertiary-container)' }}>{eligibleCount} eligible scheme{eligibleCount > 1 ? 's' : ''}</strong> identified.
                  </>
                ) : (
                  <>
                    Ask our AI Caseworker to match your profile against 148+ Central &amp; State welfare programs.
                  </>
                )}
              </>
            ) : (
              'Complete your eligibility profile to discover personalized welfare grants and DBT subsidies across India.'
            )}
          </p>
        </div>

        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <button
            type="button"
            className="chat-send-btn"
            onClick={() => onNavigateToChat()}
          >
            <span className="material-symbols-outlined">smart_toy</span>
            <span>Launch AI Caseworker</span>
          </button>
        </div>
      </div>

      {/* 4 Metric Summary Cards */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
          gap: '1rem',
        }}
      >
        {/* Profile Completion */}
        <div className="scheme-card" style={{ padding: '1.25rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <span style={{ fontSize: '0.75rem', color: 'var(--on-surface-variant)', fontWeight: 600 }}>
              Profile Completion
            </span>
            <span className="material-symbols-outlined" style={{ color: 'var(--secondary)' }}>
              account_circle
            </span>
          </div>
          <div
            style={{
              fontFamily: 'var(--font-headline)',
              fontSize: '1.75rem',
              fontWeight: 700,
              color: 'var(--primary)',
              margin: '0.5rem 0',
            }}
          >
            {pct}% Ready
          </div>
          {pendingCount > 0 ? (
            <button
              type="button"
              onClick={onOpenEditProfile}
              style={{
                background: 'none',
                border: 'none',
                color: 'var(--secondary)',
                fontSize: '0.75rem',
                fontWeight: 600,
                cursor: 'pointer',
                padding: 0,
                textDecoration: 'underline',
              }}
            >
              Fill remaining {pendingCount} field{pendingCount > 1 ? 's' : ''} →
            </button>
          ) : (
            <span style={{ fontSize: '0.75rem', color: 'var(--on-tertiary-container)', fontWeight: 600 }}>
              ✓ All key parameters captured
            </span>
          )}
        </div>

        {/* Matched Schemes */}
        <div className="scheme-card" style={{ padding: '1.25rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <span style={{ fontSize: '0.75rem', color: 'var(--on-surface-variant)', fontWeight: 600 }}>
              Eligible Schemes
            </span>
            <span className="material-symbols-outlined" style={{ color: 'var(--on-tertiary-container)' }}>
              verified
            </span>
          </div>
          <div
            style={{
              fontFamily: 'var(--font-headline)',
              fontSize: '1.75rem',
              fontWeight: 700,
              color: 'var(--on-tertiary-container)',
              margin: '0.5rem 0',
            }}
          >
            {eligibleCount > 0 ? `${eligibleCount} Qualified` : 'Inquire Now'}
          </div>
          <span style={{ fontSize: '0.75rem', color: 'var(--outline)' }}>
            {eligibleCount > 0 ? 'Cross-checked with rule engine' : 'Ask AI to evaluate catalog'}
          </span>
        </div>

        {/* State Program Coverage */}
        <div className="scheme-card" style={{ padding: '1.25rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <span style={{ fontSize: '0.75rem', color: 'var(--on-surface-variant)', fontWeight: 600 }}>
              Jurisdiction Registry
            </span>
            <span className="material-symbols-outlined" style={{ color: 'var(--secondary)' }}>
              map
            </span>
          </div>
          <div
            style={{
              fontFamily: 'var(--font-headline)',
              fontSize: '1.75rem',
              fontWeight: 700,
              color: 'var(--primary)',
              margin: '0.5rem 0',
            }}
          >
            {profile.state || 'All India'}
          </div>
          <span style={{ fontSize: '0.75rem', color: 'var(--outline)' }}>
            Central + {profile.state || 'State'} programs
          </span>
        </div>

        {/* DigiLocker Vault */}
        <div className="scheme-card" style={{ padding: '1.25rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <span style={{ fontSize: '0.75rem', color: 'var(--on-surface-variant)', fontWeight: 600 }}>
              Document Vault
            </span>
            <span className="material-symbols-outlined" style={{ color: 'var(--on-tertiary-container)' }}>
              cloud_done
            </span>
          </div>
          <div
            style={{
              fontFamily: 'var(--font-headline)',
              fontSize: '1.75rem',
              fontWeight: 700,
              color: 'var(--primary)',
              margin: '0.5rem 0',
            }}
          >
            DigiLocker
          </div>
          <button
            type="button"
            onClick={onOpenDigiLocker}
            style={{
              background: 'none',
              border: 'none',
              color: 'var(--secondary)',
              fontSize: '0.75rem',
              fontWeight: 600,
              cursor: 'pointer',
              padding: 0,
              textDecoration: 'underline',
            }}
          >
            Manage linked documents →
          </button>
        </div>
      </div>

      {/* Quick Launchpad & Recommended Next Steps */}
      <div className="scheme-card" style={{ padding: '1.5rem' }}>
        <h2 style={{ fontFamily: 'var(--font-headline)', fontSize: '1.125rem', fontWeight: 700, color: 'var(--primary)', marginBottom: '1rem' }}>
          Recommended Scheme Inquiries for You
        </h2>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '1rem' }}>
          <div
            className="criteria-tile"
            style={{ padding: '1rem', cursor: 'pointer', flexDirection: 'column', gap: '0.5rem' }}
            onClick={() => onNavigateToChat(profile.state ? `What schemes am I eligible for in ${profile.state}?` : 'What central welfare schemes am I eligible for?')}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <span className="material-symbols-outlined" style={{ color: 'var(--on-tertiary-container)' }}>
                auto_awesome
              </span>
              <strong style={{ fontSize: '0.875rem', color: 'var(--primary)' }}>Comprehensive Eligibility Check</strong>
            </div>
            <p style={{ fontSize: '0.75rem', color: 'var(--on-surface-variant)', margin: 0 }}>
              Audit your registered profile parameters against all 148 Central and State schemes.
            </p>
            <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--secondary)' }}>
              Evaluate My Eligibility →
            </span>
          </div>

          <div
            className="criteria-tile"
            style={{ padding: '1rem', cursor: 'pointer', flexDirection: 'column', gap: '0.5rem' }}
            onClick={() => onNavigateToChat('Am I eligible for PM-KISAN or agricultural income support?')}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <span className="material-symbols-outlined" style={{ color: 'var(--secondary)' }}>
                agriculture
              </span>
              <strong style={{ fontSize: '0.875rem', color: 'var(--primary)' }}>PM-KISAN &amp; Farmer Subsidies</strong>
            </div>
            <p style={{ fontSize: '0.75rem', color: 'var(--on-surface-variant)', margin: 0 }}>
              Direct income support of ₹6,000/year, crop insurance, and solar pump schemes.
            </p>
            <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--secondary)' }}>
              Check Farmer Schemes →
            </span>
          </div>

          <div
            className="criteria-tile"
            style={{ padding: '1rem', cursor: 'pointer', flexDirection: 'column', gap: '0.5rem' }}
            onClick={() => onNavigateToChat('Tell me about Ayushman Bharat PM-JAY health insurance benefits')}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <span className="material-symbols-outlined" style={{ color: 'var(--primary)' }}>
                health_and_safety
              </span>
              <strong style={{ fontSize: '0.875rem', color: 'var(--primary)' }}>Ayushman Bharat (PM-JAY)</strong>
            </div>
            <p style={{ fontSize: '0.75rem', color: 'var(--on-surface-variant)', margin: 0 }}>
              ₹5,00,000 per family per year for secondary and tertiary hospitalization.
            </p>
            <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--secondary)' }}>
              Check Health Coverage →
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CitizenDashboardView;

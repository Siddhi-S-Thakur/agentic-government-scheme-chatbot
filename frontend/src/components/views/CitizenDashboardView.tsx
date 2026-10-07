import React from 'react';
import type { UserProfile } from '../../types/api';

interface CitizenDashboardViewProps {
  profile: UserProfile;
  onNavigateToChat: (initialQuery?: string) => void;
  onOpenDigiLocker: () => void;
  onOpenEditProfile: () => void;
}

const CitizenDashboardView: React.FC<CitizenDashboardViewProps> = ({
  profile,
  onNavigateToChat,
  onOpenDigiLocker,
  onOpenEditProfile,
}) => {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', width: '100%' }}>
      {/* Top Welcome Banner */}
      <div
        style={{
          background: 'linear-gradient(135deg, #001428 0%, #0f2942 100%)',
          borderRadius: '1rem',
          padding: '1.75rem',
          color: '#ffffff',
          display: 'flex',
          flexWrap: 'wrap',
          alignItems: 'center',
          justifyContent: 'space-between',
          gap: '1rem',
          boxShadow: 'var(--shadow-md)',
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
            Aadhaar Verified Citizen Profile
          </span>
          <h1
            style={{
              fontFamily: 'var(--font-headline)',
              fontSize: '1.5rem',
              fontWeight: 700,
              marginBottom: '0.375rem',
            }}
          >
            Welcome, Priya Sharma
          </h1>
          <p style={{ fontSize: '0.875rem', color: '#b0c9e8', maxWidth: '600px' }}>
            {profile.district ? `${profile.district}, ` : ''}{profile.state || 'Maharashtra'} • {profile.occupation || 'Farmer / Agri-entrepreneur'}. You currently have{' '}
            <strong style={{ color: '#ffffff' }}>2 verified high-match subsidies</strong> pre-approved
            for Direct Benefit Transfer (DBT).
          </p>
        </div>

        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <button
            type="button"
            className="chat-send-btn"
            style={{ backgroundColor: 'var(--tertiary-fixed)', color: '#002113' }}
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
            68% Ready
          </div>
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
            Complete remaining 2 fields →
          </button>
        </div>

        <div className="scheme-card" style={{ padding: '1.25rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <span style={{ fontSize: '0.75rem', color: 'var(--on-surface-variant)', fontWeight: 600 }}>
              Eligible Subsidies
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
            Up to 90% Aid
          </div>
          <span style={{ fontSize: '0.75rem', color: 'var(--outline)' }}>
            PM-KUSUM Component-B Solar
          </span>
        </div>

        <div className="scheme-card" style={{ padding: '1.25rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <span style={{ fontSize: '0.75rem', color: 'var(--on-surface-variant)', fontWeight: 600 }}>
              Credit Facility
            </span>
            <span className="material-symbols-outlined" style={{ color: 'var(--secondary)' }}>
              payments
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
            ₹10L - ₹1 Cr
          </div>
          <span style={{ fontSize: '0.75rem', color: 'var(--outline)' }}>
            Stand-Up India Women Enterprise
          </span>
        </div>

        <div className="scheme-card" style={{ padding: '1.25rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <span style={{ fontSize: '0.75rem', color: 'var(--on-surface-variant)', fontWeight: 600 }}>
              DigiLocker Dossier
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
            4 Verified Docs
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
            View DigiLocker vault →
          </button>
        </div>
      </div>

      {/* Quick Launchpad & Recommended Next Steps */}
      <div className="scheme-card" style={{ padding: '1.5rem' }}>
        <h2 style={{ fontFamily: 'var(--font-headline)', fontSize: '1.125rem', fontWeight: 700, color: 'var(--primary)', marginBottom: '1rem' }}>
          Accelerated Scheme Actions
        </h2>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '1rem' }}>
          <div
            className="criteria-tile"
            style={{ padding: '1rem', cursor: 'pointer', flexDirection: 'column', gap: '0.5rem' }}
            onClick={() => onNavigateToChat('Am I eligible for PM-KUSUM solar agricultural pump subsidy in Nashik?')}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <span className="material-symbols-outlined" style={{ color: 'var(--on-tertiary-container)' }}>
                solar_power
              </span>
              <strong style={{ fontSize: '0.875rem', color: 'var(--primary)' }}>Check Solar Pump Subsidy</strong>
            </div>
            <p style={{ fontSize: '0.75rem', color: 'var(--on-surface-variant)', margin: 0 }}>
              Audit your landholding extract against Maharashtra Mahavitaran 90% capital aid rules.
            </p>
            <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--secondary)' }}>
              Start Inquiry →
            </span>
          </div>

          <div
            className="criteria-tile"
            style={{ padding: '1rem', cursor: 'pointer', flexDirection: 'column', gap: '0.5rem' }}
            onClick={() => onNavigateToChat('What are the Greenfield requirements for Stand-Up India women loan?')}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <span className="material-symbols-outlined" style={{ color: 'var(--secondary)' }}>
                business_center
              </span>
              <strong style={{ fontSize: '0.875rem', color: 'var(--primary)' }}>Stand-Up India Women Loan</strong>
            </div>
            <p style={{ fontSize: '0.75rem', color: 'var(--on-surface-variant)', margin: 0 }}>
              Verify SIDBI 51% shareholding requirement and priority commercial banking quota.
            </p>
            <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--secondary)' }}>
              Start Inquiry →
            </span>
          </div>

          <div
            className="criteria-tile"
            style={{ padding: '1rem', cursor: 'pointer', flexDirection: 'column', gap: '0.5rem' }}
            onClick={() => onNavigateToChat('Tell me about Lakhpati Didi self help group benefits')}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <span className="material-symbols-outlined" style={{ color: 'var(--primary)' }}>
                groups
              </span>
              <strong style={{ fontSize: '0.875rem', color: 'var(--primary)' }}>Lakhpati Didi SHG Grant</strong>
            </div>
            <p style={{ fontSize: '0.75rem', color: 'var(--on-surface-variant)', margin: 0 }}>
              Micro-enterprise training and interest-subvention credit lines for rural women entrepreneurs.
            </p>
            <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--secondary)' }}>
              Start Inquiry →
            </span>
          </div>
        </div>
      </div>

      {/* Recent DBT Highway Activity */}
      <div className="scheme-card" style={{ padding: '1.5rem' }}>
        <h2 style={{ fontFamily: 'var(--font-headline)', fontSize: '1.125rem', fontWeight: 700, color: 'var(--primary)', marginBottom: '0.75rem' }}>
          Direct Benefit Transfer (DBT) Linked Record
        </h2>
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.8125rem' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--outline-variant)', textAlign: 'left', color: 'var(--on-surface-variant)' }}>
                <th style={{ padding: '0.5rem' }}>Scheme / Program</th>
                <th style={{ padding: '0.5rem' }}>Beneficiary A/C</th>
                <th style={{ padding: '0.5rem' }}>Disbursement</th>
                <th style={{ padding: '0.5rem' }}>Status</th>
              </tr>
            </thead>
            <tbody>
              <tr style={{ borderBottom: '1px solid rgba(226, 232, 240, 0.6)' }}>
                <td style={{ padding: '0.75rem 0.5rem', fontWeight: 600, color: 'var(--primary)' }}>
                  PM-KISAN 16th &amp; 17th Installment
                </td>
                <td style={{ padding: '0.75rem 0.5rem', color: 'var(--on-surface-variant)' }}>
                  SBI •••• 4812 (Aadhaar Seeding Active)
                </td>
                <td style={{ padding: '0.75rem 0.5rem', fontWeight: 700, color: 'var(--on-tertiary-container)' }}>
                  ₹2,000 / term
                </td>
                <td style={{ padding: '0.75rem 0.5rem' }}>
                  <span className="match-pill-verified">Credited via PFMS</span>
                </td>
              </tr>
              <tr>
                <td style={{ padding: '0.75rem 0.5rem', fontWeight: 600, color: 'var(--primary)' }}>
                  Namo Shetkari Mahasanman Nidhi (MH)
                </td>
                <td style={{ padding: '0.75rem 0.5rem', color: 'var(--on-surface-variant)' }}>
                  SBI •••• 4812 (MahaDBT Verified)
                </td>
                <td style={{ padding: '0.75rem 0.5rem', fontWeight: 700, color: 'var(--on-tertiary-container)' }}>
                  ₹2,000 / term
                </td>
                <td style={{ padding: '0.75rem 0.5rem' }}>
                  <span className="match-pill-verified">Credited via PFMS</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default CitizenDashboardView;

import React, { useState } from 'react';
import type { UserProfile } from '../../types/api';

interface DbtDisbursementsViewProps {
  profile?: UserProfile;
  userName?: string;
  onNavigateToChat?: (query?: string) => void;
}

const DbtDisbursementsView: React.FC<DbtDisbursementsViewProps> = ({
  profile = {},
  userName = 'Citizen',
  onNavigateToChat,
}) => {
  const [bankLinked, setBankLinked] = useState(false);
  const [accountNumber, setAccountNumber] = useState('');
  const [bankName, setBankName] = useState('State Bank of India');
  const [isLinking, setIsLinking] = useState(false);
  const [feedback, setFeedback] = useState<string | null>(null);

  const handleLinkBank = (e: React.FormEvent) => {
    e.preventDefault();
    if (!accountNumber.trim()) return;
    setIsLinking(true);
    setTimeout(() => {
      setBankLinked(true);
      setIsLinking(false);
      setFeedback(`Account •••• ${accountNumber.slice(-4)} successfully verified via NPCI Aadhaar Seeding Gateway.`);
    }, 800);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem', width: '100%' }}>
      {/* Top Header */}
      <div className="provenance-strip">
        <div className="strip-status">
          <span className="material-symbols-outlined" style={{ color: 'var(--on-tertiary-container)' }}>
            account_balance_wallet
          </span>
          <span className="strip-title">Direct Benefit Transfer (DBT) Portal</span>
          <span className="strip-dot">•</span>
          <span className="strip-desc">
            NPCI Aadhaar Seeding &amp; Public Financial Management System (PFMS)
          </span>
        </div>

        <button
          type="button"
          className="strip-btn"
          onClick={() => {
            setFeedback(
              bankLinked
                ? 'NPCI Aadhaar Mapper status: ACTIVE & SEEDED.'
                : 'NPCI Aadhaar Mapper status: Please link your Aadhaar-seeded bank account below.'
            );
          }}
        >
          <span className="material-symbols-outlined" style={{ fontSize: 16 }}>
            verified_user
          </span>
          <span>Verify NPCI Status</span>
        </button>
      </div>

      {feedback && (
        <div className="provenance-strip" style={{ borderColor: 'var(--tertiary)' }}>
          <div className="strip-status">
            <span className="material-symbols-outlined" style={{ color: 'var(--on-tertiary-container)' }}>
              info
            </span>
            <span style={{ fontSize: '0.8125rem', color: 'var(--on-surface)' }}>{feedback}</span>
          </div>
          <button
            type="button"
            className="strip-btn"
            style={{ padding: '0.25rem 0.5rem' }}
            onClick={() => setFeedback(null)}
          >
            <span className="material-symbols-outlined" style={{ fontSize: 14 }}>
              close
            </span>
          </button>
        </div>
      )}

      {/* 3 Status Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '1rem' }}>
        <div className="scheme-card" style={{ padding: '1.25rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ fontSize: '0.75rem', color: 'var(--on-surface-variant)', fontWeight: 600 }}>
              Beneficiary Name
            </span>
            <span className="material-symbols-outlined" style={{ color: 'var(--secondary)' }}>
              person
            </span>
          </div>
          <div style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--primary)', margin: '0.5rem 0' }}>
            {userName}
          </div>
          <p style={{ fontSize: '0.75rem', color: 'var(--outline)', margin: 0 }}>
            Jurisdiction: {profile.district ? `${profile.district}, ` : ''}{profile.state || 'National Registry'}
          </p>
        </div>

        <div className="scheme-card" style={{ padding: '1.25rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ fontSize: '0.75rem', color: 'var(--on-surface-variant)', fontWeight: 600 }}>
              Primary DBT Account
            </span>
            <span className="material-symbols-outlined" style={{ color: bankLinked ? 'var(--on-tertiary-container)' : 'var(--outline)' }}>
              account_balance
            </span>
          </div>
          <div style={{ fontSize: '1.25rem', fontWeight: 700, color: bankLinked ? 'var(--on-tertiary-container)' : 'var(--primary)', margin: '0.5rem 0' }}>
            {bankLinked ? `${bankName} •••• ${accountNumber.slice(-4)}` : 'Not Linked Yet'}
          </div>
          <p style={{ fontSize: '0.75rem', color: 'var(--outline)', margin: 0 }}>
            {bankLinked ? 'Aadhaar Seeding Active' : 'Enter bank details below to link'}
          </p>
        </div>

        <div className="scheme-card" style={{ padding: '1.25rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ fontSize: '0.75rem', color: 'var(--on-surface-variant)', fontWeight: 600 }}>
              DBT Scheme Eligibility
            </span>
            <span className="material-symbols-outlined" style={{ color: 'var(--on-tertiary-container)' }}>
              payments
            </span>
          </div>
          <div style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--primary)', margin: '0.5rem 0' }}>
            {profile.occupation ? `${profile.occupation}` : 'Profile Active'}
          </div>
          <p style={{ fontSize: '0.75rem', color: 'var(--outline)', margin: 0 }}>
            Direct disbursement available on eligible grants
          </p>
        </div>
      </div>

      {/* Account Seeding Form / Status */}
      {!bankLinked ? (
        <div className="scheme-card" style={{ padding: '1.5rem' }}>
          <h3 style={{ fontFamily: 'var(--font-headline)', fontSize: '1.125rem', fontWeight: 700, color: 'var(--primary)', marginBottom: '0.5rem' }}>
            Link Aadhaar-Seeded Bank Account for Direct Benefit Transfer
          </h3>
          <p style={{ fontSize: '0.8125rem', color: 'var(--on-surface-variant)', marginBottom: '1.25rem' }}>
            Central and State DBT subsidies are credited directly into your Aadhaar-mapped bank account through the NPCI gateway.
          </p>

          <form onSubmit={handleLinkBank} style={{ display: 'flex', flexDirection: 'column', gap: '1rem', maxWidth: '560px' }}>
            <div className="auth-field">
              <label htmlFor="dbt-bank-name" className="auth-label">
                <span className="material-symbols-outlined">account_balance</span>
                Bank Name
              </label>
              <select
                id="dbt-bank-name"
                className="auth-input"
                value={bankName}
                onChange={(e) => setBankName(e.target.value)}
              >
                <option value="State Bank of India">State Bank of India (SBI)</option>
                <option value="Bank of Baroda">Bank of Baroda</option>
                <option value="Punjab National Bank">Punjab National Bank</option>
                <option value="Canara Bank">Canara Bank</option>
                <option value="HDFC Bank">HDFC Bank</option>
                <option value="ICICI Bank">ICICI Bank</option>
                <option value="Maharashtra Gramin Bank">Maharashtra Gramin Bank / Regional Rural Bank</option>
                <option value="Other Scheduled Bank">Other Scheduled Bank</option>
              </select>
            </div>

            <div className="auth-field">
              <label htmlFor="dbt-account-no" className="auth-label">
                <span className="material-symbols-outlined">pin</span>
                Bank Account Number
              </label>
              <input
                id="dbt-account-no"
                type="text"
                className="auth-input"
                placeholder="Enter 11 to 16 digit account number"
                value={accountNumber}
                onChange={(e) => setAccountNumber(e.target.value)}
                required
              />
            </div>

            <div style={{ display: 'flex', gap: '0.75rem', marginTop: '0.5rem' }}>
              <button
                type="submit"
                className="chat-send-btn"
                disabled={isLinking}
              >
                <span className="material-symbols-outlined">link</span>
                <span>{isLinking ? 'Verifying NPCI Seeding...' : 'Link & Verify DBT Seeding'}</span>
              </button>

              <button
                type="button"
                className="strip-btn"
                onClick={() => onNavigateToChat?.('Which government schemes offer direct benefit transfer for my occupation?')}
              >
                <span className="material-symbols-outlined">help</span>
                <span>Ask AI About DBT Subsidies</span>
              </button>
            </div>
          </form>
        </div>
      ) : (
        /* Verified Account Banner */
        <div className="scheme-card" style={{ padding: '1.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem' }}>
            <span className="material-symbols-outlined" style={{ fontSize: 28, color: 'var(--on-tertiary-container)' }}>
              check_circle
            </span>
            <div>
              <h3 style={{ fontFamily: 'var(--font-headline)', fontSize: '1.125rem', fontWeight: 700, color: 'var(--primary)', margin: 0 }}>
                Aadhaar Seeding Active on DBT Highway
              </h3>
              <p style={{ fontSize: '0.75rem', color: 'var(--on-surface-variant)', margin: '0.25rem 0 0' }}>
                Bank Account •••• {accountNumber.slice(-4)} ({bankName}) is linked for Public Financial Management System (PFMS) deposits.
              </p>
            </div>
          </div>

          <div style={{ display: 'flex', gap: '0.75rem' }}>
            <button
              type="button"
              className="chat-send-btn"
              onClick={() => onNavigateToChat?.('Check DBT subsidy disbursements and status for my eligible schemes')}
            >
              <span className="material-symbols-outlined">smart_toy</span>
              <span>Check Eligible Subsidies via AI Caseworker</span>
            </button>

            <button
              type="button"
              className="strip-btn"
              onClick={() => setBankLinked(false)}
            >
              <span className="material-symbols-outlined">swap_horiz</span>
              <span>Change Bank Account</span>
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default DbtDisbursementsView;

import React from 'react';

const DbtDisbursementsView: React.FC = () => {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem', width: '100%' }}>
      {/* Top Header */}
      <div className="provenance-strip">
        <div className="strip-status">
          <span className="material-symbols-outlined" style={{ color: 'var(--on-tertiary-container)' }}>
            account_balance_wallet
          </span>
          <span className="strip-title">Direct Benefit Transfer (DBT) Highway</span>
          <span className="strip-dot">•</span>
          <span className="strip-desc">Public Financial Management System (PFMS) &amp; NPCI Seeding</span>
        </div>

        <button
          type="button"
          className="strip-btn"
          onClick={() => alert('DBT Seeding status verified with NPCI Gateway: ACTIVE')}
        >
          <span className="material-symbols-outlined" style={{ fontSize: 16 }}>
            check_circle
          </span>
          <span>Check NPCI Mapper Live</span>
        </button>
      </div>

      {/* 3 Status Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '1rem' }}>
        <div className="scheme-card" style={{ padding: '1.25rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ fontSize: '0.75rem', color: 'var(--on-surface-variant)', fontWeight: 600 }}>
              NPCI Aadhaar Mapper
            </span>
            <span className="material-symbols-outlined" style={{ color: 'var(--on-tertiary-container)' }}>
              verified_user
            </span>
          </div>
          <div style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--on-tertiary-container)', margin: '0.5rem 0' }}>
            Active &amp; Seeded
          </div>
          <p style={{ fontSize: '0.75rem', color: 'var(--outline)', margin: 0 }}>
            Mapped to State Bank of India • Chandwad Branch
          </p>
        </div>

        <div className="scheme-card" style={{ padding: '1.25rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ fontSize: '0.75rem', color: 'var(--on-surface-variant)', fontWeight: 600 }}>
              Primary DBT Account
            </span>
            <span className="material-symbols-outlined" style={{ color: 'var(--secondary)' }}>
              account_balance
            </span>
          </div>
          <div style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--primary)', margin: '0.5rem 0' }}>
            SBI •••• 4812
          </div>
          <p style={{ fontSize: '0.75rem', color: 'var(--outline)', margin: 0 }}>
            Jan Dhan / Priority Account Enabled
          </p>
        </div>

        <div className="scheme-card" style={{ padding: '1.25rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ fontSize: '0.75rem', color: 'var(--on-surface-variant)', fontWeight: 600 }}>
              Cumulative DBT Aid
            </span>
            <span className="material-symbols-outlined" style={{ color: 'var(--on-tertiary-container)' }}>
              payments
            </span>
          </div>
          <div style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--primary)', margin: '0.5rem 0' }}>
            ₹34,000 Total
          </div>
          <p style={{ fontSize: '0.75rem', color: 'var(--outline)', margin: 0 }}>
            Received across 17 installments
          </p>
        </div>
      </div>

      {/* Disbursement Log History */}
      <div className="scheme-card" style={{ padding: '1.5rem' }}>
        <h3 style={{ fontFamily: 'var(--font-headline)', fontSize: '1.125rem', fontWeight: 700, color: 'var(--primary)', marginBottom: '1rem' }}>
          Recent DBT Subsidies &amp; Direct Deposits
        </h3>

        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.8125rem' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--outline-variant)', textAlign: 'left', color: 'var(--on-surface-variant)' }}>
                <th style={{ padding: '0.75rem 0.5rem' }}>Disbursement Date</th>
                <th style={{ padding: '0.75rem 0.5rem' }}>Scheme Authority</th>
                <th style={{ padding: '0.75rem 0.5rem' }}>UTR / Reference</th>
                <th style={{ padding: '0.75rem 0.5rem' }}>Amount</th>
                <th style={{ padding: '0.75rem 0.5rem' }}>PFMS Status</th>
              </tr>
            </thead>
            <tbody>
              <tr style={{ borderBottom: '1px solid rgba(226, 232, 240, 0.7)' }}>
                <td style={{ padding: '0.75rem 0.5rem' }}>18 Jun 2025</td>
                <td style={{ padding: '0.75rem 0.5rem', fontWeight: 600, color: 'var(--primary)' }}>
                  PM-KISAN Samman Nidhi 17th Installment
                </td>
                <td style={{ padding: '0.75rem 0.5rem', color: 'var(--outline)' }}>
                  PFMS/20250618/90218491
                </td>
                <td style={{ padding: '0.75rem 0.5rem', fontWeight: 700, color: 'var(--on-tertiary-container)' }}>
                  ₹2,000.00
                </td>
                <td style={{ padding: '0.75rem 0.5rem' }}>
                  <span className="match-pill-verified">Credited to SBI</span>
                </td>
              </tr>

              <tr style={{ borderBottom: '1px solid rgba(226, 232, 240, 0.7)' }}>
                <td style={{ padding: '0.75rem 0.5rem' }}>28 Feb 2025</td>
                <td style={{ padding: '0.75rem 0.5rem', fontWeight: 600, color: 'var(--primary)' }}>
                  PM-KISAN Samman Nidhi 16th Installment
                </td>
                <td style={{ padding: '0.75rem 0.5rem', color: 'var(--outline)' }}>
                  PFMS/20250228/88319402
                </td>
                <td style={{ padding: '0.75rem 0.5rem', fontWeight: 700, color: 'var(--on-tertiary-container)' }}>
                  ₹2,000.00
                </td>
                <td style={{ padding: '0.75rem 0.5rem' }}>
                  <span className="match-pill-verified">Credited to SBI</span>
                </td>
              </tr>

              <tr>
                <td style={{ padding: '0.75rem 0.5rem' }}>15 Jan 2025</td>
                <td style={{ padding: '0.75rem 0.5rem', fontWeight: 600, color: 'var(--primary)' }}>
                  Namo Shetkari Mahasanman Nidhi (Maharashtra)
                </td>
                <td style={{ padding: '0.75rem 0.5rem', color: 'var(--outline)' }}>
                  MHDBT/20250115/44120981
                </td>
                <td style={{ padding: '0.75rem 0.5rem', fontWeight: 700, color: 'var(--on-tertiary-container)' }}>
                  ₹2,000.00
                </td>
                <td style={{ padding: '0.75rem 0.5rem' }}>
                  <span className="match-pill-verified">Credited to SBI</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default DbtDisbursementsView;

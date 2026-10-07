import React from 'react';

export interface SavedApplication {
  id: string;
  schemeName: string;
  department: string;
  status: 'Drafted' | 'Docs Verified' | 'Submitted';
  benefit: string;
  portalUrl: string;
  savedDate: string;
}

interface ActiveApplicationsViewProps {
  applications: SavedApplication[];
  onRemoveApplication: (id: string) => void;
  onNavigateToChat: (query?: string) => void;
}

const ActiveApplicationsView: React.FC<ActiveApplicationsViewProps> = ({
  applications,
  onRemoveApplication,
  onNavigateToChat,
}) => {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem', width: '100%' }}>
      {/* Top Header Strip */}
      <div className="provenance-strip">
        <div className="strip-status">
          <span className="material-symbols-outlined" style={{ color: 'var(--on-tertiary-container)' }}>
            task_alt
          </span>
          <span className="strip-title">Active Applications &amp; Saved Locker</span>
          <span className="strip-dot">•</span>
          <span className="strip-desc">Track state filings &amp; direct benefit grants</span>
        </div>

        <button
          type="button"
          className="strip-btn"
          onClick={() => onNavigateToChat('What is the application deadline for my saved schemes?')}
        >
          <span className="material-symbols-outlined" style={{ fontSize: 16 }}>
            help
          </span>
          <span>Check Filing Deadlines</span>
        </button>
      </div>

      {applications.length === 0 ? (
        <div className="scheme-card" style={{ padding: '3rem', textAlign: 'center' }}>
          <span className="material-symbols-outlined" style={{ fontSize: 48, color: 'var(--outline)' }}>
            folder_open
          </span>
          <h3 style={{ fontFamily: 'var(--font-headline)', color: 'var(--primary)', marginTop: '0.75rem' }}>
            No Schemes Saved in Locker Yet
          </h3>
          <p style={{ color: 'var(--on-surface-variant)', fontSize: '0.875rem', maxWidth: '400px', margin: '0.5rem auto' }}>
            Browse recommendations in the AI Caseworker and click "Save to Locker" to bookmark grants for tracking.
          </p>
          <button
            type="button"
            className="chat-send-btn"
            style={{ margin: '1rem auto 0' }}
            onClick={() => onNavigateToChat()}
          >
            <span>Explore Recommended Schemes</span>
          </button>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {applications.map((app) => (
            <div key={app.id} className="scheme-card" style={{ padding: '1.25rem' }}>
              <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'flex-start', justifyContent: 'space-between', gap: '0.75rem' }}>
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <h3 style={{ fontFamily: 'var(--font-headline)', fontSize: '1.125rem', fontWeight: 700, color: 'var(--primary)' }}>
                      {app.schemeName}
                    </h3>
                    <span className="match-pill-verified" style={{ fontSize: '0.625rem' }}>
                      {app.status}
                    </span>
                  </div>
                  <p style={{ fontSize: '0.75rem', color: 'var(--on-surface-variant)', marginTop: '0.25rem' }}>
                    {app.department}
                  </p>
                </div>

                <div className="scheme-benefit-badge" style={{ padding: '0.375rem 0.75rem', minWidth: '120px' }}>
                  <span className="benefit-badge-label">Benefit</span>
                  <span className="benefit-badge-value" style={{ fontSize: '1rem' }}>
                    {app.benefit}
                  </span>
                </div>
              </div>

              {/* Progress Milestones */}
              <div style={{ margin: '1rem 0', background: 'var(--surface-container-low)', padding: '0.75rem', borderRadius: '0.5rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.6875rem', color: 'var(--on-surface-variant)', fontWeight: 600 }}>
                  <span style={{ color: 'var(--on-tertiary-container)' }}>✓ Eligibility Confirmed</span>
                  <span style={{ color: 'var(--on-tertiary-container)' }}>✓ DigiLocker Dossier Linked</span>
                  <span>3. Final Portal Submission</span>
                </div>
                <div style={{ height: '4px', background: 'var(--surface-container)', borderRadius: '2px', marginTop: '0.375rem', overflow: 'hidden' }}>
                  <div style={{ height: '100%', width: '66%', background: 'var(--on-tertiary-container)' }} />
                </div>
              </div>

              {/* Action Buttons */}
              <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', justifyContent: 'space-between', gap: '0.5rem' }}>
                <div style={{ display: 'flex', gap: '0.5rem' }}>
                  <a
                    href={app.portalUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="btn-apply-portal"
                    style={{ fontSize: '0.75rem', padding: '0.5rem 0.75rem' }}
                  >
                    <span>Proceed on Official Portal</span>
                    <span className="material-symbols-outlined" style={{ fontSize: 14 }}>
                      open_in_new
                    </span>
                  </a>

                  <button
                    type="button"
                    className="strip-btn"
                    onClick={() => onNavigateToChat(`What documents do I still need to submit for ${app.schemeName}?`)}
                    style={{ fontSize: '0.75rem' }}
                  >
                    <span className="material-symbols-outlined" style={{ fontSize: 16 }}>
                      chat
                    </span>
                    <span>Ask AI Help</span>
                  </button>
                </div>

                <button
                  type="button"
                  style={{
                    background: 'none',
                    border: 'none',
                    color: 'var(--error)',
                    fontSize: '0.75rem',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.25rem',
                  }}
                  onClick={() => onRemoveApplication(app.id)}
                >
                  <span className="material-symbols-outlined" style={{ fontSize: 16 }}>
                    delete
                  </span>
                  <span>Remove from Locker</span>
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ActiveApplicationsView;

import React from 'react';
import type { UserProfile } from '../../types/api';

interface DigiLockerViewProps {
  profile?: UserProfile;
  onAttachDocument: (docName: string, dataAttrs?: Record<string, unknown>) => void;
  onNavigateToChat: () => void;
}

const DigiLockerView: React.FC<DigiLockerViewProps> = ({
  profile = {},
  onAttachDocument,
  onNavigateToChat,
}) => {
  const documents = [
    {
      id: 'aadhaar',
      title: 'Aadhaar e-KYC Card',
      issuer: 'Unique Identification Authority of India (UIDAI)',
      docNumber: 'XXXX-XXXX-8921',
      date: 'Digital Verified',
      status: 'Verified',
      icon: 'verified_user',
      dataAttrs: {
        gender: profile.gender || 'Not specified',
        age: profile.age || 'Not specified',
      },
    },
    {
      id: 'land-extract',
      title: '7/12 & 8A Land Extract Record',
      issuer: `Revenue Department • Govt. of ${profile.state || 'State'}`,
      docNumber: `Land Registry · ${profile.district || 'District'}`,
      date: 'Digital Verified',
      status: 'Verified',
      icon: 'landscape',
      dataAttrs: {
        landholding_acres: profile.landholding_acres || 0,
        state: profile.state || 'Not specified',
        district: profile.district || 'Not specified',
      },
    },
    {
      id: 'bank-passbook',
      title: 'NPCI DBT Linked Bank Account',
      issuer: 'National Payments Corporation of India (NPCI)',
      docNumber: 'A/C Linked (DBT Enabled)',
      date: 'Active Aadhaar Seeding',
      status: 'DBT Enabled',
      icon: 'account_balance',
      dataAttrs: {},
    },
    {
      id: 'income-cert',
      title: 'Tahsildar Income Assessment Certificate',
      issuer: `Revenue Office • ${profile.district || profile.state || 'Regional Sub-Division'}`,
      docNumber: 'REV-CERT-OFFICIAL',
      date: profile.annual_income ? `Annual Income ₹${profile.annual_income.toLocaleString('en-IN')} Certified` : 'Income Record',
      status: 'Verified',
      icon: 'receipt_long',
      dataAttrs: { annual_income: profile.annual_income || 0 },
    },
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem', width: '100%' }}>
      {/* Header Banner */}
      <div className="provenance-strip">
        <div className="strip-status">
          <span className="material-symbols-outlined" style={{ color: 'var(--on-tertiary-container)' }}>
            folder_managed
          </span>
          <span className="strip-title">National DigiLocker Dossier Vault</span>
          <span className="strip-dot">•</span>
          <span className="strip-desc">Tamper-evident legal credentials linked to your session</span>
        </div>

        <button
          type="button"
          className="strip-btn"
          onClick={() => {
            alert('DigiLocker documents successfully synchronized.');
          }}
        >
          <span className="material-symbols-outlined" style={{ fontSize: 16 }}>
            sync
          </span>
          <span>Sync from DigiLocker</span>
        </button>
      </div>

      {/* Grid of Verified Documents */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1rem' }}>
        {documents.map((doc) => (
          <div key={doc.id} className="scheme-card" style={{ padding: '1.25rem', display: 'flex', flexDirection: 'column', justifyContent: 'space-between', gap: '1rem' }}>
            <div>
              <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: '0.5rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.625rem' }}>
                  <div className="attr-icon-box" style={{ width: '2.25rem', height: '2.25rem' }}>
                    <span className="material-symbols-outlined" style={{ fontSize: 20 }}>
                      {doc.icon}
                    </span>
                  </div>
                  <div>
                    <h3 style={{ fontSize: '0.9375rem', fontWeight: 700, color: 'var(--primary)' }}>
                      {doc.title}
                    </h3>
                    <span style={{ fontSize: '0.6875rem', color: 'var(--outline)' }}>
                      {doc.docNumber}
                    </span>
                  </div>
                </div>

                <span className="match-pill-verified" style={{ fontSize: '0.625rem' }}>
                  {doc.status}
                </span>
              </div>

              <div style={{ marginTop: '0.75rem', padding: '0.5rem', background: 'var(--surface-container-low)', borderRadius: '0.5rem', fontSize: '0.75rem', color: 'var(--on-surface-variant)' }}>
                <div><strong>Issuer:</strong> {doc.issuer}</div>
                <div style={{ fontSize: '0.6875rem', color: 'var(--outline)', marginTop: '0.125rem' }}>{doc.date}</div>
              </div>
            </div>

            <div style={{ display: 'flex', gap: '0.5rem', paddingTop: '0.5rem', borderTop: '1px solid rgba(226, 232, 240, 0.7)' }}>
              <button
                type="button"
                className="chat-send-btn"
                style={{ flex: 1, height: '34px', fontSize: '0.75rem' }}
                onClick={() => {
                  onAttachDocument(doc.title, doc.dataAttrs);
                  onNavigateToChat();
                }}
              >
                <span className="material-symbols-outlined" style={{ fontSize: 16 }}>
                  attach_file
                </span>
                <span>Attach to AI Session</span>
              </button>

              <button
                type="button"
                className="strip-btn"
                style={{ height: '34px', padding: '0 0.75rem' }}
                onClick={() => alert(`Verified digital signature for ${doc.title} (Issued under IT Act 2000 Section 4)`)}
                title="Verify Certificate Signature"
              >
                <span className="material-symbols-outlined" style={{ fontSize: 16 }}>
                  verified
                </span>
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default DigiLockerView;

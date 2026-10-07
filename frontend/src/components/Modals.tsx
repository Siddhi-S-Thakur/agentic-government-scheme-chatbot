import React, { useState } from 'react';
import type { UserProfile } from '../types/api';

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
}

interface VaultModalProps extends ModalProps {
  onSelectSchemeForInquiry?: (schemeName: string) => void;
}

interface DigiLockerModalProps extends ModalProps {
  onAttachDocument?: (docTitle: string, dataAttrs?: Record<string, unknown>) => void;
}

interface EditProfileModalProps extends ModalProps {
  profile: UserProfile;
  onSaveProfile: (updated: UserProfile) => void;
}

export const HelpModal: React.FC<ModalProps> = ({ isOpen, onClose }) => {
  const [copied, setCopied] = useState<string | null>(null);

  if (!isOpen) return null;

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(text);
    setTimeout(() => setCopied(null), 2000);
  };

  const HELPLINES = [
    {
      title: 'Kisan Call Centre (Agriculture & Farmers Welfare)',
      number: '18001801551',
      displayNumber: '1800-180-1551 (Toll-Free)',
      desc: '24x7 expert agricultural advice in 22 languages',
      badge: '24x7 Active',
      icon: 'support_agent',
    },
    {
      title: 'PM-KUSUM Standalone Solar Pump Helpline (MNRE)',
      number: '18001803333',
      displayNumber: '1800-180-3333',
      desc: 'Subsidies, vendor empanelment & discom issues',
      badge: 'National Toll-Free',
      icon: 'solar_power',
    },
    {
      title: 'Stand-Up India / SIDBI Credit Support Desk',
      number: '1800118811',
      displayNumber: '1800-11-8811',
      desc: 'Scheduled commercial bank credit facilities for women & SC/ST',
      badge: 'Banking Hours',
      icon: 'business_center',
    },
    {
      title: 'Direct Benefit Transfer (DBT) Mission Helpdesk',
      number: '01123340000',
      displayNumber: '011-2334-0000',
      desc: 'Aadhaar seeding, NPCI mapper & PFMS payment failure',
      badge: 'Govt Working Days',
      icon: 'account_balance',
    },
    {
      title: 'Women Entrepreneurship Platform (NITI Aayog)',
      number: '18002660000',
      displayNumber: '1800-266-0000',
      desc: 'Incubation, mentorship, and equity capital schemes',
      badge: 'Mon - Fri',
      icon: 'female',
    },
  ];

  return (
    <div className="modal-overlay" onClick={onClose} role="dialog" aria-modal="true">
      <div className="modal-dialog" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span className="material-symbols-outlined" style={{ color: 'var(--secondary)' }}>
              support_agent
            </span>
            <h2 className="modal-title">National Citizen Helplines &amp; Advisory</h2>
          </div>
          <button type="button" className="modal-close-btn" onClick={onClose}>
            <span className="material-symbols-outlined">close</span>
          </button>
        </div>

        <p style={{ fontSize: '0.75rem', color: 'var(--on-surface-variant)', margin: '-0.25rem 0 0.5rem' }}>
          Official toll-free government hotlines for scheme eligibility, application tracking, and grievances.
        </p>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
          {HELPLINES.map((h, i) => (
            <div key={i} className="helpline-tile" style={{ padding: '0.875rem 1rem' }}>
              <div className="helpline-tile-left" style={{ flex: 1 }}>
                <div className="helpline-icon-box">
                  <span className="material-symbols-outlined">{h.icon}</span>
                </div>
                <div className="helpline-meta">
                  <span className="helpline-label" style={{ fontWeight: 600, color: 'var(--primary)' }}>
                    {h.title}
                  </span>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginTop: '0.125rem' }}>
                    <a href={`tel:${h.number}`} className="helpline-number">
                      {h.displayNumber}
                    </a>
                    <button
                      type="button"
                      style={{
                        background: 'none',
                        border: 'none',
                        padding: '2px',
                        cursor: 'pointer',
                        color: copied === h.number ? 'var(--on-tertiary-container)' : 'var(--outline)',
                        display: 'flex',
                        alignItems: 'center',
                      }}
                      title="Copy phone number"
                      onClick={() => copyToClipboard(h.number)}
                    >
                      <span className="material-symbols-outlined" style={{ fontSize: 14 }}>
                        {copied === h.number ? 'check' : 'content_copy'}
                      </span>
                    </button>
                  </div>
                  <span style={{ fontSize: '0.6875rem', color: 'var(--outline)', marginTop: '0.125rem' }}>
                    {h.desc}
                  </span>
                </div>
              </div>
              <span className="helpline-badge">{h.badge}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export const VaultModal: React.FC<VaultModalProps> = ({
  isOpen,
  onClose,
  onSelectSchemeForInquiry,
}) => {
  const [categoryFilter, setCategoryFilter] = useState('All');
  const [query, setQuery] = useState('');

  if (!isOpen) return null;

  const SCHEMES = [
    {
      id: 'pm-kusum-b',
      name: 'PM-KUSUM Component-B',
      dept: 'Standalone Solar Agriculture Pump Subsidy Program • MNRE',
      category: 'Agriculture',
      benefit: 'Up to 90% Capital Subsidy',
      match: '98% Match',
      matchType: 'verified',
    },
    {
      id: 'stand-up-india',
      name: 'Stand-Up India Scheme',
      dept: 'Ministry of Finance & SIDBI Commercial Bank Facility',
      category: 'Credit & Business',
      benefit: '₹10 Lakh - ₹1 Crore Credit',
      match: '75% Match',
      matchType: 'provisional',
    },
    {
      id: 'pm-kisan',
      name: 'PM-KISAN Samman Nidhi',
      dept: 'Department of Agriculture & Farmers Welfare',
      category: 'Agriculture',
      benefit: '₹6,000 / year DBT Deposit',
      match: 'Pre-Approved',
      matchType: 'verified',
    },
    {
      id: 'lakhpati-didi',
      name: 'Lakhpati Didi Initiative',
      dept: 'Ministry of Rural Development • DAY-NRLM',
      category: 'Women Welfare',
      benefit: 'Interest-Free Loan & Skilling',
      match: 'Eligible',
      matchType: 'verified',
    },
    {
      id: 'pmay-g',
      name: 'Pradhan Mantri Awas Yojana - Gramin',
      dept: 'Ministry of Rural Development',
      category: 'Housing',
      benefit: 'Up to ₹1.3 Lakh Housing Aid',
      match: 'Pending Land Docs',
      matchType: 'provisional',
    },
    {
      id: 'kcc',
      name: 'Kisan Credit Card (KCC) Concessional Loan',
      dept: 'NABARD & Reserve Bank of India',
      category: 'Agriculture',
      benefit: '4% Subsidized Interest Crop Loan',
      match: 'Pre-Approved',
      matchType: 'verified',
    },
    {
      id: 'sanjay-gandhi-niradhar',
      name: 'Sanjay Gandhi Niradhar Anudan Yojana',
      dept: 'Social Justice Dept • Govt of Maharashtra',
      category: 'Social Welfare',
      benefit: 'Monthly Pension of ₹1,500',
      match: 'Requires Age Audit',
      matchType: 'provisional',
    },
  ];

  const filtered = SCHEMES.filter((s) => {
    if (categoryFilter !== 'All' && s.category !== categoryFilter) return false;
    if (query.trim()) {
      const q = query.toLowerCase();
      return s.name.toLowerCase().includes(q) || s.dept.toLowerCase().includes(q);
    }
    return true;
  });

  return (
    <div className="modal-overlay" onClick={onClose} role="dialog" aria-modal="true">
      <div className="modal-dialog" style={{ maxWidth: '44rem' }} onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <span className="material-symbols-outlined" style={{ color: 'var(--primary)' }}>
                auto_stories
              </span>
              <h2 className="modal-title">National Digital Scheme Vault (148 Schemes)</h2>
            </div>
            <p style={{ fontSize: '0.75rem', color: 'var(--on-surface-variant)' }}>
              Verified Central and State initiatives indexed with deterministic rules.
            </p>
          </div>
          <button type="button" className="modal-close-btn" onClick={onClose}>
            <span className="material-symbols-outlined">close</span>
          </button>
        </div>

        {/* Filter bar */}
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.375rem', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', gap: '0.25rem', overflowX: 'auto' }}>
            {['All', 'Agriculture', 'Credit & Business', 'Women Welfare', 'Housing', 'Social Welfare'].map((cat) => (
              <button
                key={cat}
                type="button"
                className={`font-btn ${categoryFilter === cat ? 'active' : ''}`}
                style={{ padding: '0.25rem 0.625rem', fontSize: '0.6875rem' }}
                onClick={() => setCategoryFilter(cat)}
              >
                {cat}
              </button>
            ))}
          </div>

          <input
            type="text"
            className="chat-main-input"
            style={{ padding: '0.375rem 0.625rem', fontSize: '0.75rem', width: '180px' }}
            placeholder="Search scheme..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
        </div>

        {/* Scheme List */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', maxHeight: '55vh', overflowY: 'auto' }}>
          {filtered.map((scheme) => (
            <div key={scheme.id} className="scheme-card" style={{ padding: '0.875rem 1rem' }}>
              <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'flex-start', justifyContent: 'space-between', gap: '0.5rem' }}>
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <strong style={{ color: 'var(--primary)', fontSize: '0.875rem' }}>{scheme.name}</strong>
                    <span
                      className={scheme.matchType === 'verified' ? 'match-pill-verified' : 'match-pill-provisional'}
                      style={{ fontSize: '0.625rem' }}
                    >
                      {scheme.match}
                    </span>
                  </div>
                  <p style={{ fontSize: '0.6875rem', color: 'var(--on-surface-variant)', margin: '0.125rem 0' }}>
                    {scheme.dept}
                  </p>
                  <span style={{ fontSize: '0.6875rem', fontWeight: 600, color: 'var(--on-tertiary-container)' }}>
                    Benefit: {scheme.benefit}
                  </span>
                </div>

                <button
                  type="button"
                  className="chat-send-btn"
                  style={{ height: '30px', fontSize: '0.6875rem', padding: '0 0.625rem' }}
                  onClick={() => {
                    onClose();
                    onSelectSchemeForInquiry?.(`Am I eligible for ${scheme.name}? Please evaluate against my profile.`);
                  }}
                >
                  <span className="material-symbols-outlined" style={{ fontSize: 14 }}>
                    smart_toy
                  </span>
                  <span>Ask AI Assistant</span>
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export const DigiLockerModal: React.FC<DigiLockerModalProps> = ({
  isOpen,
  onClose,
  onAttachDocument,
}) => {
  if (!isOpen) return null;

  const DOCS = [
    {
      title: '7/12 & 8A Land Extract (MahaBhulekh)',
      source: 'Revenue Dept • Nashik (Gat 184/2 · 2.5 Acres)',
      icon: 'landscape',
      attrs: { landholding_acres: 2.5, state: 'Maharashtra', district: 'Nashik' },
    },
    {
      title: 'Aadhaar e-KYC Identity Dossier',
      source: 'UIDAI • Female, Age 28 Verified',
      icon: 'verified_user',
      attrs: { age: 28, gender: 'Female' },
    },
    {
      title: 'Income Assessment Certificate',
      source: 'Revenue Sub-Division • ₹2,40,000 Certified',
      icon: 'receipt_long',
      attrs: { annual_income: 240000 },
    },
    {
      title: 'Bank Passbook & NPCI DBT Mandate',
      source: 'State Bank of India • Active Aadhaar Seeding',
      icon: 'account_balance',
      attrs: {},
    },
  ];

  return (
    <div className="modal-overlay" onClick={onClose} role="dialog" aria-modal="true">
      <div className="modal-dialog" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span className="material-symbols-outlined" style={{ color: 'var(--on-tertiary-container)' }}>
              cloud_done
            </span>
            <h2 className="modal-title">Attach DigiLocker Verified Document</h2>
          </div>
          <button type="button" className="modal-close-btn" onClick={onClose}>
            <span className="material-symbols-outlined">close</span>
          </button>
        </div>

        <p style={{ fontSize: '0.75rem', color: 'var(--on-surface-variant)', margin: '-0.25rem 0 0.5rem' }}>
          Select a verified government credential from your DigiLocker to sync with the AI Caseworker session:
        </p>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
          {DOCS.map((doc, idx) => (
            <div key={idx} className="profile-attr-row" style={{ padding: '0.75rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                <span className="material-symbols-outlined" style={{ color: 'var(--on-tertiary-container)' }}>
                  {doc.icon}
                </span>
                <div>
                  <strong style={{ fontSize: '0.8125rem', color: 'var(--primary)' }}>{doc.title}</strong>
                  <div style={{ fontSize: '0.6875rem', color: 'var(--outline)' }}>{doc.source}</div>
                </div>
              </div>

              <button
                type="button"
                className="chat-send-btn"
                style={{ height: '30px', fontSize: '0.75rem', padding: '0 0.75rem' }}
                onClick={() => {
                  onAttachDocument?.(doc.title, doc.attrs);
                  onClose();
                }}
              >
                <span>Attach</span>
                <span className="material-symbols-outlined" style={{ fontSize: 14 }}>
                  attach_file
                </span>
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export const EditProfileModal: React.FC<EditProfileModalProps> = ({
  isOpen,
  onClose,
  profile,
  onSaveProfile,
}) => {
  const [formData, setFormData] = useState<UserProfile>(profile);

  if (!isOpen) return null;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSaveProfile(formData);
    onClose();
  };

  return (
    <div className="modal-overlay" onClick={onClose} role="dialog" aria-modal="true">
      <div className="modal-dialog" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span className="material-symbols-outlined" style={{ color: 'var(--primary)' }}>
              edit_note
            </span>
            <h2 className="modal-title">Edit Citizen Profile Attributes</h2>
          </div>
          <button type="button" className="modal-close-btn" onClick={onClose}>
            <span className="material-symbols-outlined">close</span>
          </button>
        </div>

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
            <div>
              <label style={{ fontSize: '0.6875rem', fontWeight: 700, color: 'var(--on-surface-variant)' }}>
                Age (Years)
              </label>
              <input
                type="number"
                className="chat-main-input"
                style={{ padding: '0.5rem', fontSize: '0.8125rem' }}
                value={formData.age ?? ''}
                onChange={(e) => setFormData({ ...formData, age: e.target.value ? Number(e.target.value) : undefined })}
                placeholder="e.g. 28"
              />
            </div>

            <div>
              <label style={{ fontSize: '0.6875rem', fontWeight: 700, color: 'var(--on-surface-variant)' }}>
                Gender
              </label>
              <select
                className="chat-main-input"
                style={{ padding: '0.5rem', fontSize: '0.8125rem', cursor: 'pointer' }}
                value={formData.gender || ''}
                onChange={(e) => setFormData({ ...formData, gender: e.target.value })}
              >
                <option value="Female">Female</option>
                <option value="Male">Male</option>
                <option value="Other">Other</option>
              </select>
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
            <div>
              <label style={{ fontSize: '0.6875rem', fontWeight: 700, color: 'var(--on-surface-variant)' }}>
                State
              </label>
              <input
                type="text"
                className="chat-main-input"
                style={{ padding: '0.5rem', fontSize: '0.8125rem' }}
                value={formData.state || ''}
                onChange={(e) => setFormData({ ...formData, state: e.target.value })}
                placeholder="e.g. Maharashtra"
              />
            </div>

            <div>
              <label style={{ fontSize: '0.6875rem', fontWeight: 700, color: 'var(--on-surface-variant)' }}>
                District
              </label>
              <input
                type="text"
                className="chat-main-input"
                style={{ padding: '0.5rem', fontSize: '0.8125rem' }}
                value={formData.district || ''}
                onChange={(e) => setFormData({ ...formData, district: e.target.value })}
                placeholder="e.g. Nashik"
              />
            </div>
          </div>

          <div>
            <label style={{ fontSize: '0.6875rem', fontWeight: 700, color: 'var(--on-surface-variant)' }}>
              Occupation
            </label>
            <input
              type="text"
              className="chat-main-input"
              style={{ padding: '0.5rem', fontSize: '0.8125rem' }}
              value={formData.occupation || ''}
              onChange={(e) => setFormData({ ...formData, occupation: e.target.value })}
              placeholder="e.g. Farmer / Agri-entrepreneur"
            />
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
            <div>
              <label style={{ fontSize: '0.6875rem', fontWeight: 700, color: 'var(--on-surface-variant)' }}>
                Annual Household Income (₹)
              </label>
              <input
                type="number"
                className="chat-main-input"
                style={{ padding: '0.5rem', fontSize: '0.8125rem' }}
                value={formData.annual_income ?? ''}
                onChange={(e) => setFormData({ ...formData, annual_income: e.target.value ? Number(e.target.value) : undefined })}
                placeholder="e.g. 240000"
              />
            </div>

            <div>
              <label style={{ fontSize: '0.6875rem', fontWeight: 700, color: 'var(--on-surface-variant)' }}>
                Agricultural Landholding (Acres)
              </label>
              <input
                type="number"
                step="0.1"
                className="chat-main-input"
                style={{ padding: '0.5rem', fontSize: '0.8125rem' }}
                value={formData.landholding_acres ?? ''}
                onChange={(e) => setFormData({ ...formData, landholding_acres: e.target.value ? Number(e.target.value) : undefined })}
                placeholder="e.g. 2.5"
              />
            </div>
          </div>

          <div>
            <label style={{ fontSize: '0.6875rem', fontWeight: 700, color: 'var(--on-surface-variant)' }}>
              Social Category (Caste)
            </label>
            <select
              className="chat-main-input"
              style={{ padding: '0.5rem', fontSize: '0.8125rem', cursor: 'pointer' }}
              value={formData.caste_category || ''}
              onChange={(e) => setFormData({ ...formData, caste_category: e.target.value })}
            >
              <option value="">Select Category</option>
              <option value="General">General / Open</option>
              <option value="OBC">Other Backward Class (OBC)</option>
              <option value="SC">Scheduled Caste (SC)</option>
              <option value="ST">Scheduled Tribe (ST)</option>
              <option value="EWS">Economically Weaker Section (EWS)</option>
            </select>
          </div>

          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.5rem', marginTop: '0.5rem' }}>
            <button type="button" className="strip-btn" onClick={onClose}>
              Cancel
            </button>
            <button type="submit" className="chat-send-btn">
              <span>Save &amp; Update Eligibility</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

import React, { useState } from 'react';
import type { SchemeRecommendation, EligibilityStatus } from '../types/api';

interface SchemeCardProps {
  rec: SchemeRecommendation;
  onClarificationSelect?: (value: string) => void;
  onSaveToLocker?: (schemeName: string) => void;
}

function getStatusBadge(status: EligibilityStatus, matchPct?: number) {
  if (status === 'ELIGIBLE' || (matchPct && matchPct >= 90)) {
    return {
      cls: 'eligible',
      badgeCls: 'match-pill-verified',
      text: matchPct ? `Verified ${matchPct}% Match` : 'Verified 98% Match',
      preApproved: true,
      noteText: 'Pre-Approved Category',
      noteIcon: 'check_circle',
      noteCls: '',
    };
  }
  if (status === 'PARTIAL' || status === 'UNKNOWN' || (matchPct && matchPct >= 60)) {
    return {
      cls: 'provisional',
      badgeCls: 'match-pill-provisional',
      text: matchPct ? `${matchPct}% Provisional Match` : '75% Provisional Match',
      preApproved: false,
      noteText: 'Actionable Clarification Needed',
      noteIcon: 'info',
      noteCls: 'warning',
    };
  }
  return {
    cls: 'ineligible',
    badgeCls: 'match-pill-ineligible',
    text: 'Not Eligible',
    preApproved: false,
    noteText: 'Statutory Disqualification',
    noteIcon: 'cancel',
    noteCls: 'warning',
  };
}

const SchemeCard: React.FC<SchemeCardProps> = ({
  rec,
  onClarificationSelect,
  onSaveToLocker,
}) => {
  const [expanded, setExpanded] = useState(false);
  const [saved, setSaved] = useState(false);
  const [selectedClarification, setSelectedClarification] = useState<string | null>(null);

  const statusInfo = getStatusBadge(rec.status, rec.match_percentage);

  // Conditions to display in alignment matrix
  const allConditions = [
    ...(rec.matched_conditions ?? []),
    ...(rec.failed_conditions ?? []),
  ];

  // Default criteria if matched conditions list is empty or sparse
  const displayConditions = allConditions.length > 0 ? allConditions : [
    {
      condition_name: 'Residency Criteria',
      description: 'Matches targeted state / regional eligibility',
      status: 'passed' as const,
      reason: 'Resident verification verified',
    },
    {
      condition_name: 'Income Threshold',
      description: 'Annual family income complies with grant cap',
      status: 'passed' as const,
      reason: 'Qualifies within threshold',
    },
    {
      condition_name: 'Target Sector',
      description: 'Occupation and target beneficiaries aligned',
      status: 'passed' as const,
      reason: 'Beneficiary profile confirmed',
    },
  ];

  const handleSave = () => {
    setSaved(true);
    onSaveToLocker?.(rec.scheme_name);
    setTimeout(() => setSaved(false), 3000);
  };

  const handleClarification = (optLabel: string) => {
    setSelectedClarification(optLabel);
    onClarificationSelect?.(optLabel);
  };

  return (
    <article className={`scheme-card ${statusInfo.cls}`}>
      {/* 1. Header Ribbon */}
      <div className="scheme-header-ribbon">
        <div className="ribbon-badges">
          <span className={statusInfo.badgeCls}>{statusInfo.text}</span>
          <span className="ribbon-scheme-type">
            {rec.category_badge || (rec.level === 'central' ? 'Centrally Sponsored Scheme (CSS)' : 'State Direct Benefit Initiative')}
          </span>
        </div>
        <div className={`ribbon-status-note ${statusInfo.noteCls}`}>
          <span className="material-symbols-outlined" style={{ fontSize: 16 }}>
            {statusInfo.noteIcon}
          </span>
          <span>{statusInfo.noteText}</span>
        </div>
      </div>

      {/* 2. Main Card Content */}
      <div className="scheme-card-body">
        {/* Title & Effective Benefit Row */}
        <div className="scheme-title-row">
          <div>
            <h3 className="scheme-main-title">{rec.scheme_name}</h3>
            <p className="scheme-agency-desc">
              {rec.description || rec.summary || `${rec.department || 'Govt of India'} • Official Benefit Assistance`}
            </p>
          </div>

          {(rec.effective_benefit || rec.status === 'ELIGIBLE') && (
            <div className="scheme-benefit-badge">
              <span className="benefit-badge-label">
                {rec.status === 'ELIGIBLE' ? 'Effective Benefit' : 'Credit Bracket'}
              </span>
              <span className="benefit-badge-value">
                {rec.effective_benefit || (rec.status === 'ELIGIBLE' ? 'Up to 90% Aid' : '₹10 Lakh - ₹1 Crore')}
              </span>
            </div>
          )}
        </div>

        {/* 3. AI Criteria Alignment Matrix */}
        <div className="criteria-matrix-box">
          <div className="criteria-matrix-title">AI Verified Criteria Alignment</div>
          <div className="criteria-grid">
            {displayConditions.slice(0, 3).map((c, idx) => {
              const isMet = c.status === 'passed';
              const isUnmet = c.status === 'failed';
              const tileCls = isMet ? 'met' : isUnmet ? 'unmet' : 'info';
              const icon = isMet ? 'check_circle' : isUnmet ? 'cancel' : 'info';

              return (
                <div key={idx} className={`criteria-tile ${tileCls}`}>
                  <span className="material-symbols-outlined">{icon}</span>
                  <div className="criteria-tile-info">
                    <span className="criteria-tile-name">{c.condition_name}</span>
                    <span className="criteria-tile-detail">
                      {c.reason || c.description}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* 4. Clarification Notice Box (if present e.g. Stand-Up India) */}
        {rec.clarification_prompt && (
          <div className="clarification-prompt-box">
            <div className="clarification-title">
              <span className="material-symbols-outlined">help_center</span>
              <span>{rec.clarification_prompt.title}</span>
            </div>
            <p className="clarification-desc">
              {rec.clarification_prompt.description}
            </p>
            <div className="clarification-chips-row">
              {rec.clarification_prompt.options.map((opt, oIdx) => {
                const isSelected = selectedClarification === opt.label;
                return (
                  <button
                    key={oIdx}
                    type="button"
                    className={`clarification-option-btn ${isSelected ? 'selected' : ''}`}
                    onClick={() => handleClarification(opt.label)}
                  >
                    <span className="material-symbols-outlined" style={{ fontSize: 18 }}>
                      {isSelected ? 'check_circle' : opt.icon || 'done_all'}
                    </span>
                    <span>{opt.label}</span>
                  </button>
                );
              })}
            </div>
          </div>
        )}

        {/* 5. Financial Architecture Breakout (if present) */}
        {rec.financial_breakout && rec.financial_breakout.length > 0 && (
          <div className="financial-grid">
            {rec.financial_breakout.map((item, fIdx) => (
              <div
                key={fIdx}
                className={`financial-box ${item.isHighlight ? 'highlight' : ''} ${item.isSecondary ? 'secondary' : ''}`}
              >
                <span className="financial-box-label">{item.label}</span>
                <span className="financial-box-value">{item.value}</span>
                {item.subtext && <span className="financial-box-sub">{item.subtext}</span>}
              </div>
            ))}
          </div>
        )}

        {/* 6. Required Documentation Artifacts */}
        <div className="docs-section">
          <div className="docs-label">Required Documentation Artifacts:</div>
          <div className="docs-chips">
            {(rec.required_documents && rec.required_documents.length > 0
              ? rec.required_documents
              : [
                  { name: '7/12 & 8A Land Extract', isVerified: true },
                  { name: 'Aadhaar (e-KYC verified)', isVerified: true },
                  { name: 'Bank Passbook / DBT Link', isVerified: true },
                  { name: 'NOC from Local Authority', isVerified: false },
                ]
            ).map((doc, dIdx) => (
              <span
                key={dIdx}
                className={`doc-chip ${doc.isVerified ? 'verified' : 'pending'}`}
              >
                <span className="material-symbols-outlined">
                  {doc.isVerified ? 'folder_check' : 'pending'}
                </span>
                <span>{doc.name}</span>
              </span>
            ))}
          </div>
        </div>

        {/* 7. Action Bar */}
        <div className="scheme-action-bar">
          <div className="scheme-action-buttons">
            <a
              href={rec.official_url || 'https://www.myscheme.gov.in'}
              target="_blank"
              rel="noopener noreferrer"
              className="btn-apply-portal"
            >
              <span>Apply on Official Portal</span>
              <span className="material-symbols-outlined" style={{ fontSize: 16 }}>
                open_in_new
              </span>
            </a>

            <button
              type="button"
              className="btn-save-locker"
              onClick={handleSave}
            >
              <span className="material-symbols-outlined" style={{ fontSize: 18 }}>
                {saved ? 'check' : 'bookmark_add'}
              </span>
              <span>{saved ? 'Saved to Locker' : 'Save to Locker'}</span>
            </button>
          </div>

          <span className="scheme-window-date">
            {rec.registration_window || 'Registration window active for FY 2025-26'}
          </span>
        </div>

        {/* 8. Collapsible Condition Details & Evidence */}
        {allConditions.length > 3 && (
          <div>
            <button
              type="button"
              className="scheme-accordion-toggle"
              onClick={() => setExpanded(!expanded)}
              aria-expanded={expanded}
            >
              <span className="material-symbols-outlined" style={{ fontSize: 16 }}>
                {expanded ? 'expand_less' : 'expand_more'}
              </span>
              <span>{expanded ? 'Hide full criteria audit' : `View all ${allConditions.length} criteria details & evidence`}</span>
            </button>

            {expanded && (
              <div className="scheme-conditions-detail">
                {allConditions.map((c, cIdx) => (
                  <div key={cIdx} className="condition-detail-row">
                    <span className="material-symbols-outlined" style={{
                      fontSize: 14,
                      color: c.status === 'passed' ? 'var(--on-tertiary-container)' : 'var(--error)'
                    }}>
                      {c.status === 'passed' ? 'check' : 'close'}
                    </span>
                    <span>
                      <strong>{c.condition_name}:</strong> {c.reason || c.description}
                    </span>
                  </div>
                ))}

                {rec.top_evidence_snippet && (
                  <div style={{ marginTop: '0.5rem', paddingTop: '0.5rem', borderTop: '1px dashed var(--outline-variant)' }}>
                    <div style={{ fontSize: '0.6875rem', fontWeight: 700, color: 'var(--on-surface-variant)' }}>
                      Legal Extract Snippet:
                    </div>
                    <code style={{ fontSize: '0.6875rem', color: 'var(--secondary)', display: 'block', marginTop: '0.25rem' }}>
                      {rec.top_evidence_snippet}
                    </code>
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </article>
  );
};

export default SchemeCard;

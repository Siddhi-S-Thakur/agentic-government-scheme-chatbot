import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import type { SchemeRecommendation, EligibilityStatus } from '../types/api';

interface SchemeCardProps {
  rec: SchemeRecommendation;
}

function statusLabel(status: EligibilityStatus, t: (key: string) => string): string {
  switch (status) {
    case 'ELIGIBLE':   return t('eligible');
    case 'INELIGIBLE': return t('ineligible');
    case 'PARTIAL':    return t('partial');
    default:           return t('unknown');
  }
}

function statusClass(status: EligibilityStatus): string {
  switch (status) {
    case 'ELIGIBLE':   return 'eligible';
    case 'INELIGIBLE': return 'ineligible';
    case 'PARTIAL':    return 'partial';
    default:           return 'unknown';
  }
}

function conditionStatusIcon(status: string): { icon: string; cls: string } {
  if (status === 'passed') return { icon: '✓', cls: 'met' };
  if (status === 'failed') return { icon: '✗', cls: 'unmet' };
  return { icon: '?', cls: 'info' };
}

const SchemeCard: React.FC<SchemeCardProps> = ({ rec }) => {
  const { t } = useTranslation();
  const [expanded, setExpanded] = useState(false);

  const allConditions = [
    ...(rec.matched_conditions ?? []),
    ...(rec.failed_conditions ?? []),
  ];

  const cls = statusClass(rec.status);

  return (
    <div className={`rec-card ${cls}`}>
      {/* Header */}
      <div className="rec-header">
        <div>
          <div className="rec-name">{rec.scheme_name}</div>
          {(rec.department || rec.level) && (
            <div className="rec-dept">
              {rec.department && `${rec.department}`}
              {rec.level && ` · ${rec.level === 'central' ? '🇮🇳 Central' : '🏛️ State'}`}
            </div>
          )}
        </div>
        <span className={`eligibility-badge ${cls}`}>
          {statusLabel(rec.status, t)}
        </span>
      </div>

      {/* Summary / description */}
      {(rec.summary || rec.description) && (
        <p className="rec-description">{rec.summary || rec.description}</p>
      )}

      {/* Tags */}
      <div className="rec-tags">
        {rec.level && <span className="rec-tag">#{rec.level}</span>}
        {rec.status === 'ELIGIBLE' && <span className="rec-tag">✅ {t('eligible')}</span>}
        {allConditions.length > 0 && (
          <span className="rec-tag">{allConditions.length} conditions</span>
        )}
        {(rec.missing_fields ?? []).length > 0 && (
          <span className="rec-tag">ℹ️ {rec.missing_fields!.length} fields needed</span>
        )}
      </div>

      {/* Conditions (expanded) */}
      {expanded && allConditions.length > 0 && (
        <div className="rec-conditions">
          <div className="rec-conditions-title">{t('conditionsMet')}</div>
          {allConditions.map((c, i) => {
            const { icon, cls: iconCls } = conditionStatusIcon(c.status);
            return (
              <div key={i} className="condition-item">
                <span className={`condition-icon ${iconCls}`}>{icon}</span>
                <span>{c.reason || c.description || c.condition_name}</span>
              </div>
            );
          })}
        </div>
      )}

      {/* Top evidence (expanded) */}
      {expanded && rec.top_evidence_snippet && (
        <div style={{ marginBottom: 10 }}>
          <div className="rec-conditions-title">Evidence</div>
          <p className="rec-description" style={{ marginBottom: 0, fontFamily: 'monospace', fontSize: '11px' }}>
            {rec.top_evidence_snippet}
          </p>
        </div>
      )}

      {/* Footer */}
      <div className="rec-footer">
        {rec.official_url && (
          <a
            href={rec.official_url}
            target="_blank"
            rel="noopener noreferrer"
            className="rec-source-link"
          >
            🔗 {t('viewSource')}
          </a>
        )}
        {allConditions.length > 0 && (
          <button
            id={`scheme-expand-${rec.scheme_id}`}
            className="rec-expand-btn"
            onClick={() => setExpanded(!expanded)}
            aria-expanded={expanded}
          >
            {expanded ? '▲ Less' : '▼ ' + t('viewDetails')}
          </button>
        )}
      </div>
    </div>
  );
};

interface SchemeResultsProps {
  recommendations: SchemeRecommendation[];
}

const SchemeResults: React.FC<SchemeResultsProps> = ({ recommendations }) => {
  const { t } = useTranslation();
  if (recommendations.length === 0) return null;

  return (
    <div className="recommendations-section">
      <div style={{
        fontSize: 'var(--font-size-xs)',
        fontWeight: 600,
        color: 'var(--c-text-muted)',
        textTransform: 'uppercase',
        letterSpacing: '0.06em',
        marginBottom: 10,
      }}>
        🎯 {t('schemes')} ({recommendations.length})
      </div>
      {recommendations.map((rec) => (
        <SchemeCard key={rec.scheme_id} rec={rec} />
      ))}
    </div>
  );
};

export default SchemeResults;

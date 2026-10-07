import React, { useState } from 'react';
import type { SchemeRecommendation } from '../../types/api';
import SchemeCard from '../SchemeCard';

interface RecommendationsViewProps {
  recommendations: SchemeRecommendation[];
  onSaveToLocker: (schemeName: string) => void;
  onClarificationSelect: (value: string) => void;
  onNavigateToChat: (query?: string) => void;
}

const RecommendationsView: React.FC<RecommendationsViewProps> = ({
  recommendations,
  onSaveToLocker,
  onClarificationSelect,
  onNavigateToChat,
}) => {
  const [filter, setFilter] = useState<'all' | 'eligible' | 'provisional' | 'ineligible'>('all');
  const [searchQuery, setSearchQuery] = useState('');

  const filtered = recommendations.filter((r) => {
    if (filter === 'eligible' && r.status !== 'ELIGIBLE') return false;
    if (filter === 'provisional' && r.status !== 'PARTIAL' && r.status !== 'UNKNOWN') return false;
    if (filter === 'ineligible' && r.status !== 'INELIGIBLE') return false;
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      return (
        r.scheme_name.toLowerCase().includes(q) ||
        (r.department && r.department.toLowerCase().includes(q)) ||
        (r.description && r.description.toLowerCase().includes(q))
      );
    }
    return true;
  });

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem', width: '100%' }}>
      {/* Header bar with filters and search */}
      <div className="provenance-strip" style={{ marginBottom: 0 }}>
        <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', gap: '0.5rem' }}>
          <button
            type="button"
            className={`font-btn ${filter === 'all' ? 'active' : ''}`}
            style={{ padding: '0.375rem 0.75rem', fontSize: '0.75rem' }}
            onClick={() => setFilter('all')}
          >
            All Recommended ({recommendations.length})
          </button>
          <button
            type="button"
            className={`font-btn ${filter === 'eligible' ? 'active' : ''}`}
            style={{ padding: '0.375rem 0.75rem', fontSize: '0.75rem' }}
            onClick={() => setFilter('eligible')}
          >
            Pre-Approved &amp; Eligible
          </button>
          <button
            type="button"
            className={`font-btn ${filter === 'provisional' ? 'active' : ''}`}
            style={{ padding: '0.375rem 0.75rem', fontSize: '0.75rem' }}
            onClick={() => setFilter('provisional')}
          >
            Clarification Needed
          </button>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <input
            type="text"
            className="chat-main-input"
            style={{ padding: '0.375rem 0.75rem', fontSize: '0.75rem', width: '220px' }}
            placeholder="Search schemes..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
          <button
            type="button"
            className="chat-send-btn"
            style={{ height: '32px', fontSize: '0.75rem', padding: '0 0.75rem' }}
            onClick={() => onNavigateToChat('Find more schemes for my profile')}
          >
            <span className="material-symbols-outlined" style={{ fontSize: 16 }}>
              auto_awesome
            </span>
            <span>Scan Vault</span>
          </button>
        </div>
      </div>

      {/* Recommendations Cards List */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        {filtered.length === 0 ? (
          <div className="scheme-card" style={{ padding: '2rem', textAlign: 'center' }}>
            <span className="material-symbols-outlined" style={{ fontSize: 40, color: 'var(--outline)' }}>
              manage_search
            </span>
            <p style={{ marginTop: '0.5rem', color: 'var(--on-surface-variant)' }}>
              No schemes match the selected filter. Try switching filters or search terms.
            </p>
          </div>
        ) : (
          filtered.map((rec) => (
            <div key={rec.scheme_id} style={{ width: '100%' }}>
              <SchemeCard
                rec={rec}
                onSaveToLocker={onSaveToLocker}
                onClarificationSelect={onClarificationSelect}
              />
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default RecommendationsView;

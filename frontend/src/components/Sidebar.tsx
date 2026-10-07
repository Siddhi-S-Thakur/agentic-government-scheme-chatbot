import React from 'react';
import { useTranslation } from 'react-i18next';

interface SidebarProps {
  activeTab?: string;
  onTabSelect?: (tab: string) => void;
  isOpen?: boolean;
  onClose?: () => void;
}

const Sidebar: React.FC<SidebarProps> = ({
  activeTab = 'agentic-caseworker',
  onTabSelect,
  isOpen = false,
  onClose,
}) => {
  const { t } = useTranslation();

  const NAV_ITEMS = [
    { id: 'citizen-dashboard', label: t('nav.dashboard', 'Citizen Dashboard'), icon: 'dashboard' },
    { id: 'ai-recommendations', label: t('nav.recommendations', 'AI Recommendations'), icon: 'auto_awesome' },
    { id: 'active-applications', label: t('nav.applications', 'Active Applications'), icon: 'task_alt' },
    { id: 'digilocker-dossier', label: t('nav.digilocker', 'DigiLocker Dossier'), icon: 'folder_managed' },
    { id: 'dbt-disbursements', label: t('nav.dbt', 'DBT Disbursements'), icon: 'account_balance_wallet' },
    { id: 'agentic-caseworker', label: t('nav.caseworker', 'Agentic Caseworker'), icon: 'smart_toy', defaultActive: true },
  ];

  return (
    <aside className={`gov-sidebar ${isOpen ? 'open' : ''}`}>
      {/* Brand Header */}
      <div className="gov-sidebar-brand">
        <div className="brand-title">{t('appName', 'GovScheme')}</div>
        <div className="brand-subtitle">{t('appSubtitle', 'Citizen Beneficiary Suite')}</div>
      </div>

      {/* Nav Menu */}
      <nav className="gov-nav" role="navigation" aria-label="Main menu">
        {NAV_ITEMS.map((item) => {
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              type="button"
              className={`gov-nav-item ${isActive ? 'active' : ''}`}
              onClick={() => {
                onTabSelect?.(item.id);
                onClose?.();
              }}
              aria-current={isActive ? 'page' : undefined}
            >
              <span className="material-symbols-outlined">{item.icon}</span>
              <span>{item.label}</span>
            </button>
          );
        })}
      </nav>

      {/* Footer Aadhaar / DBT status card */}
      <div className="gov-sidebar-footer">
        <div className="kyc-status-card">
          <div className="kyc-status-title">
            <span className="kyc-dot" />
            <span>Aadhaar KYC Linked</span>
          </div>
          <div className="kyc-status-desc">
            Direct Benefit Transfer (DBT) Ready
          </div>
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;

import React, { useRef, useEffect, useState, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import type {
  Message,
  Language,
  SessionState,
  UserProfile,
  SchemeRecommendation,
} from '../types/api';
import { sendChatMessage } from '../api/client';
import Sidebar from './Sidebar';
import Header from './Header';
import SchemeCard from './SchemeCard';
import ProfileDossier from './ProfileDossier';
import { HelpModal, VaultModal, DigiLockerModal, EditProfileModal } from './Modals';
import CitizenDashboardView from './views/CitizenDashboardView';
import RecommendationsView from './views/RecommendationsView';
import ActiveApplicationsView, { type SavedApplication } from './views/ActiveApplicationsView';
import DigiLockerView from './views/DigiLockerView';
import DbtDisbursementsView from './views/DbtDisbursementsView';

function genId() {
  return Math.random().toString(36).slice(2);
}

function formatTime(d: Date): string {
  return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

// Priya Sharma seed profile from screen.png / code.html
const INITIAL_PROFILE: UserProfile = {
  age: 28,
  gender: 'Female',
  occupation: 'Farmer / Agri-entrepreneur',
  state: 'Maharashtra',
  district: 'Nashik',
  annual_income: 240000,
};

// Default seed recommendations
const INITIAL_RECOMMENDATIONS: SchemeRecommendation[] = [
  {
    scheme_id: 'pm-kusum-b',
    scheme_name: 'PM-KUSUM Component-B',
    status: 'ELIGIBLE',
    match_percentage: 98,
    category_badge: 'Centrally Sponsored Scheme (CSS)',
    department:
      'Standalone Solar Agriculture Pump Subsidy Program • MNRE & Govt. of Maharashtra (Mahavitaran)',
    effective_benefit: 'Up to 90% Aid',
    matched_conditions: [
      {
        condition_name: 'Age & Residency',
        description: '28 yrs (Req: 18-60) in Nashik, MH',
        status: 'passed',
        reason: '28 yrs (Req: 18-60) in Nashik, MH',
      },
      {
        condition_name: 'Income Threshold',
        description: '₹2.4L qualifies under Small Farmer',
        status: 'passed',
        reason: '₹2.4L qualifies under Small Farmer',
      },
      {
        condition_name: 'Targeted Sector',
        description: 'Irrigation electrification',
        status: 'passed',
        reason: 'Irrigation electrification',
      },
    ],
    financial_breakout: [
      {
        label: 'Central + State Grant',
        value: '60% Outright Subsidy',
        subtext: '3HP to 7.5HP AC/DC Pumps',
      },
      {
        label: 'Soft Bank Loan (NABARD)',
        value: '30% Subsidized Credit',
        subtext: 'Priority Sector Lending rates',
        isSecondary: true,
      },
      {
        label: 'Direct Farmer Contribution',
        value: 'Only 10%',
        subtext: 'Payable upon work allotment',
        isHighlight: true,
      },
    ],
    required_documents: [
      { name: '7/12 & 8A Land Extract', isVerified: true },
      { name: 'Aadhaar (e-KYC verified)', isVerified: true },
      { name: 'Bank Passbook / DBT Link', isVerified: true },
      { name: 'NOC from Discom', isVerified: false },
    ],
    registration_window: 'Registration window open till 31 Oct 2025',
    official_url: 'https://kusum.online.gov.in',
  },
  {
    scheme_id: 'stand-up-india',
    scheme_name: 'Stand-Up India Scheme',
    status: 'PARTIAL',
    match_percentage: 75,
    category_badge: 'Scheduled Commercial Bank Direct Facility',
    department:
      'Promoting Entrepreneurship for Women & SC/ST Enterprises • Ministry of Finance & SIDBI',
    effective_benefit: '₹10 Lakh - ₹1 Crore',
    clarification_prompt: {
      title: 'Eligibility Checkpoint: Venture Classification',
      description:
        'Stand-Up India mandates that the enterprise must be a Greenfield project (first-time venture in manufacturing, services, agri-allied, or trading). Furthermore, woman entrepreneurs must hold at least 51% shareholding and controlling stake.',
      options: [
        {
          label: 'Yes, it is a first-time (Greenfield) venture',
          icon: 'done_all',
        },
        {
          label: 'No, existing business expansion',
          icon: 'domain_add',
        },
      ],
    },
    financial_breakout: [
      {
        label: 'Loan Type & Tenor',
        value: 'Composite Loan (Term Loan + Working Capital)',
        subtext: '7-year tenure with up to 18-month moratorium window.',
      },
      {
        label: 'Margin Money Coverage',
        value: 'Up to 15% with State Convergences',
        subtext: 'Can be paired with Maharashtra Women Industrial Policy benefits.',
      },
    ],
    official_url: 'https://www.standupmitra.in',
  },
];

const INITIAL_MESSAGES: Message[] = [
  {
    id: 'msg-seed-1',
    role: 'assistant',
    userName: 'GovScheme AI Specialist',
    timestamp: new Date(Date.now() - 120000),
    content:
      'Namaste Priya! I am your personalized GovScheme AI Assistant. Through your login session, I note your registered state as Maharashtra. To uncover customized grants and central subsidies, please share your profession, estimated household annual income, or key equipment needs (e.g., solar drip irrigation, SHG startup loans, rural housing).',
  },
  {
    id: 'msg-seed-2',
    role: 'user',
    userName: 'You (Priya Sharma)',
    userAvatar:
      'https://lh3.googleusercontent.com/aida-public/AB6AXuB22gqerMV4DS0BZlwnOcERZGC4WRVGhVXJhZkuahW5DADWlmjyi5ur1jkb3TRJNBGWCfRKCn5AenBu9jLXrUU8U-XfqsxdYCeYq3ZupSF0nqXVbZahbfwAaAWnHyw3QQ_tODtN4CVZ1gKcbIqGEoPdi7sMNAF4draK0xKJq8GszO3F_2ChViHfXxPA0zxtCEO9HR33jmopzOypZnN8ePq_8-4GpWc77vuY6VZIJag',
    timestamp: new Date(Date.now() - 60000),
    content:
      'I am a 28-year-old female farmer and agri-entrepreneur based in Nashik, Maharashtra. Our total family income is roughly ₹2.4 Lakhs annually. I am urgently looking for government subsidies on solar irrigation pumps and accessible credit guarantees for agro-processing.',
  },
  {
    id: 'msg-seed-3',
    role: 'assistant',
    userName: 'GovScheme AI Specialist',
    timestamp: new Date(),
    syncNotice:
      'Extracted 5 key parameters and synced with your Citizen Profile panel.',
    content:
      'Cross-referenced against 148 Central & State schemes: Located 1 fully verified high-match grant, and 1 high-value loan opportunity requiring single clarification.',
    recommendations: INITIAL_RECOMMENDATIONS,
  },
];

const INITIAL_APPLICATIONS: SavedApplication[] = [
  {
    id: 'pm-kusum-b',
    schemeName: 'PM-KUSUM Component-B Solar Pump Subsidy',
    department: 'MNRE & Govt. of Maharashtra (Mahavitaran)',
    status: 'Drafted',
    benefit: 'Up to 90% Capital Subsidy',
    portalUrl: 'https://kusum.online.gov.in',
    savedDate: 'Today',
  },
  {
    id: 'stand-up-india',
    schemeName: 'Stand-Up India Scheme for Women Enterprises',
    department: 'Ministry of Finance & SIDBI',
    status: 'Docs Verified',
    benefit: '₹10 Lakh - ₹1 Crore Facility',
    portalUrl: 'https://www.standupmitra.in',
    savedDate: 'Yesterday',
  },
];

const QUICK_CHIPS = [
  'Lakhpati Didi details',
  'PMAY-G Housing Subsidy',
  'KCC Crop Loan',
  'PM Kisan 6000 status',
  'Solar Pump Subsidy MH',
];

const ChatInterface: React.FC = () => {
  const { t, i18n } = useTranslation();

  // ── Navigation & Views State ─────────────────────────────
  const [activeTab, setActiveTab] = useState<string>('agentic-caseworker');
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  // ── Core Conversational & Profile State ──────────────────
  const [messages, setMessages] = useState<Message[]>(INITIAL_MESSAGES);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [language, setLanguage] = useState<Language>('en');
  const [mcqMode, setMcqMode] = useState<boolean>(true);
  const [fontScale, setFontScale] = useState<number>(1);
  const [profile, setProfile] = useState<UserProfile>(INITIAL_PROFILE);
  const [sessionState, setSessionState] = useState<SessionState | undefined>(undefined);
  const [allRecommendations, setAllRecommendations] = useState<SchemeRecommendation[]>(INITIAL_RECOMMENDATIONS);
  const [savedApplications, setSavedApplications] = useState<SavedApplication[]>(INITIAL_APPLICATIONS);

  // ── UI Feedback & Toasts ─────────────────────────────────
  const [toastMessage, setToastMessage] = useState<string | null>(null);
  const [isListening, setIsListening] = useState(false);

  // ── Modals State ─────────────────────────────────────────
  const [isHelpOpen, setIsHelpOpen] = useState(false);
  const [isVaultOpen, setIsVaultOpen] = useState(false);
  const [isDigiLockerOpen, setIsDigiLockerOpen] = useState(false);
  const [isEditProfileOpen, setIsEditProfileOpen] = useState(false);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // ── Flash Toast Helper ───────────────────────────────────
  const showToast = useCallback((msg: string) => {
    setToastMessage(msg);
    setTimeout(() => {
      setToastMessage(null);
    }, 3000);
  }, []);

  // ── Dynamic Font Scaling ─────────────────────────────────
  useEffect(() => {
    document.documentElement.style.setProperty('--user-font-scale', String(fontScale));
  }, [fontScale]);

  // ── Auto-scroll Chat ─────────────────────────────────────
  useEffect(() => {
    if (activeTab === 'agentic-caseworker') {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, isLoading, activeTab]);

  // ── Language Switcher ────────────────────────────────────
  const handleLanguageChange = (lang: Language) => {
    setLanguage(lang);
    i18n.changeLanguage(lang);
    showToast(lang === 'hi' ? 'भाषा बदलकर हिंदी की गई' : lang === 'mr' ? 'भाषा बदलून मराठी केली' : 'Language set to English');
  };

  // ── Send Message to AI Agent (LangGraph) ──────────────────
  const sendMessage = useCallback(
    async (text: string) => {
      const trimmed = text.trim();
      if (!trimmed || isLoading) return;

      // Always switch to caseworker view when chatting
      setActiveTab('agentic-caseworker');

      const userMsg: Message = {
        id: genId(),
        role: 'user',
        userName: 'You (Priya Sharma)',
        userAvatar:
          'https://lh3.googleusercontent.com/aida-public/AB6AXuB22gqerMV4DS0BZlwnOcERZGC4WRVGhVXJhZkuahW5DADWlmjyi5ur1jkb3TRJNBGWCfRKCn5AenBu9jLXrUU8U-XfqsxdYCeYq3ZupSF0nqXVbZahbfwAaAWnHyw3QQ_tODtN4CVZ1gKcbIqGEoPdi7sMNAF4draK0xKJq8GszO3F_2ChViHfXxPA0zxtCEO9HR33jmopzOypZnN8ePq_8-4GpWc77vuY6VZIJag',
        content: trimmed,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, userMsg]);
      setInputText('');
      setIsLoading(true);

      // Package state so LangGraph orchestrator receives profile, language & MCQ preference
      const currentSessionState: SessionState = {
        messages: (sessionState?.messages || messages.map((m) => ({ role: m.role, content: m.content }))).concat([
          { role: 'user', content: trimmed },
        ]),
        profile: profile,
        detected_language: language,
        interaction_mode: mcqMode ? 'mcq' : 'text',
      };

      try {
        const response = await sendChatMessage({
          message: trimmed,
          session_state: currentSessionState,
        });

        if (response.session_state) {
          setSessionState(response.session_state);
        }
        if (response.profile) {
          setProfile((prev) => ({ ...prev, ...response.profile }));
        }
        if (response.detected_language) {
          setLanguage(response.detected_language);
        }

        // Process recommendations if returned
        const recs: SchemeRecommendation[] = (response.recommendations || []).map((r) => {
          return {
            ...r,
            match_percentage: r.status === 'ELIGIBLE' ? 95 : 75,
            category_badge: r.level === 'central' ? 'Centrally Sponsored Scheme (CSS)' : 'State Direct Benefit Initiative',
            effective_benefit: r.status === 'ELIGIBLE' ? 'Direct Subsidy Assistance' : 'Financial Aid',
          };
        });

        if (recs.length > 0) {
          setAllRecommendations((prev) => {
            const combined = [...recs];
            for (const item of prev) {
              if (!combined.some((c) => c.scheme_id === item.scheme_id)) {
                combined.push(item);
              }
            }
            return combined;
          });
        }

        const assistantMsg: Message = {
          id: genId(),
          role: 'assistant',
          userName: 'GovScheme AI Specialist',
          content: response.response,
          timestamp: new Date(),
          mcq_options: response.mcq_options ?? undefined,
          recommendations: recs.length > 0 ? recs : undefined,
          syncNotice:
            response.needs_clarification
              ? undefined
              : 'Cross-referenced against National Digital Scheme Registry',
        };

        setMessages((prev) => [...prev, assistantMsg]);
      } catch (err: unknown) {
        const errMsg =
          err instanceof Error
            ? err.message
            : 'Unable to connect to AI Orchestrator service. Please try again.';

        const fallbackMsg: Message = {
          id: genId(),
          role: 'assistant',
          userName: 'GovScheme AI Specialist',
          content: `⚠️ ${errMsg}`,
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, fallbackMsg]);
      } finally {
        setIsLoading(false);
        inputRef.current?.focus();
      }
    },
    [isLoading, sessionState, messages, profile, language, mcqMode]
  );

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    sendMessage(inputText);
  };

  // ── Reset Session ─────────────────────────────────────────
  const handleResetSession = () => {
    if (window.confirm('Do you want to reset current scheme analysis conversation?')) {
      setMessages([
        {
          id: 'welcome-reset',
          role: 'assistant',
          userName: 'GovScheme AI Specialist',
          timestamp: new Date(),
          content:
            'Session conversation context refreshed. Your Aadhaar profile remains secure. How can I assist you with government schemes today?',
        },
      ]);
      setSessionState(undefined);
      setInputText('');
      showToast('Conversation session reset');
      inputRef.current?.focus();
    }
  };

  // ── Download PDF Dossier ──────────────────────────────────
  const handleDownloadPdf = () => {
    showToast('Compiling Official Dossier PDF...');
    setTimeout(() => {
      window.print();
    }, 700);
  };

  // ── Voice Input using Web Speech API ───────────────────────
  const handleVoiceInput = () => {
    const SpeechRecognition =
      (window as unknown as { SpeechRecognition?: unknown; webkitSpeechRecognition?: unknown }).SpeechRecognition ||
      (window as unknown as { webkitSpeechRecognition?: unknown }).webkitSpeechRecognition;

    if (SpeechRecognition) {
      try {
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        const recognition = new (SpeechRecognition as any)();
        recognition.lang = language === 'hi' ? 'hi-IN' : language === 'mr' ? 'mr-IN' : 'en-IN';
        setIsListening(true);
        showToast('Listening in regional language... Speak now');

        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        recognition.onresult = (event: any) => {
          setIsListening(false);
          const transcript = event.results[0][0].transcript;
          setInputText(transcript);
          sendMessage(transcript);
        };

        recognition.onerror = () => {
          setIsListening(false);
          showToast('Voice input stopped');
        };

        recognition.onend = () => {
          setIsListening(false);
        };

        recognition.start();
      } catch {
        setIsListening(false);
        setInputText('Am I eligible for solar pump subsidy in Maharashtra?');
        inputRef.current?.focus();
      }
    } else {
      setInputText('Am I eligible for solar pump subsidy in Maharashtra?');
      inputRef.current?.focus();
      showToast('Speech recognition not supported in this browser. Pre-filled query.');
    }
  };

  // ── Save to Locker Action ─────────────────────────────────
  const handleSaveToLocker = (schemeName: string) => {
    const existing = savedApplications.find((a) => a.schemeName.toLowerCase() === schemeName.toLowerCase());
    if (!existing) {
      const newApp: SavedApplication = {
        id: genId(),
        schemeName: schemeName,
        department: 'Government Welfare Division',
        status: 'Drafted',
        benefit: 'Grant Subsidy Verified',
        portalUrl: 'https://www.myscheme.gov.in',
        savedDate: 'Just now',
      };
      setSavedApplications((prev) => [newApp, ...prev]);
    }
    showToast(`✓ Saved "${schemeName}" to Active Applications Locker`);
  };

  // ── Remove from Locker ────────────────────────────────────
  const handleRemoveApplication = (id: string) => {
    setSavedApplications((prev) => prev.filter((a) => a.id !== id));
    showToast('Removed scheme from Locker');
  };

  // ── Attach DigiLocker Document ────────────────────────────
  const handleAttachDocument = (docTitle: string, dataAttrs?: Record<string, unknown>) => {
    if (dataAttrs) {
      setProfile((prev) => ({ ...prev, ...dataAttrs }));
    }
    showToast(`Attached ${docTitle} to AI Session`);
    sendMessage(
      `I have attached my verified DigiLocker document: ${docTitle}. Please check my eligibility based on this verified data.`
    );
  };

  // ── Save Profile from Inline Editor ───────────────────────
  const handleSaveProfile = (updated: UserProfile) => {
    setProfile(updated);
    showToast('Citizen profile updated and verified');
    sendMessage(
      `I have updated my profile details: Age ${updated.age ?? '28'}, Annual Income ₹${updated.annual_income ?? '240000'}, Landholding ${updated.landholding_acres ?? '2.5'} Acres in ${updated.state ?? 'Maharashtra'}. Please re-evaluate my eligible schemes.`
    );
  };

  return (
    <div className="app-container">
      {/* ── Left Sidebar Navigation ───────────────────────── */}
      <Sidebar
        activeTab={activeTab}
        onTabSelect={(tab) => {
          setActiveTab(tab);
          setIsSidebarOpen(false);
        }}
        isOpen={isSidebarOpen}
        onClose={() => setIsSidebarOpen(false)}
      />

      {/* ── Main Content Area ─────────────────────────────── */}
      <div className="gov-main-wrapper">
        {/* Top Header */}
        <Header
          currentLang={language}
          onLanguageChange={handleLanguageChange}
          fontScale={fontScale}
          onFontScaleChange={setFontScale}
          onOpenHelpline={() => setIsHelpOpen(true)}
          onToggleSidebar={() => setIsSidebarOpen(!isSidebarOpen)}
          onOpenDashboard={() => setActiveTab('citizen-dashboard')}
        />

        {/* Main Canvas */}
        <main className="gov-main-content">
          <div className="canvas-root">
            {/* Top Context & Provenance Strip */}
            <div className="provenance-strip">
              <div className="strip-status">
                <div className="ping-indicator">
                  <span className="ping-pulse" />
                  <span className="ping-dot" />
                </div>
                <span className="strip-title">{t('appName', 'AI Scheme Orchestrator')}</span>
                <span className="strip-dot">•</span>
                <span className="strip-desc">{t('header.engineVersion', 'Engine v3.2 (Aadhaar & Jan Samarth Verified Registry)')}</span>
                <span className="strip-badge">{t('header.liveContext', 'Live Context Engine')}</span>
              </div>

              <div className="strip-actions">
                <button
                  type="button"
                  className="strip-btn"
                  onClick={handleDownloadPdf}
                  title="Download Scheme Evaluation Dossier"
                >
                  <span className="material-symbols-outlined" style={{ fontSize: 16 }}>
                    picture_as_pdf
                  </span>
                  <span>{toastMessage || t('header.downloadPdf', 'Download PDF Dossier')}</span>
                </button>

                <button
                  type="button"
                  className="strip-btn reset"
                  onClick={handleResetSession}
                  title="Clear conversation and reset session"
                >
                  <span className="material-symbols-outlined" style={{ fontSize: 16 }}>
                    restart_alt
                  </span>
                  <span>{t('header.resetSession', 'Reset Session')}</span>
                </button>
              </div>
            </div>

            {/* View Switcher based on Active Tab */}
            {activeTab === 'citizen-dashboard' && (
              <CitizenDashboardView
                profile={profile}
                onNavigateToChat={(q) => {
                  setActiveTab('agentic-caseworker');
                  if (q) sendMessage(q);
                }}
                onOpenDigiLocker={() => setIsDigiLockerOpen(true)}
                onOpenEditProfile={() => setIsEditProfileOpen(true)}
              />
            )}

            {activeTab === 'ai-recommendations' && (
              <RecommendationsView
                recommendations={allRecommendations}
                onSaveToLocker={handleSaveToLocker}
                onClarificationSelect={(opt) => sendMessage(opt)}
                onNavigateToChat={(q) => {
                  setActiveTab('agentic-caseworker');
                  if (q) sendMessage(q);
                }}
              />
            )}

            {activeTab === 'active-applications' && (
              <ActiveApplicationsView
                applications={savedApplications}
                onRemoveApplication={handleRemoveApplication}
                onNavigateToChat={(q) => {
                  setActiveTab('agentic-caseworker');
                  if (q) sendMessage(q);
                }}
              />
            )}

            {activeTab === 'digilocker-dossier' && (
              <DigiLockerView
                onAttachDocument={handleAttachDocument}
                onNavigateToChat={() => setActiveTab('agentic-caseworker')}
              />
            )}

            {activeTab === 'dbt-disbursements' && <DbtDisbursementsView />}

            {activeTab === 'agentic-caseworker' && (
              /* Split Architecture: Left 70% Chat / Right 30% Profile Dossier */
              <div className="workspace-grid">
                {/* ==================================================== */}
                {/* LEFT COLUMN: CHAT STREAM & INPUT CONSOLE             */}
                {/* ==================================================== */}
                <section className="chat-column">
                  {/* Chat Stream Vessel */}
                  <div className="chat-stream-vessel" role="log" aria-live="polite">
                    {messages.map((msg) => {
                      const isUser = msg.role === 'user';

                      return (
                        <div key={msg.id} style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                          {/* Chat Message Row */}
                          <div className={`chat-message-row ${isUser ? 'user' : 'agent'}`}>
                            {/* Agent Avatar */}
                            {!isUser && (
                              <div className="message-avatar-agent">
                                <span className="material-symbols-outlined">smart_toy</span>
                              </div>
                            )}

                            {/* Message Body & Header */}
                            <div className="message-bubble-wrap">
                              <div className="message-meta">
                                <span className="message-sender">
                                  {isUser ? 'You (Priya Sharma)' : 'GovScheme AI Specialist'}
                                </span>
                                <span className="message-time">{formatTime(msg.timestamp)}</span>
                              </div>

                              {/* Bubble Content */}
                              <div className={isUser ? 'bubble-content-user' : 'bubble-content-agent'}>
                                {msg.syncNotice && (
                                  <div className="sync-verified-pill">
                                    <span className="material-symbols-outlined" style={{ fontSize: 18 }}>
                                      verified
                                    </span>
                                    <span>{msg.syncNotice}</span>
                                  </div>
                                )}
                                <div>{msg.content}</div>

                                {/* MCQ Options if returned by backend */}
                                {msg.mcq_options && msg.mcq_options.length > 0 && (
                                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', marginTop: '0.75rem' }}>
                                    {msg.mcq_options.map((opt, oIdx) => (
                                      <button
                                        key={oIdx}
                                        type="button"
                                        className="clarification-option-btn"
                                        onClick={() => sendMessage(opt.label)}
                                      >
                                        <span className="material-symbols-outlined" style={{ fontSize: 16 }}>
                                          check_circle
                                        </span>
                                        <span>{opt.label}</span>
                                      </button>
                                    ))}
                                  </div>
                                )}
                              </div>
                            </div>

                            {/* User Avatar */}
                            {isUser && (
                              <div className="message-avatar-user">
                                <img
                                  src={msg.userAvatar || 'https://lh3.googleusercontent.com/aida-public/AB6AXuB22gqerMV4DS0BZlwnOcERZGC4WRVGhVXJhZkuahW5DADWlmjyi5ur1jkb3TRJNBGWCfRKCn5AenBu9jLXrUU8U-XfqsxdYCeYq3ZupSF0nqXVbZahbfwAaAWnHyw3QQ_tODtN4CVZ1gKcbIqGEoPdi7sMNAF4draK0xKJq8GszO3F_2ChViHfXxPA0zxtCEO9HR33jmopzOypZnN8ePq_8-4GpWc77vuY6VZIJag'}
                                  alt="User Profile"
                                />
                              </div>
                            )}
                          </div>

                          {/* Rich Scheme Cards (nested inside flow matching screen.png) */}
                          {msg.recommendations && msg.recommendations.length > 0 && (
                            <div className="scheme-card-wrapper">
                              {msg.recommendations.map((rec) => (
                                <SchemeCard
                                  key={rec.scheme_id}
                                  rec={rec}
                                  onClarificationSelect={(choice) => sendMessage(choice)}
                                  onSaveToLocker={handleSaveToLocker}
                                />
                              ))}
                            </div>
                          )}
                        </div>
                      );
                    })}

                    {/* Active Deliberation / Reasoning State */}
                    {isLoading && (
                      <div className="reasoning-box">
                        <div className="message-avatar-agent">
                          <span className="material-symbols-outlined" style={{ animation: 'spin 1.5s linear infinite' }}>
                            sync
                          </span>
                        </div>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
                          <div className="message-meta">
                            <span className="message-sender">GovScheme AI Specialist</span>
                            <span style={{ fontSize: '0.6875rem', color: 'var(--on-tertiary-container)', fontWeight: 700 }}>
                              {t('chat.synthesizing', 'Synthesizing Maharashtra DBT DB...')}
                            </span>
                          </div>
                          <div className="reasoning-pill-content">
                            <div className="reasoning-dots">
                              <span className="bounce-dot" />
                              <span className="bounce-dot" />
                              <span className="bounce-dot" />
                            </div>
                            <span className="reasoning-text">
                              {t('chat.scanning', 'Scanning Dr. Babasaheb Ambedkar Krushi Swavalamban Yojana & MahaDBT Horticulture grants...')}
                            </span>
                          </div>
                        </div>
                      </div>
                    )}

                    <div ref={messagesEndRef} />
                  </div>

                  {/* Sticky Chat Input Controls Console */}
                  <div className="chat-input-console">
                    {/* Mode Bar: Guided MCQ & Suggestion Chips */}
                    <div className="console-mode-row">
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                        <label className="mcq-switch-label" title="Toggle guided 4-step eligibility validator">
                          <input
                            type="checkbox"
                            style={{ display: 'none' }}
                            checked={mcqMode}
                            onChange={(e) => {
                              setMcqMode(e.target.checked);
                              showToast(e.target.checked ? 'Guided MCQ Mode Enabled' : 'Text Interaction Mode Enabled');
                            }}
                          />
                          <div className={`mcq-switch-container ${mcqMode ? 'active' : ''}`}>
                            <div className="mcq-switch-knob" />
                          </div>
                          <span className="mcq-switch-text">{t('chat.mcqMode', 'Guided MCQ Mode')}</span>
                        </label>

                        <span className="mcq-validator-badge">
                          <span className="material-symbols-outlined">bolt</span>
                          <span>{t('chat.mcqSubtitle', 'Rapid 4-step eligibility validator')}</span>
                        </span>
                      </div>

                      {/* Quick Suggestion Chips */}
                      <div className="suggestion-chips-scroll">
                        {QUICK_CHIPS.map((chip, idx) => (
                          <button
                            key={idx}
                            type="button"
                            className="quick-suggestion-chip"
                            onClick={() => {
                              setInputText(chip);
                              sendMessage(chip);
                            }}
                          >
                            {chip}
                          </button>
                        ))}
                      </div>
                    </div>

                    {/* Main Input Field Form */}
                    <form className="chat-input-form" onSubmit={handleSubmit}>
                      <div className="chat-input-field-wrap">
                        <input
                          ref={inputRef}
                          type="text"
                          className="chat-main-input"
                          placeholder={t('chat.inputPlaceholder', "Ask in English, हिंदी, or मराठी... e.g., 'Am I eligible for Lakhpati Didi scheme?'")}
                          value={inputText}
                          onChange={(e) => setInputText(e.target.value)}
                          disabled={isLoading}
                          aria-label="Ask about government schemes"
                        />
                        <div className="chat-input-addons">
                          <button
                            type="button"
                            className="addon-icon-btn"
                            title="Attach Document from DigiLocker"
                            onClick={() => setIsDigiLockerOpen(true)}
                            aria-label="Attach Document"
                          >
                            <span className="material-symbols-outlined" style={{ fontSize: 19 }}>
                              attachment
                            </span>
                          </button>
                          <button
                            type="button"
                            className="addon-icon-btn"
                            title="Voice Query in Regional Languages"
                            onClick={handleVoiceInput}
                            aria-label="Voice Query"
                            style={{ color: isListening ? 'var(--on-tertiary-container)' : undefined }}
                          >
                            <span className="material-symbols-outlined" style={{ fontSize: 19 }}>
                              {isListening ? 'graphic_eq' : 'mic'}
                            </span>
                          </button>
                        </div>
                      </div>

                      <button
                        type="submit"
                        className="chat-send-btn"
                        disabled={isLoading || !inputText.trim()}
                        aria-label="Inquire"
                      >
                        <span>{t('chat.inquire', 'Inquire')}</span>
                        <span className="material-symbols-outlined" style={{ fontSize: 18 }}>
                          send
                        </span>
                      </button>
                    </form>

                    {/* Footnote */}
                    <div className="console-footnote">
                      <span className="footnote-security">
                        <span className="material-symbols-outlined">lock</span>
                        <span>{t('chat.encryptedFootnote', 'End-to-End Encrypted via Aadhaar Virtual ID')}</span>
                      </span>
                      <span>{t('chat.gazetteFootnote', 'Responses generated using verified government gazettes')}</span>
                    </div>
                  </div>
                </section>

                {/* ==================================================== */}
                {/* RIGHT COLUMN: CITIZEN PROFILE DOSSIER (STICKY)       */}
                {/* ==================================================== */}
                <ProfileDossier
                  profile={profile}
                  onRefresh={() => showToast('Profile synced with Aadhaar Registry')}
                  onPromptAttribute={() => setIsEditProfileOpen(true)}
                  onOpenVaultModal={() => setIsVaultOpen(true)}
                  onOpenEditProfile={() => setIsEditProfileOpen(true)}
                  eligibleCount={allRecommendations.filter((r) => r.status === 'ELIGIBLE').length || 2}
                />
              </div>
            )}
          </div>
        </main>
      </div>

      {/* ── Dialog Modals ──────────────────────────────────── */}
      <HelpModal isOpen={isHelpOpen} onClose={() => setIsHelpOpen(false)} />

      <VaultModal
        isOpen={isVaultOpen}
        onClose={() => setIsVaultOpen(false)}
        onSelectSchemeForInquiry={(query) => {
          setActiveTab('agentic-caseworker');
          sendMessage(query);
        }}
      />

      <DigiLockerModal
        isOpen={isDigiLockerOpen}
        onClose={() => setIsDigiLockerOpen(false)}
        onAttachDocument={handleAttachDocument}
      />

      <EditProfileModal
        isOpen={isEditProfileOpen}
        onClose={() => setIsEditProfileOpen(false)}
        profile={profile}
        onSaveProfile={handleSaveProfile}
      />
    </div>
  );
};

export default ChatInterface;

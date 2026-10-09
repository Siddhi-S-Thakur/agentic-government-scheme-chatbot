import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import type { Language } from '../types/api';

type AuthMode = 'login' | 'register';

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const INDIAN_STATES = [
  'Maharashtra',
  'Uttar Pradesh',
  'Bihar',
  'Madhya Pradesh',
  'Rajasthan',
  'Gujarat',
  'Karnataka',
  'Tamil Nadu',
  'Andhra Pradesh',
  'Telangana',
  'West Bengal',
  'Kerala',
  'Punjab',
  'Haryana',
  'Odisha',
  'Assam',
  'Delhi',
  'Other / Central',
];

const OCCUPATIONS = [
  'Farmer / Agricultural',
  'Student / Youth',
  'Small Business Owner / Self-Employed',
  'Daily Wage Worker / Laborer',
  'Homemaker',
  'Salaried Employee',
  'Senior Citizen / Pensioner',
  'Unemployed',
  'Other',
];

const SOCIAL_CATEGORIES = ['General', 'OBC', 'SC', 'ST', 'EWS'];

const AuthModal: React.FC<AuthModalProps> = ({ isOpen, onClose }) => {
  const { login, register, error, clearError, isLoading, user } = useAuth();
  const [mode, setMode] = useState<AuthMode>('login');

  // Account credentials
  const [username, setUsername] = useState('');
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');

  // Citizen Profile & Eligibility attributes (for registration)
  const [age, setAge] = useState<string>('');
  const [gender, setGender] = useState<string>('');
  const [occupation, setOccupation] = useState<string>('');
  const [state, setState] = useState<string>('Maharashtra');
  const [district, setDistrict] = useState<string>('');
  const [annualIncome, setAnnualIncome] = useState<string>('');
  const [casteCategory, setCasteCategory] = useState<string>('');
  const [landholding, setLandholding] = useState<string>('');
  const [preferredLang, setPreferredLang] = useState<Language>('en');

  const [localError, setLocalError] = useState<string | null>(null);

  // Auto-close modal when user successfully logs in
  useEffect(() => {
    if (user && isOpen) {
      onClose();
    }
  }, [user, isOpen, onClose]);

  const switchMode = (newMode: AuthMode) => {
    setMode(newMode);
    clearError();
    setLocalError(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLocalError(null);

    if (mode === 'register') {
      if (!username.trim() || !fullName.trim() || !password.trim()) {
        setLocalError('Username, full name, and password are required.');
        return;
      }
      if (password.length < 6) {
        setLocalError('Password must be at least 6 characters.');
        return;
      }
      if (password !== confirmPassword) {
        setLocalError('Passwords do not match.');
        return;
      }

      try {
        await register({
          username: username.trim(),
          fullName: fullName.trim(),
          password,
          email: email.trim() || undefined,
          age: age ? Number(age) : undefined,
          gender: gender || undefined,
          occupation: occupation || undefined,
          state: state || undefined,
          district: district.trim() || undefined,
          annual_income: annualIncome ? Number(annualIncome) : undefined,
          caste_category: casteCategory || undefined,
          landholding_acres: landholding ? Number(landholding) : undefined,
          preferred_language: preferredLang,
        });
      } catch {
        // Error captured in auth context
      }
    } else {
      if (!username.trim() || !password.trim()) {
        setLocalError('Username/email and password are required.');
        return;
      }
      try {
        await login(username.trim(), password);
      } catch {
        // Error captured in auth context
      }
    }
  };

  if (!isOpen) return null;

  const displayError = localError || error;

  return (
    <div className="auth-modal-overlay" onClick={onClose}>
      <div
        className="auth-modal-content"
        onClick={(e) => e.stopPropagation()}
        style={{ maxWidth: mode === 'register' ? '640px' : '480px' }}
      >
        {/* Close Button */}
        <button
          type="button"
          className="auth-modal-close-btn"
          onClick={onClose}
          aria-label="Close"
        >
          <span className="material-symbols-outlined">close</span>
        </button>

        {/* Modal Header with Branding */}
        <div className="auth-modal-header">
          <div className="auth-brand-icon" style={{ width: 40, height: 40, fontSize: 20 }}>
            <span className="material-symbols-outlined" style={{ fontSize: 22 }}>assured_workload</span>
          </div>
          <h2 className="auth-form-title" style={{ margin: 0 }}>
            {mode === 'login' ? 'Sign In to GovScheme AI' : 'Create Your Account'}
          </h2>
          <p className="auth-form-desc" style={{ margin: '0.25rem 0 0' }}>
            {mode === 'login'
              ? 'Sign in to save your chat history and profile across sessions.'
              : 'Register to persist your conversations and eligibility profile.'}
          </p>
        </div>

        {/* Tabs */}
        <div className="auth-tabs">
          <button
            type="button"
            className={`auth-tab ${mode === 'login' ? 'active' : ''}`}
            onClick={() => switchMode('login')}
          >
            <span className="material-symbols-outlined">login</span>
            <span>Sign In</span>
          </button>
          <button
            type="button"
            className={`auth-tab ${mode === 'register' ? 'active' : ''}`}
            onClick={() => switchMode('register')}
          >
            <span className="material-symbols-outlined">person_add</span>
            <span>Register</span>
          </button>
        </div>

        {/* Error Display */}
        {displayError && (
          <div className="auth-error-banner">
            <span className="material-symbols-outlined">error</span>
            <span>{displayError}</span>
            <button
              type="button"
              className="auth-error-dismiss"
              onClick={() => {
                setLocalError(null);
                clearError();
              }}
              aria-label="Dismiss error"
            >
              <span className="material-symbols-outlined">close</span>
            </button>
          </div>
        )}

        {/* Form */}
        <form className="auth-form" onSubmit={handleSubmit}>
          {mode === 'login' ? (
            /* ── Login Mode ── */
            <>
              <div className="auth-field">
                <label htmlFor="login-username" className="auth-label">
                  <span className="material-symbols-outlined">person</span>
                  Username or Email
                </label>
                <input
                  id="login-username"
                  type="text"
                  className="auth-input"
                  placeholder="e.g. rajesh_patil"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  autoComplete="username"
                  autoFocus
                />
              </div>

              <div className="auth-field">
                <label htmlFor="login-password" className="auth-label">
                  <span className="material-symbols-outlined">lock</span>
                  Password
                </label>
                <input
                  id="login-password"
                  type="password"
                  className="auth-input"
                  placeholder="Enter your password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  autoComplete="current-password"
                />
              </div>
            </>
          ) : (
            /* ── Register Mode ── */
            <>
              {/* Section 1: Account Credentials */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
                  <div className="auth-field">
                    <label htmlFor="reg-fullname" className="auth-label">
                      <span className="material-symbols-outlined">badge</span>
                      Full Name *
                    </label>
                    <input
                      id="reg-fullname"
                      type="text"
                      className="auth-input"
                      placeholder="e.g. Ramesh Patil"
                      value={fullName}
                      onChange={(e) => setFullName(e.target.value)}
                      autoComplete="name"
                      required
                    />
                  </div>

                  <div className="auth-field">
                    <label htmlFor="reg-username" className="auth-label">
                      <span className="material-symbols-outlined">person</span>
                      Username *
                    </label>
                    <input
                      id="reg-username"
                      type="text"
                      className="auth-input"
                      placeholder="e.g. ramesh_patil"
                      value={username}
                      onChange={(e) => setUsername(e.target.value)}
                      autoComplete="username"
                      required
                    />
                  </div>
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
                  <div className="auth-field">
                    <label htmlFor="reg-password" className="auth-label">
                      <span className="material-symbols-outlined">lock</span>
                      Password *
                    </label>
                    <input
                      id="reg-password"
                      type="password"
                      className="auth-input"
                      placeholder="Min 6 characters"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      autoComplete="new-password"
                      required
                    />
                  </div>

                  <div className="auth-field">
                    <label htmlFor="reg-conf-password" className="auth-label">
                      <span className="material-symbols-outlined">lock_reset</span>
                      Confirm Password *
                    </label>
                    <input
                      id="reg-conf-password"
                      type="password"
                      className="auth-input"
                      placeholder="Re-enter password"
                      value={confirmPassword}
                      onChange={(e) => setConfirmPassword(e.target.value)}
                      autoComplete="new-password"
                      required
                    />
                  </div>
                </div>

                <div className="auth-field">
                  <label htmlFor="reg-email" className="auth-label">
                    <span className="material-symbols-outlined">email</span>
                    Email Address
                    <span className="auth-optional-tag">(optional)</span>
                  </label>
                  <input
                    id="reg-email"
                    type="email"
                    className="auth-input"
                    placeholder="e.g. ramesh@example.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    autoComplete="email"
                  />
                </div>
              </div>

              {/* Section 2: Citizen Profile (Context for Schemes) */}
              <div
                style={{
                  borderTop: '1px solid var(--outline-variant)',
                  paddingTop: '0.875rem',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '0.75rem',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <span
                    style={{
                      fontSize: '0.75rem',
                      fontWeight: 700,
                      textTransform: 'uppercase',
                      letterSpacing: '0.05em',
                      color: 'var(--primary)',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '0.375rem',
                    }}
                  >
                    <span className="material-symbols-outlined" style={{ fontSize: 16, color: 'var(--secondary)' }}>
                      contact_page
                    </span>
                    Citizen Eligibility Details
                  </span>
                  <span className="auth-optional-tag">Used by AI to match schemes</span>
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
                  <div className="auth-field">
                    <label htmlFor="reg-state" className="auth-label">
                      <span className="material-symbols-outlined">location_on</span>
                      State
                    </label>
                    <select
                      id="reg-state"
                      className="auth-input"
                      value={state}
                      onChange={(e) => setState(e.target.value)}
                    >
                      {INDIAN_STATES.map((s) => (
                        <option key={s} value={s}>
                          {s}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div className="auth-field">
                    <label htmlFor="reg-district" className="auth-label">
                      <span className="material-symbols-outlined">my_location</span>
                      District / City
                    </label>
                    <input
                      id="reg-district"
                      type="text"
                      className="auth-input"
                      placeholder="e.g. Nashik, Pune"
                      value={district}
                      onChange={(e) => setDistrict(e.target.value)}
                    />
                  </div>
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
                  <div className="auth-field">
                    <label htmlFor="reg-occupation" className="auth-label">
                      <span className="material-symbols-outlined">work</span>
                      Occupation
                    </label>
                    <select
                      id="reg-occupation"
                      className="auth-input"
                      value={occupation}
                      onChange={(e) => setOccupation(e.target.value)}
                    >
                      <option value="">Select occupation...</option>
                      {OCCUPATIONS.map((occ) => (
                        <option key={occ} value={occ}>
                          {occ}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div className="auth-field">
                    <label htmlFor="reg-income" className="auth-label">
                      <span className="material-symbols-outlined">currency_rupee</span>
                      Annual Family Income (₹)
                    </label>
                    <input
                      id="reg-income"
                      type="number"
                      min="0"
                      step="1000"
                      className="auth-input"
                      placeholder="e.g. 180000"
                      value={annualIncome}
                      onChange={(e) => setAnnualIncome(e.target.value)}
                    />
                  </div>
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '0.5rem' }}>
                  <div className="auth-field">
                    <label htmlFor="reg-age" className="auth-label">
                      <span className="material-symbols-outlined">cake</span>
                      Age
                    </label>
                    <input
                      id="reg-age"
                      type="number"
                      min="1"
                      max="120"
                      className="auth-input"
                      placeholder="e.g. 28"
                      value={age}
                      onChange={(e) => setAge(e.target.value)}
                    />
                  </div>

                  <div className="auth-field">
                    <label htmlFor="reg-gender" className="auth-label">
                      <span className="material-symbols-outlined">wc</span>
                      Gender
                    </label>
                    <select
                      id="reg-gender"
                      className="auth-input"
                      value={gender}
                      onChange={(e) => setGender(e.target.value)}
                    >
                      <option value="">Select...</option>
                      <option value="Female">Female</option>
                      <option value="Male">Male</option>
                      <option value="Other">Other</option>
                    </select>
                  </div>

                  <div className="auth-field">
                    <label htmlFor="reg-caste" className="auth-label">
                      <span className="material-symbols-outlined">diversity_3</span>
                      Category
                    </label>
                    <select
                      id="reg-caste"
                      className="auth-input"
                      value={casteCategory}
                      onChange={(e) => setCasteCategory(e.target.value)}
                    >
                      <option value="">Select...</option>
                      {SOCIAL_CATEGORIES.map((c) => (
                        <option key={c} value={c}>
                          {c}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
                  <div className="auth-field">
                    <label htmlFor="reg-land" className="auth-label">
                      <span className="material-symbols-outlined">landscape</span>
                      Landholding (Acres)
                      <span className="auth-optional-tag">(optional)</span>
                    </label>
                    <input
                      id="reg-land"
                      type="number"
                      step="0.1"
                      min="0"
                      className="auth-input"
                      placeholder="e.g. 2.5"
                      value={landholding}
                      onChange={(e) => setLandholding(e.target.value)}
                    />
                  </div>

                  <div className="auth-field">
                    <label htmlFor="reg-lang" className="auth-label">
                      <span className="material-symbols-outlined">translate</span>
                      Preferred Language
                    </label>
                    <select
                      id="reg-lang"
                      className="auth-input"
                      value={preferredLang}
                      onChange={(e) => setPreferredLang(e.target.value as Language)}
                    >
                      <option value="en">English</option>
                      <option value="hi">हिंदी (Hindi)</option>
                      <option value="mr">मराठी (Marathi)</option>
                    </select>
                  </div>
                </div>
              </div>
            </>
          )}

          {/* Submit Button */}
          <button
            type="submit"
            className="auth-submit-btn"
            disabled={isLoading}
          >
            {isLoading ? (
              <>
                <span className="auth-spinner" />
                <span>{mode === 'login' ? 'Signing in...' : 'Registering citizen profile...'}</span>
              </>
            ) : (
              <>
                <span className="material-symbols-outlined">
                  {mode === 'login' ? 'arrow_forward' : 'check_circle'}
                </span>
                <span>{mode === 'login' ? 'Sign In & Load Profile' : 'Register & Start'}</span>
              </>
            )}
          </button>
        </form>

        {/* Switch prompt */}
        <div className="auth-switch-prompt">
          {mode === 'login' ? (
            <>
              New citizen?{' '}
              <button type="button" className="auth-switch-btn" onClick={() => switchMode('register')}>
                Register with your profile details
              </button>
            </>
          ) : (
            <>
              Already registered?{' '}
              <button type="button" className="auth-switch-btn" onClick={() => switchMode('login')}>
                Sign in to your account
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default AuthModal;

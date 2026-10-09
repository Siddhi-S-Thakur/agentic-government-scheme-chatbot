import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { loginUser, registerUser, fetchCurrentUser, fetchUserProfile, updateUserProfile as apiUpdateProfile } from '../api/client';
import type { UserProfile, RegisterPayload } from '../types/api';

export interface AuthUser {
  id: number;
  username: string;
  full_name: string;
  email: string | null;
  session_id: string;
  profile?: UserProfile;
}

interface AuthContextType {
  user: AuthUser | null;
  profile: UserProfile;
  isLoading: boolean;
  error: string | null;
  /** A session_id that always exists — either the logged-in user's or a guest UUID */
  guestSessionId: string;
  isGuest: boolean;
  login: (usernameOrEmail: string, password: string) => Promise<void>;
  register: (payload: RegisterPayload) => Promise<void>;
  updateProfile: (updated: UserProfile) => Promise<void>;
  refreshProfile: () => Promise<void>;
  logout: () => void;
  clearError: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const SESSION_KEY = 'govscheme_session';
const GUEST_SESSION_KEY = 'govscheme_guest_session';

function generateGuestSessionId(): string {
  // Simple UUID v4 generator
  return 'guest-' + 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
    const r = (Math.random() * 16) | 0;
    const v = c === 'x' ? r : (r & 0x3) | 0x8;
    return v.toString(16);
  });
}

function getOrCreateGuestSessionId(): string {
  const existing = localStorage.getItem(GUEST_SESSION_KEY);
  if (existing) return existing;
  const id = generateGuestSessionId();
  localStorage.setItem(GUEST_SESSION_KEY, id);
  return id;
}

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [profile, setProfile] = useState<UserProfile>({});
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [guestSessionId] = useState<string>(() => getOrCreateGuestSessionId());

  const isGuest = user === null;
  const activeSessionId = user?.session_id || guestSessionId;

  // On mount, check for a saved session
  useEffect(() => {
    const saved = localStorage.getItem(SESSION_KEY);
    if (saved) {
      try {
        const parsed = JSON.parse(saved) as AuthUser;
        fetchCurrentUser(parsed.session_id)
          .then((userData) => {
            setUser(userData);
            if (userData.profile) {
              setProfile(userData.profile);
            } else {
              // Fetch profile from endpoint if not attached
              fetchUserProfile(parsed.session_id).then(setProfile);
            }
          })
          .catch(() => {
            localStorage.removeItem(SESSION_KEY);
          })
          .finally(() => setIsLoading(false));
      } catch {
        localStorage.removeItem(SESSION_KEY);
        setIsLoading(false);
      }
    } else {
      setIsLoading(false);
    }
  }, []);

  const login = useCallback(async (usernameOrEmail: string, password: string) => {
    setError(null);
    setIsLoading(true);
    try {
      const userData = await loginUser(usernameOrEmail, password);
      setUser(userData);
      if (userData.profile) {
        setProfile(userData.profile);
      } else {
        const p = await fetchUserProfile(userData.session_id);
        setProfile(p);
      }
      localStorage.setItem(SESSION_KEY, JSON.stringify(userData));
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Login failed. Please try again.';
      setError(message);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const register = useCallback(async (payload: RegisterPayload) => {
    setError(null);
    setIsLoading(true);
    try {
      const userData = await registerUser(payload);
      setUser(userData);
      if (userData.profile) {
        setProfile(userData.profile);
      }
      localStorage.setItem(SESSION_KEY, JSON.stringify(userData));
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Registration failed. Please try again.';
      setError(message);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const updateProfile = useCallback(async (updated: UserProfile) => {
    if (!user) return;
    try {
      const saved = await apiUpdateProfile(user.session_id, updated);
      setProfile(saved);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to update profile';
      setError(message);
      throw err;
    }
  }, [user]);

  const refreshProfile = useCallback(async () => {
    if (!user) return;
    try {
      const p = await fetchUserProfile(user.session_id);
      setProfile(p);
    } catch (err) {
      console.warn('Could not refresh profile:', err);
    }
  }, [user]);

  const logout = useCallback(() => {
    setUser(null);
    setProfile({});
    localStorage.removeItem(SESSION_KEY);
    setError(null);
  }, []);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return (
    <AuthContext.Provider
      value={{
        user,
        profile,
        isLoading,
        error,
        guestSessionId: activeSessionId,
        isGuest,
        login,
        register,
        updateProfile,
        refreshProfile,
        logout,
        clearError,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export function useAuth(): AuthContextType {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return ctx;
}

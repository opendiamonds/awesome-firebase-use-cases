import React, { createContext, useState, useEffect, useContext, useCallback } from 'react';
import { apiUrl } from '../config/api';

export type StoryAction = 'view' | 'edit' | 'review';
export type AuthorizationStatus = 'pending' | 'approved' | 'rejected';

export interface StoryPermission {
  view: boolean;
  edit: boolean;
  review: boolean;
  can_view?: boolean;
  can_edit?: boolean;
  can_review?: boolean;
}

export interface PendingRequest {
  id: number;
  requested_role: string;
  created_at?: string;
  updated_at?: string;
}

export interface User {
  id?: number;
  username: string;
  role: string | null;
  is_active?: boolean;
  authorization_status?: AuthorizationStatus;
  permissions?: Record<string, StoryPermission>;
  pending_request?: PendingRequest | null;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  isPending: boolean;
  login: (username: string, token: string, role: string | null) => Promise<void>;
  logout: () => void;
  checkAuthSession: () => Promise<boolean>;
  can: (storyId: string, action?: StoryAction) => boolean;
  canArch: (action?: StoryAction) => boolean;
  refreshMe: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const ARCH_STORIES = new Set(['A1', 'A2', 'A4']);
const ARCH_CANONICAL = 'A1';

async function fetchMe(tokenVal: string): Promise<User> {
  const res = await fetch(apiUrl('/api/auth/me'), {
    headers: { Authorization: `Bearer ${tokenVal}` },
  });
  if (!res.ok) {
    throw new Error('session_invalid');
  }
  const data = await res.json();
  return {
    id: data.id,
    username: data.username,
    role: data.role,
    is_active: data.is_active,
    authorization_status: data.authorization_status || 'approved',
    permissions: data.permissions || {},
    pending_request: data.pending_request || null,
  };
}

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const applyUser = (u: User, tokenVal: string) => {
    localStorage.setItem('token', tokenVal);
    localStorage.setItem('username', u.username);
    localStorage.setItem('role', u.role || '');
    localStorage.setItem('authorization_status', u.authorization_status || 'approved');
    setToken(tokenVal);
    setUser(u);
  };

  const logout = useCallback(() => {
    localStorage.removeItem('token');
    localStorage.removeItem('username');
    localStorage.removeItem('role');
    localStorage.removeItem('authorization_status');
    setToken(null);
    setUser(null);
  }, []);

  const refreshMe = useCallback(async () => {
    const activeToken = token || localStorage.getItem('token');
    if (!activeToken) return;
    const me = await fetchMe(activeToken);
    applyUser(me, activeToken);
  }, [token]);

  useEffect(() => {
    const savedToken = localStorage.getItem('token');
    if (!savedToken) {
      setIsLoading(false);
      return;
    }
    fetchMe(savedToken)
      .then((me) => applyUser(me, savedToken))
      .catch(() => logout())
      .finally(() => setIsLoading(false));
  }, [logout]);

  const login = async (username: string, tokenVal: string, roleVal: string | null) => {
    localStorage.setItem('token', tokenVal);
    localStorage.setItem('username', username);
    localStorage.setItem('role', roleVal || '');
    setToken(tokenVal);
    setUser({ username, role: roleVal, permissions: {}, authorization_status: 'approved' });
    try {
      const me = await fetchMe(tokenVal);
      applyUser(me, tokenVal);
    } catch {
      // keep token
    }
  };

  const checkAuthSession = async (): Promise<boolean> => {
    const activeToken = token || localStorage.getItem('token');
    if (!activeToken) {
      logout();
      return false;
    }
    try {
      const me = await fetchMe(activeToken);
      applyUser(me, activeToken);
      return true;
    } catch {
      logout();
      return false;
    }
  };

  const isPending = user?.authorization_status === 'pending';

  const can = (storyId: string, action: StoryAction = 'view'): boolean => {
    if (isPending) return false;
    const key = ARCH_STORIES.has(storyId) ? ARCH_CANONICAL : storyId;
    const p = user?.permissions?.[key];
    if (!p) return false;
    const hasView = !!(p.view || p.can_view || p.edit || p.can_edit || p.review || p.can_review);
    const hasEdit = !!(p.edit || p.can_edit);
    const hasReview = !!(p.review || p.can_review);
    if (action === 'view') return hasView;
    if (action === 'edit') return hasEdit;
    if (action === 'review') return hasReview;
    return false;
  };

  const canArch = (action: StoryAction = 'view') => can(ARCH_CANONICAL, action);

  const isAuthenticated = !!token;

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isAuthenticated,
        isLoading,
        isPending,
        login,
        logout,
        checkAuthSession,
        can,
        canArch,
        refreshMe,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

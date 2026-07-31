import React, { useState, useEffect, useCallback } from 'react';
import { apiUrl } from '../config/api';
import { AuthContext } from './auth-context';
import type { StoryAction, User } from './auth-context';

/** A1／A2／A4 視為同一「架構圖生成」能力，以 A1 為準 */
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
  // 只有「真的要打 /me」時才處於 loading。用 lazy initial state 讀 localStorage，
  // 沒有 token 的情況第一次 render 就是 false，不必在 effect body 內同步 setState
  // （react-hooks/set-state-in-effect），也省掉登入頁的載入畫面閃爍。
  const [isLoading, setIsLoading] = useState(() => !!localStorage.getItem('token'));

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

  // 初始化：有 token 則打 /me 取得最新 role + permissions
  useEffect(() => {
    const savedToken = localStorage.getItem('token');
    // isLoading 的初始值已由同一份 localStorage 判定，這裡直接返回即可。
    if (!savedToken) return;
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
      // /me 失敗仍保留登入 token，permissions 稍後再補
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

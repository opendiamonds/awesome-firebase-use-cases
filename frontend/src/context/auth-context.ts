import { createContext, useContext } from 'react';

// Context 物件、型別與 useAuth hook 與 AuthProvider 分檔存放：react-refresh 要求
// 一個模組只匯出 component，否則編輯該檔會讓 HMR 退化成整頁重載。
// AuthProvider 在 ./AuthContext.tsx。

export type StoryAction = 'view' | 'edit' | 'review';

export interface StoryPermission {
  view: boolean;
  edit: boolean;
  review: boolean;
  can_view?: boolean;
  can_edit?: boolean;
  can_review?: boolean;
}

export interface User {
  id?: number;
  username: string;
  role: string;
  is_active?: boolean;
  permissions?: Record<string, StoryPermission>;
}

export interface AuthContextType {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (username: string, token: string, role: string) => Promise<void>;
  logout: () => void;
  checkAuthSession: () => Promise<boolean>;
  can: (storyId: string, action?: StoryAction) => boolean;
  /** 架構圖生成（A1／A2／A4 同一功能） */
  canArch: (action?: StoryAction) => boolean;
  refreshMe: () => Promise<void>;
}

export const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

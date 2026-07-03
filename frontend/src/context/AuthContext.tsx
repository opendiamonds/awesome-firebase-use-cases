import React, { createContext, useState, useEffect, useContext } from 'react';

export interface User {
  id?: number;
  username: string;
  role: string;
  is_active?: boolean;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (username: string, token: string, role: string) => void;
  logout: () => void;
  checkAuthSession: () => Promise<boolean>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // 1. 初始化時從 localStorage 讀取狀態
  useEffect(() => {
    const savedToken = localStorage.getItem('token');
    const savedUsername = localStorage.getItem('username');
    const savedRole = localStorage.getItem('role');

    if (savedToken && savedUsername && savedRole) {
      setToken(savedToken);
      setUser({ username: savedUsername, role: savedRole });
    }
    setIsLoading(false);
  }, []);

  // 2. 登入成功寫入狀態
  const login = (username: string, tokenVal: string, roleVal: string) => {
    localStorage.setItem('token', tokenVal);
    localStorage.setItem('username', username);
    localStorage.setItem('role', roleVal);
    setToken(tokenVal);
    setUser({ username, role: roleVal });
  };

  // 3. 登出清除狀態
  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('username');
    localStorage.removeItem('role');
    setToken(null);
    setUser(null);
  };

  // 4. 校驗 Session (從後端獲取最新資訊)
  const checkAuthSession = async (): Promise<boolean> => {
    const activeToken = token || localStorage.getItem('token');
    if (!activeToken) {
      logout();
      return false;
    }

    try {
      const res = await fetch('http://localhost:8000/api/auth/me', {
        headers: {
          'Authorization': `Bearer ${activeToken}`
        }
      });
      if (res.ok) {
        const data = await res.json();
        setUser({ username: data.username, role: data.role });
        localStorage.setItem('role', data.role); // 更新快取角色
        return true;
      } else {
        logout();
        return false;
      }
    } catch (err) {
      // 網路連線錯誤暫不登出，保留快取狀態
      return !!user;
    }
  };

  const isAuthenticated = !!token;

  return (
    <AuthContext.Provider value={{
      user,
      token,
      isAuthenticated,
      isLoading,
      login,
      logout,
      checkAuthSession
    }}>
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

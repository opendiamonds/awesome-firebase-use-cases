import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { apiUrl } from '../config/api';

interface DbUser {
  id: number;
  username: string;
  role: string;
  is_active: boolean;
}

const AVAILABLE_ROLES = [
  "Project_Admin",
  "Platform_Admin",
  "Project_Architect",
  "SRE",
  "FinOps_Analyst",
  "Platform_Engineer",
  "Security_Reviewer",
  "Ops_Lead",
  "Project_Editor",
  "Developer",
  "Platform_Owner"
];

export const AdminPage: React.FC = () => {
  const { token, user: currentUser, can } = useAuth();
  const canEdit = can('J3a', 'edit');
  const [users, setUsers] = useState<DbUser[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' } | null>(null);

  const fetchUsers = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await fetch(apiUrl('/api/auth/list'), {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || '取得使用者列表失敗');
      }
      const data = await res.json();
      setUsers(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : '連線失敗');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (token) {
      fetchUsers();
    }
  }, [token]);

  const showToast = (message: string, type: 'success' | 'error') => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 4000);
  };

  const handleRoleChange = async (userId: number, newRole: string) => {
    try {
      const res = await fetch(apiUrl(`/api/auth/${userId}/role`), {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ role: newRole })
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.detail || '更新角色失敗');
      }

      // 更新本地狀態
      setUsers(prev => prev.map(u => u.id === userId ? { ...u, role: newRole } : u));
      showToast(`✔ 已成功更新使用者 '${data.username}' 的角色為 '${newRole}'`, 'success');
    } catch (err) {
      showToast(err instanceof Error ? err.message : '更新失敗', 'error');
      // 重新讀取確保資料一致
      fetchUsers();
    }
  };

  return (
    <div className="relative min-h-full bg-slate-950 p-6 md:p-10 pb-16 text-white font-sans w-full">
      {/* Toast Alert */}
      {toast && (
        <div className={`fixed top-6 left-1/2 -translate-x-1/2 z-50 px-6 py-4 rounded-2xl shadow-xl backdrop-blur-xl border flex items-center gap-3 animate-[slideInDown_0.3s_ease-out] ${
          toast.type === 'success' 
            ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-300' 
            : 'bg-red-500/10 border-red-500/20 text-red-300'
        }`}>
          <span className="font-semibold text-sm tracking-wide">{toast.message}</span>
        </div>
      )}

      {/* Title Header */}
      <div className="flex flex-col gap-2 mb-8">
        <h1 className="text-3xl font-black tracking-tight text-white flex items-center gap-3">
          <svg className="w-8 h-8 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
          </svg>
          使用者角色指派
        </h1>
        <p className="text-slate-400 text-sm font-medium">
          指定哪個使用者對應哪個平台角色（J3a）。細項權限請至「角色細項權限」頁調整。列表可用滾輪捲動。
        </p>
      </div>

      {/* Main Table Card (Glassmorphism) */}
      <div className="bg-white/5 backdrop-blur-2xl border border-white/10 rounded-[2rem] shadow-2xl overflow-hidden">
        {isLoading ? (
          <div className="p-20 text-center flex flex-col items-center gap-3 text-slate-400">
            <div className="w-10 h-10 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
            <span className="text-sm font-semibold">載入使用者列表中...</span>
          </div>
        ) : error ? (
          <div className="p-20 text-center flex flex-col items-center gap-4 text-red-300">
            <svg className="w-12 h-12" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>
            <span className="font-bold">{error}</span>
            <button 
              onClick={fetchUsers}
              className="px-6 py-2 bg-slate-800 text-white text-xs font-bold rounded-xl border border-slate-700 hover:bg-slate-700 transition-colors"
            >
              重新整理
            </button>
          </div>
        ) : (
          <div className="overflow-auto max-h-[min(70vh,720px)] overscroll-contain">
            <table className="w-full text-left border-collapse">
              <thead className="sticky top-0 z-20">
                <tr className="bg-slate-950 border-b border-white/10 text-xs font-bold text-slate-400 tracking-wider uppercase">
                  <th className="px-8 py-5">使用者帳號 (Username)</th>
                  <th className="px-8 py-5">目前角色 (Current Role)</th>
                  <th className="px-8 py-5">操作指派 (Assign New Role)</th>
                  <th className="px-8 py-5">狀態 (Status)</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5 font-medium">
                {users.map((u) => (
                  <tr key={u.id} className="hover:bg-white/[0.02] transition-colors">
                    <td className="px-8 py-5 flex items-center gap-3">
                      <div className="w-9 h-9 bg-blue-500/10 text-blue-400 rounded-xl flex items-center justify-center font-bold">
                        {u.username[0].toUpperCase()}
                      </div>
                      <div className="flex flex-col">
                        <span className="text-sm font-bold text-white">
                          {u.username}
                          {u.username === currentUser?.username && (
                            <span className="ml-2 px-2 py-0.5 bg-blue-500/20 text-blue-300 text-[10px] font-extrabold rounded-full border border-blue-500/30">
                              目前登入
                            </span>
                          )}
                        </span>
                      </div>
                    </td>
                    <td className="px-8 py-5">
                      <span className={`px-3 py-1 rounded-full text-xs font-bold border ${
                        u.role.includes('Admin')
                          ? 'bg-purple-500/10 border-purple-500/20 text-purple-300'
                          : u.role === 'Project_Architect'
                          ? 'bg-blue-500/10 border-blue-500/20 text-blue-300'
                          : u.role === 'SRE'
                          ? 'bg-rose-500/10 border-rose-500/20 text-rose-300'
                          : 'bg-slate-500/10 border-slate-500/20 text-slate-300'
                      }`}>
                        {u.role}
                      </span>
                    </td>
                    <td className="px-8 py-5">
                      <select 
                        value={u.role}
                        disabled={!canEdit}
                        onChange={(e) => handleRoleChange(u.id, e.target.value)}
                        className="bg-slate-900 border border-slate-800 text-slate-300 text-xs font-bold rounded-xl px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500 cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        {AVAILABLE_ROLES.map((roleOpt) => (
                          <option key={roleOpt} value={roleOpt}>
                            {roleOpt}
                          </option>
                        ))}
                      </select>
                    </td>
                    <td className="px-8 py-5">
                      <div className="flex items-center gap-2">
                        <span className={`w-2.5 h-2.5 rounded-full ${u.is_active ? 'bg-emerald-500 animate-pulse' : 'bg-slate-500'}`}></span>
                        <span className="text-xs text-slate-300">{u.is_active ? '啟用中' : '已停用'}</span>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

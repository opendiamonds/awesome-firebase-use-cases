import React, { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/auth-context';
import { apiUrl } from '../config/api';

interface DbUser {
  id: number;
  username: string;
  role: string | null;
  is_active: boolean;
  authorization_status: string;
  requested_role?: string | null;
}

const AVAILABLE_ROLES = [
  'Project_Admin',
  'Platform_Admin',
  'Project_Architect',
  'SRE',
  'FinOps_Analyst',
  'Platform_Engineer',
  'Security_Reviewer',
  'Ops_Lead',
  'Project_Editor',
  'Developer',
  'Platform_Owner',
];

export const AdminPage: React.FC = () => {
  const { token, user: currentUser, can } = useAuth();
  const canEdit = can('J3a', 'edit');
  const [users, setUsers] = useState<DbUser[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' } | null>(null);

  // 純抓取，完全不碰 state。react-hooks/set-state-in-effect 會做過程間分析：
  // 只要 effect 同步呼叫的函式內部有 setState 就會被擋，因此把 state 更新一律
  // 留在呼叫端的 .then／.catch／.finally callback 內（規則允許的形式）。
  const fetchUserList = useCallback(async (): Promise<DbUser[]> => {
    const res = await fetch(apiUrl('/api/auth/list'), {
      headers: { Authorization: `Bearer ${token}` },
    });
    const data = await res.json();
    if (!res.ok) {
      throw new Error(data.detail || '取得使用者列表失敗');
    }
    return data;
  }, [token]);

  // 使用者主動觸發的重新整理：先切回 loading 再抓，事件處理內同步 setState 無妨。
  const fetchUsers = useCallback(() => {
    setIsLoading(true);
    setError(null);
    return fetchUserList()
      .then(setUsers)
      .catch((err) => setError(err instanceof Error ? err.message : '連線失敗'))
      .finally(() => setIsLoading(false));
  }, [fetchUserList]);

  useEffect(() => {
    if (!token) return;
    // 初次載入時 isLoading 已是 true，不需要再設一次。
    let cancelled = false;
    fetchUserList()
      .then((data) => { if (!cancelled) setUsers(data); })
      .catch((err) => { if (!cancelled) setError(err instanceof Error ? err.message : '連線失敗'); })
      .finally(() => { if (!cancelled) setIsLoading(false); });
    return () => { cancelled = true; };
  }, [token, fetchUserList]);

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
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ role: newRole }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || '更新角色失敗');
      setUsers((prev) => prev.map((u) => (u.id === userId ? { ...u, role: newRole } : u)));
      showToast(`✔ 已更新 '${data.username}' 角色為 '${newRole}'`, 'success');
    } catch (err) {
      showToast(err instanceof Error ? err.message : '更新失敗', 'error');
      fetchUsers();
    }
  };

  const handleToggleActive = async (u: DbUser) => {
    try {
      const res = await fetch(apiUrl(`/api/auth/${u.id}/active`), {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ is_active: !u.is_active }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || '更新狀態失敗');
      showToast(
        data.is_active ? `✔ 已啟用 ${data.username}` : `✔ 已停用 ${data.username}`,
        'success'
      );
      fetchUsers();
    } catch (err) {
      showToast(err instanceof Error ? err.message : '更新失敗', 'error');
    }
  };

  const handleDelete = async (u: DbUser) => {
    if (!confirm(`確定刪除使用者 ${u.username}？此操作無法復原。`)) return;
    try {
      const res = await fetch(apiUrl(`/api/auth/${u.id}`), {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` },
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || '刪除失敗');
      showToast(`✔ 已刪除 ${data.deleted_username}`, 'success');
      fetchUsers();
    } catch (err) {
      showToast(err instanceof Error ? err.message : '刪除失敗', 'error');
    }
  };

  return (
    <div className="relative min-h-full bg-slate-950 p-6 md:p-10 pb-16 text-white font-sans w-full">
      {toast && (
        <div
          className={`fixed top-6 left-1/2 -translate-x-1/2 z-50 px-6 py-4 rounded-2xl shadow-xl backdrop-blur-xl border flex items-center gap-3 ${
            toast.type === 'success'
              ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-300'
              : 'bg-red-500/10 border-red-500/20 text-red-300'
          }`}
        >
          <span className="font-semibold text-sm tracking-wide">{toast.message}</span>
        </div>
      )}

      <div className="flex flex-col gap-2 mb-8">
        <h1 className="text-3xl font-black tracking-tight text-white">使用者角色指派</h1>
        <p className="text-slate-400 text-sm font-medium">
          指定使用者角色、啟停用與刪除（J3a）。待授權申請請至{' '}
          <Link to="/admin/authorization-requests" className="text-blue-400 hover:underline">
            授權申請
          </Link>
          。
        </p>
      </div>

      <div className="bg-white/5 backdrop-blur-2xl border border-white/10 rounded-[2rem] shadow-2xl overflow-hidden">
        {isLoading ? (
          <div className="p-20 text-center text-slate-400 text-sm">載入中…</div>
        ) : error ? (
          <div className="p-20 text-center text-red-300 text-sm">{error}</div>
        ) : (
          <div className="overflow-auto max-h-[min(70vh,720px)]">
            <table className="w-full text-left border-collapse">
              <thead className="sticky top-0 z-20">
                <tr className="bg-slate-950 border-b border-white/10 text-xs font-bold text-slate-400 tracking-wider uppercase">
                  <th className="px-6 py-5">使用者</th>
                  <th className="px-6 py-5">授權狀態</th>
                  <th className="px-6 py-5">角色</th>
                  <th className="px-6 py-5">操作</th>
                  <th className="px-6 py-5">啟用</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5 font-medium">
                {users.map((u) => (
                  <tr key={u.id} className="hover:bg-white/[0.02]">
                    <td className="px-6 py-4">
                      <span className="text-sm font-bold text-white">
                        {u.username}
                        {u.username === currentUser?.username && (
                          <span className="ml-2 px-2 py-0.5 bg-blue-500/20 text-blue-300 text-[10px] font-extrabold rounded-full">
                            目前登入
                          </span>
                        )}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-xs">
                      {u.authorization_status === 'pending' ? (
                        <span className="text-amber-300">
                          待授權
                          {u.requested_role ? `（${u.requested_role}）` : ''}
                        </span>
                      ) : (
                        <span className="text-emerald-300">已核准</span>
                      )}
                    </td>
                    <td className="px-6 py-4">
                      <span className="text-xs text-slate-300">{u.role || '—'}</span>
                    </td>
                    <td className="px-6 py-4">
                      {u.authorization_status === 'approved' ? (
                        <select
                          value={u.role || ''}
                          disabled={!canEdit}
                          onChange={(e) => handleRoleChange(u.id, e.target.value)}
                          className="bg-slate-900 border border-slate-800 text-slate-300 text-xs font-bold rounded-xl px-3 py-2 disabled:opacity-50"
                        >
                          {AVAILABLE_ROLES.map((roleOpt) => (
                            <option key={roleOpt} value={roleOpt}>
                              {roleOpt}
                            </option>
                          ))}
                        </select>
                      ) : (
                        <Link
                          to="/admin/authorization-requests"
                          className="text-xs text-blue-400 hover:underline"
                        >
                          至授權申請處理
                        </Link>
                      )}
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex flex-col gap-2">
                        <div className="flex items-center gap-2">
                          <span
                            className={`w-2.5 h-2.5 rounded-full ${
                              u.is_active ? 'bg-emerald-500' : 'bg-slate-500'
                            }`}
                          />
                          <span className="text-xs text-slate-300">
                            {u.is_active ? '啟用中' : '已停用'}
                          </span>
                        </div>
                        {canEdit && u.username !== currentUser?.username && (
                          <div className="flex gap-2">
                            <button
                              type="button"
                              onClick={() => handleToggleActive(u)}
                              className="px-2 py-1 text-[10px] font-bold rounded-lg bg-slate-800 border border-slate-700"
                            >
                              {u.is_active ? '停用' : '啟用'}
                            </button>
                            {!u.is_active && (
                              <button
                                type="button"
                                onClick={() => handleDelete(u)}
                                className="px-2 py-1 text-[10px] font-bold rounded-lg bg-red-900/40 border border-red-800 text-red-300"
                              >
                                刪除
                              </button>
                            )}
                          </div>
                        )}
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

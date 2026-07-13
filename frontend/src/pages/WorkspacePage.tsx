import { useState, useRef, useEffect, useCallback } from 'react';
import { ChatBox } from '../components/ChatBox';
import type { Message } from '../components/ChatBox';
import { DrawioCanvas } from '../components/DrawioCanvas';
import type { DiagramSaveStatus, DrawioCanvasRef } from '../components/DrawioCanvas';
import { ShareModal } from '../components/ShareModal';
import { useAuth } from '../context/AuthContext';
import { useCollaboration } from '../hooks/useCollaboration';
import { apiUrl } from '../config/api';

type ToastType = 'success' | 'error';

interface Diagram {
  id: number;
  title: string;
  xml_data?: string;
  is_owner: boolean;
  shared_user_ids?: number[];
  updated_at: string;
}

type ToastState = {
  message: string;
  type: ToastType;
  /** 成功／失敗下方說明 */
  hint?: string;
  /** 顯示 Story 對齊的 CTA stub */
  showCtas?: boolean;
} | null;

const API_COLLAB = apiUrl('/api/collab');

/** 全部重置寫回 DB 用的空白畫布 */
const EMPTY_DIAGRAM_XML =
  '<mxGraphModel><root><mxCell id="0"/><mxCell id="1" parent="0"/></root></mxGraphModel>';

const DEFAULT_WELCOME: Message = {
  role: 'assistant',
  content:
    '嗨！我是您的 AI 雲端架構助理 👋\n請描述您想建立的雲端架構，例如：\n✨ 我要做一個電商網站\n✨ 我要一個包含 WAF 與 Aurora 的高可用架構',
};

/** 將後端錯誤對齊 User Story 失敗文案 */
function formatGenerateError(raw: string): string {
  if (/region|區域|不支援|not supported|unavailable|resource conflict|不相容/i.test(raw)) {
    return '資源衝突：所選區域不支援該服務';
  }
  return raw.trim() || '生成失敗';
}

export const WorkspacePage = () => {
  const { token, canArch } = useAuth();
  const canEditArch = canArch('edit');
  const canReviewArch = canArch('review');
  const canViewOnly = canArch('view') && !canEditArch;
  const canvasRef = useRef<DrawioCanvasRef>(null);

  const [xml, setXml] = useState<string>('');
  const [diagrams, setDiagrams] = useState<Diagram[]>([]);
  const [currentDiagramId, setCurrentDiagramId] = useState<number | null>(null);
  const [isShareModalOpen, setIsShareModalOpen] = useState(false);
  const [isShared, setIsShared] = useState(false);
  const [bootstrapDone, setBootstrapDone] = useState(false);

  const { isConnected, broadcastXml } = useCollaboration({
    workspaceId: currentDiagramId ? currentDiagramId.toString() : '',
    onReceiveXml: (newXml) => {
      if (newXml) {
        setXml(newXml);
      }
    },
  });

  const [isGenerating, setIsGenerating] = useState(false);
  const [progress, setProgress] = useState<string>('');
  const [toast, setToast] = useState<ToastState>(null);
  const [messages, setMessages] = useState<Message[]>([DEFAULT_WELCOME]);
  const [saveStatus, setSaveStatus] = useState<DiagramSaveStatus>('no-file');

  /** 避免 generate 閉包讀到過期的 diagram id */
  const currentDiagramIdRef = useRef<number | null>(null);
  const diagramsRef = useRef<Diagram[]>([]);
  const canvasAutosaveTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    currentDiagramIdRef.current = currentDiagramId;
  }, [currentDiagramId]);

  useEffect(() => {
    diagramsRef.current = diagrams;
  }, [diagrams]);

  const authHeaders = useCallback(
    () => ({
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json',
    }),
    [token]
  );

  const fetchDiagrams = async () => {
    try {
      const response = await fetch(`${API_COLLAB}/diagrams`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (response.ok) {
        const data = await response.json();
        setDiagrams(data);
      }
    } catch (err) {
      console.error('Failed to load diagram list', err);
    }
  };

  /** A4：將 messages 寫回該 user×diagram */
  const persistChat = async (diagramId: number, msgs: Message[]) => {
    try {
      await fetch(`${API_COLLAB}/diagrams/${diagramId}/chat`, {
        method: 'PUT',
        headers: authHeaders(),
        body: JSON.stringify({ messages: msgs }),
      });
    } catch (err) {
      console.error('Failed to persist chat', err);
    }
  };

  const setLastOpened = async (diagramId: number | null) => {
    try {
      await fetch(`${API_COLLAB}/workspace/last-opened`, {
        method: 'PUT',
        headers: authHeaders(),
        body: JSON.stringify({ diagram_id: diagramId }),
      });
    } catch (err) {
      console.error('Failed to update last-opened', err);
    }
  };

  const loadChatForDiagram = async (diagramId: number) => {
    try {
      const response = await fetch(`${API_COLLAB}/diagrams/${diagramId}/chat`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (response.ok) {
        const data = await response.json();
        if (Array.isArray(data.messages) && data.messages.length > 0) {
          setMessages(data.messages);
          return;
        }
      }
    } catch (err) {
      console.error('Failed to load chat', err);
    }
    setMessages([DEFAULT_WELCOME]);
  };

  /** A1 Phase 2：已有 diagram_id 時自動 PUT XML（不自動建新圖） */
  const autosaveDiagramXml = async (diagramId: number, xmlData: string) => {
    setSaveStatus('saving');
    try {
      const title =
        diagramsRef.current.find((d) => d.id === diagramId)?.title || '未命名架構圖';
      const response = await fetch(`${API_COLLAB}/diagrams/${diagramId}`, {
        method: 'PUT',
        headers: authHeaders(),
        body: JSON.stringify({
          xml_data: xmlData,
          title,
        }),
      });
      if (!response.ok) {
        console.error('Autosave diagram failed', response.status);
        setSaveStatus('unsaved');
        return false;
      }
      fetchDiagrams();
      setSaveStatus('saved');
      return true;
    } catch (err) {
      console.error('Autosave diagram failed', err);
      setSaveStatus('unsaved');
      return false;
    }
  };

  /** draw.io iframe autosave → 廣播 WS；有 diagram_id 時 debounce 寫 DB */
  const handleCanvasAutosave = (savedXml: string) => {
    if (!canEditArch) return;
    setXml(savedXml);
    broadcastXml(savedXml);

    const diagramId = currentDiagramIdRef.current;
    if (!diagramId) {
      setSaveStatus('no-file');
      return;
    }

    setSaveStatus('unsaved');
    if (canvasAutosaveTimer.current) {
      clearTimeout(canvasAutosaveTimer.current);
    }
    canvasAutosaveTimer.current = setTimeout(() => {
      void autosaveDiagramXml(diagramId, savedXml);
    }, 1200);
  };

  const showComingSoon = (feature: string) => {
    setToast({
      message: `${feature}即將推出`,
      type: 'success',
      hint: '此功能尚在規劃中，請先繼續對話編輯或手動儲存架構圖。',
      showCtas: false,
    });
  };

  // A4：進入工作區 bootstrap（還原上次圖 + 聊天）
  useEffect(() => {
    if (!token) return;

    const bootstrap = async () => {
      try {
        await fetchDiagrams();
        const response = await fetch(`${API_COLLAB}/workspace/bootstrap`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (!response.ok) return;
        const data = await response.json();
        if (data.diagram) {
          setXml(data.diagram.xml_data || '');
          setCurrentDiagramId(data.diagram.id);
          setSaveStatus(data.diagram.xml_data ? 'saved' : 'unsaved');
          setIsShared(
            !data.diagram.is_owner ||
              (data.diagram.shared_user_ids && data.diagram.shared_user_ids.length > 0)
          );
        } else {
          setSaveStatus('no-file');
        }
        if (Array.isArray(data.messages) && data.messages.length > 0) {
          setMessages(data.messages);
        }
      } catch (err) {
        console.error('Workspace bootstrap failed', err);
      } finally {
        setBootstrapDone(true);
      }
    };

    bootstrap();
  }, [token]);

  const handleLoadDiagram = async (id: number) => {
    try {
      const response = await fetch(`${API_COLLAB}/diagrams/${id}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (response.ok) {
        const data = await response.json();
        if (data.xml_data !== undefined) {
          setXml(data.xml_data);
          setCurrentDiagramId(data.id);
          setSaveStatus('saved');
          setIsShared(
            !data.is_owner || (data.shared_user_ids && data.shared_user_ids.length > 0)
          );
          await loadChatForDiagram(data.id);
          await setLastOpened(data.id);
        }
      }
    } catch (err) {
      console.error('Failed to load diagram', err);
    }
  };

  const handleNewDiagram = async () => {
    if (!canEditArch) {
      showToast('僅檢視／審核權限無法建立架構圖', 'error', { autoDismissMs: 4000 });
      return;
    }
    setXml('');
    setCurrentDiagramId(null);
    setIsShared(false);
    setSaveStatus('no-file');
    setMessages([DEFAULT_WELCOME]);
    await setLastOpened(null);
  };

  const showToast = (
    message: string,
    type: ToastType,
    opts?: { hint?: string; showCtas?: boolean; autoDismissMs?: number }
  ) => {
    setToast({
      message,
      type,
      hint: opts?.hint,
      showCtas: opts?.showCtas,
    });
    const ms = opts?.autoDismissMs;
    if (ms && ms > 0) {
      setTimeout(() => setToast(null), ms);
    }
  };

  const handleGenerate = async (prompt: string) => {
    if (!canArch('edit')) {
      showToast('權限不足：需要架構圖「編輯」權限才能與 AI 對話產圖', 'error', {
        autoDismissMs: 4000,
      });
      return;
    }
    setIsGenerating(true);
    setToast(null);
    setProgress('');

    const newMessages: Message[] = [...messages, { role: 'user', content: prompt }];
    setMessages(newMessages);

    let assistantMessage = '';
    let finalMessages: Message[] = [
      ...newMessages,
      { role: 'assistant', content: '' },
    ];
    let generatedXml: string | null = null;
    let streamError: string | null = null;

    try {
      const response = await fetch(apiUrl('/api/architecture/generate'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          messages: newMessages,
          current_xml: xml || undefined,
        }),
      });

      if (!response.ok) {
        let detail = '生成失敗';
        try {
          const errBody = await response.json();
          if (typeof errBody.detail === 'string') detail = errBody.detail;
        } catch {
          /* ignore */
        }
        throw new Error(detail);
      }

      setMessages(finalMessages);

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      if (reader) {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split('\n');
          buffer = lines.pop() || '';

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const data = JSON.parse(line.slice(6));
                if (data.type === 'message') {
                  assistantMessage += data.content;
                  finalMessages = [
                    ...newMessages,
                    { role: 'assistant', content: assistantMessage },
                  ];
                  setMessages(finalMessages);
                } else if (data.type === 'progress') {
                  setProgress(data.content);
                } else if (data.type === 'xml') {
                  generatedXml = data.content;
                  setXml(data.content);
                  setProgress('');
                } else if (data.type === 'error') {
                  streamError = formatGenerateError(String(data.content || ''));
                  setProgress('');
                }
              } catch {
                // ignore invalid JSON line
              }
            }
          }
        }
      }

      if (streamError) {
        setToast({
          message: streamError,
          type: 'error',
          hint: '請於對話框修改參數後重試。',
          showCtas: true,
        });
      } else if (generatedXml) {
        // Q2-B：僅有 diagram_id 才自動存；無 id 提示手動儲存
        const diagramId = currentDiagramIdRef.current;
        if (diagramId) {
          const ok = await autosaveDiagramXml(diagramId, generatedXml);
          await persistChat(diagramId, finalMessages);
          setToast({
            message: '✔ 架構草圖已生成',
            type: 'success',
            hint: ok
              ? '已自動存檔至資料庫。工具列應顯示「已儲存」。'
              : '產圖成功，但自動存檔失敗，請點「儲存架構圖」重試。',
            showCtas: true,
          });
        } else {
          setSaveStatus('no-file');
          setToast({
            message: '✔ 架構草圖已生成',
            type: 'success',
            hint: '尚未綁定架構圖檔案，請點擊畫布「儲存架構圖」以永久保存。',
            showCtas: true,
          });
        }
      } else if (currentDiagramIdRef.current) {
        // 僅對話、未產圖：仍持久化聊天
        await persistChat(currentDiagramIdRef.current, finalMessages);
      }
    } catch (err) {
      const errMsg = formatGenerateError(
        err instanceof Error ? err.message : '生成失敗'
      );
      setToast({
        message: errMsg,
        type: 'error',
        hint: '請於對話框修改參數後重試。',
        showCtas: true,
      });
    } finally {
      setIsGenerating(false);
    }
  };

  const handleLoadComplete = () => {
    // 產圖成功 Toast 已由 handleGenerate 處理，避免重複彈窗
  };

  /** A4：清空對話（確認後）；有 diagram_id 則呼叫 DELETE，不清 XML */
  const handleClearChat = async () => {
    const ok = window.confirm(
      '確定要清空此架構圖的對話紀錄嗎？\n（不會刪除架構圖本身）'
    );
    if (!ok) return;

    if (currentDiagramId) {
      try {
        const response = await fetch(
          `${API_COLLAB}/diagrams/${currentDiagramId}/chat`,
          {
            method: 'DELETE',
            headers: { Authorization: `Bearer ${token}` },
          }
        );
        if (response.ok) {
          const data = await response.json();
          setMessages(
            Array.isArray(data.messages) && data.messages.length > 0
              ? data.messages
              : [DEFAULT_WELCOME]
          );
          showToast('對話已清空', 'success', { autoDismissMs: 3000 });
          return;
        }
      } catch (err) {
        console.error('Failed to clear chat', err);
        showToast('清空對話失敗', 'error', { autoDismissMs: 4000 });
        return;
      }
    }

    setMessages([DEFAULT_WELCOME]);
    setToast(null);
  };

  /** A1 Phase 2：全部重置 — 清畫布 + 對話；有 id 則寫回空白 XML 並清 chat */
  const handleFullReset = async () => {
    const ok = window.confirm(
      '確定要全部重置嗎？\n將清空畫布與對話紀錄。\n（不會刪除架構圖檔案，但會清空圖面內容）'
    );
    if (!ok) return;

    setXml('');
    setMessages([DEFAULT_WELCOME]);
    setToast(null);
    setSaveStatus(currentDiagramId ? 'saving' : 'no-file');

    if (currentDiagramId) {
      try {
        await autosaveDiagramXml(currentDiagramId, EMPTY_DIAGRAM_XML);
        setXml(EMPTY_DIAGRAM_XML);
        setSaveStatus('saved');
        const response = await fetch(
          `${API_COLLAB}/diagrams/${currentDiagramId}/chat`,
          {
            method: 'DELETE',
            headers: { Authorization: `Bearer ${token}` },
          }
        );
        if (response.ok) {
          const data = await response.json();
          setMessages(
            Array.isArray(data.messages) && data.messages.length > 0
              ? data.messages
              : [DEFAULT_WELCOME]
          );
        }
        showToast('已全部重置', 'success', {
          hint: '畫布與對話已清空。',
          autoDismissMs: 3000,
        });
      } catch (err) {
        console.error('Full reset failed', err);
        showToast('全部重置失敗', 'error', { autoDismissMs: 4000 });
      }
    } else {
      showToast('已全部重置', 'success', {
        hint: '畫布與對話已清空。',
        autoDismissMs: 3000,
      });
    }
  };

  const handleSaveDiagram = async (currentXml: string) => {
    if (!canEditArch) {
      showToast('僅檢視／審核權限無法儲存架構圖', 'error', { autoDismissMs: 4000 });
      return;
    }
    if (!currentXml) {
      showToast('沒有可儲存的架構圖', 'error', { autoDismissMs: 4000 });
      return;
    }
    try {
      if (currentDiagramId) {
        setSaveStatus('saving');
        const response = await fetch(`${API_COLLAB}/diagrams/${currentDiagramId}`, {
          method: 'PUT',
          headers: authHeaders(),
          body: JSON.stringify({
            xml_data: currentXml,
            title:
              diagrams.find((d) => d.id === currentDiagramId)?.title || '未命名架構圖',
          }),
        });
        if (response.ok) {
          showToast('架構圖更新成功', 'success', { autoDismissMs: 3000 });
          setSaveStatus('saved');
          fetchDiagrams();
          await persistChat(currentDiagramId, messages);
        } else {
          throw new Error('更新失敗');
        }
      } else {
        const title = prompt('請為這個架構圖命名：', '新架構圖');
        if (!title) return;
        setSaveStatus('saving');
        const response = await fetch(`${API_COLLAB}/diagrams`, {
          method: 'POST',
          headers: authHeaders(),
          body: JSON.stringify({ xml_data: currentXml, title }),
        });
        if (response.ok) {
          const data = await response.json();
          setCurrentDiagramId(data.id);
          setSaveStatus('saved');
          showToast('架構圖建立成功', 'success', { autoDismissMs: 3000 });
          fetchDiagrams();
          await persistChat(data.id, messages);
        } else {
          setSaveStatus('no-file');
          throw new Error('建立失敗');
        }
      }
    } catch {
      setSaveStatus(currentDiagramIdRef.current ? 'unsaved' : 'no-file');
      showToast('儲存架構圖失敗', 'error', { autoDismissMs: 4000 });
    }
  };

  return (
    <div className="relative flex h-full w-full overflow-hidden">
      {canViewOnly && (
        <div className="absolute top-16 left-1/2 -translate-x-1/2 z-50 max-w-lg w-[min(92vw,28rem)] px-4 py-2.5 rounded-xl bg-amber-50 border border-amber-200 text-amber-900 text-xs font-semibold text-center shadow-sm">
          {canReviewArch
            ? '審核模式：可開啟他人分享的架構圖並審核；無法編輯畫布或與 AI 對話'
            : '僅檢視：只能開啟他人分享給您的架構圖；無法編輯或與 AI 對話'}
        </div>
      )}

      {/* Diagram Selector (Top Center) */}
      <div className="absolute top-4 left-1/2 -translate-x-1/2 z-50 flex items-center gap-2 bg-white/90 backdrop-blur px-4 py-2 rounded-xl shadow-[0_4px_20px_rgba(0,0,0,0.05)] border border-gray-100">
        <select
          className="bg-transparent border-none text-sm font-semibold text-gray-800 outline-none cursor-pointer focus:ring-0 w-48"
          value={currentDiagramId || ''}
          onChange={(e) => handleLoadDiagram(Number(e.target.value))}
        >
          <option value="" disabled>
            {bootstrapDone
              ? canViewOnly
                ? '-- 請選擇分享給您的架構圖 --'
                : '-- 請選擇歷史架構圖 --'
              : '載入中…'}
          </option>
          {diagrams.map((d) => (
            <option key={d.id} value={d.id}>
              {d.is_owner ? d.title : `👥 ${d.title}`} (
              {new Date(d.updated_at).toLocaleDateString()})
            </option>
          ))}
        </select>
        <div className="w-px h-4 bg-gray-200 mx-1"></div>
        <button
          onClick={handleNewDiagram}
          disabled={!canEditArch}
          className="text-gray-400 hover:text-brand-600 p-1.5 rounded-lg hover:bg-brand-50 transition-colors flex items-center justify-center disabled:opacity-30 disabled:pointer-events-none"
          title={canEditArch ? '建立新架構圖' : '僅檢視／審核無法新建'}
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2.5}
              d="M12 4v16m8-8H4"
            />
          </svg>
        </button>
        <div className="w-px h-4 bg-gray-200 mx-1"></div>
        <div
          className="flex items-center gap-2 px-2"
          title={isConnected && isShared ? '已啟用多人協作' : '目前為單機模式'}
        >
          <div
            className={`w-2.5 h-2.5 rounded-full ${
              isConnected && isShared
                ? 'bg-green-500 animate-pulse shadow-[0_0_8px_rgba(34,197,94,0.6)]'
                : 'bg-gray-300'
            }`}
          ></div>
          <span className="text-xs font-medium text-gray-500">
            {isConnected && isShared ? '協作中' : '單機模式'}
          </span>
        </div>
      </div>

      {toast?.type === 'error' && (
        <div className="absolute top-8 left-1/2 -translate-x-1/2 z-50 bg-white/90 backdrop-blur-xl border border-red-100 px-6 py-4 rounded-2xl shadow-[0_12px_40px_rgba(239,68,68,0.15)] flex flex-col gap-3 animate-[slideInDown_0.4s_ease-out] max-w-lg w-[min(92vw,28rem)]">
          <div className="flex items-center gap-4">
            <div className="w-10 h-10 bg-red-50 text-red-500 rounded-full flex items-center justify-center shrink-0">
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                />
              </svg>
            </div>
            <div className="flex-1 min-w-0">
              <span className="font-semibold text-gray-800 tracking-wide text-sm block">
                {toast.message}
              </span>
              {toast.hint && (
                <p className="text-xs text-gray-500 mt-1">{toast.hint}</p>
              )}
            </div>
            <button
              onClick={() => setToast(null)}
              className="text-gray-400 hover:text-gray-700 ml-2 p-1 rounded-md hover:bg-gray-100 transition-colors shrink-0"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
          </div>
          {toast.showCtas && (
            <div className="flex gap-2 pl-14">
              <button
                onClick={() => setToast(null)}
                className="flex-1 py-2 bg-brand-50 text-brand-700 text-xs font-bold rounded-lg hover:bg-brand-100"
              >
                於對話框重試
              </button>
              <button
                onClick={() => showComingSoon('聯絡平台架構師')}
                className="flex-1 py-2 bg-gray-100 text-gray-700 text-xs font-bold rounded-lg hover:bg-gray-200"
              >
                聯絡架構師（即將推出）
              </button>
            </div>
          )}
        </div>
      )}

      {toast?.type === 'success' && (
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 z-50 bg-white/95 backdrop-blur-2xl border border-white text-gray-900 px-10 py-8 rounded-[2rem] shadow-[0_24px_80px_rgba(37,99,235,0.15)] flex flex-col items-center gap-5 animate-[fadeInUp_0.4s_ease-out] max-w-md w-[min(92vw,24rem)]">
          <div className="relative">
            <div className="absolute inset-0 bg-green-200 rounded-full blur-xl opacity-60 animate-pulse"></div>
            <div className="w-16 h-16 bg-gradient-to-br from-green-400 to-emerald-600 text-white rounded-2xl flex items-center justify-center relative z-10 shadow-lg shadow-green-500/30">
              <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={3}
                  d="M5 13l4 4L19 7"
                />
              </svg>
            </div>
          </div>
          <div className="text-center">
            <h3 className="text-xl font-bold tracking-tight text-gray-900">
              {toast.message}
            </h3>
            <p className="text-sm text-gray-500 mt-2 font-medium">
              {toast.hint || '現在您可以對圖面進行微調。'}
            </p>
          </div>
          {toast.showCtas ? (
            <div className="flex flex-col gap-2 mt-2 w-full">
              <button
                onClick={() => setToast(null)}
                className="w-full py-3 bg-brand-50 text-brand-700 text-sm font-bold rounded-xl hover:bg-brand-100 transition-colors"
              >
                繼續對話編輯
              </button>
              <div className="flex gap-2">
                <button
                  onClick={() => showComingSoon('IaC 代碼生成')}
                  className="flex-1 py-3 bg-gradient-to-r from-brand-600 to-indigo-600 text-white text-sm font-bold rounded-xl shadow-md hover:shadow-lg transition-all"
                >
                  生成 IaC 代碼
                </button>
                <button
                  onClick={() => showComingSoon('Well-Architected 評估')}
                  className="flex-1 py-3 bg-indigo-50 text-indigo-700 text-sm font-bold rounded-xl hover:bg-indigo-100 transition-colors"
                >
                  Well-Architected
                </button>
              </div>
            </div>
          ) : (
            <button
              onClick={() => setToast(null)}
              className="w-full py-3 bg-brand-50 text-brand-700 text-sm font-bold rounded-xl hover:bg-brand-100"
            >
              關閉
            </button>
          )}
        </div>
      )}

      <ChatBox
        messages={messages}
        onGenerate={handleGenerate}
        onClearChat={handleClearChat}
        onFullReset={handleFullReset}
        isGenerating={isGenerating}
        progress={progress}
        canEdit={canEditArch}
        canReview={canReviewArch}
      />
      <DrawioCanvas
        ref={canvasRef}
        xml={xml}
        readOnly={!canEditArch}
        diagramTitle={
          currentDiagramId
            ? diagrams.find((d) => d.id === currentDiagramId)?.title || '未命名架構圖'
            : '未命名架構圖'
        }
        saveStatus={saveStatus}
        onLoadComplete={handleLoadComplete}
        onAutosave={canEditArch ? handleCanvasAutosave : undefined}
        onSaveClick={canEditArch ? handleSaveDiagram : undefined}
        onShareClick={
          canEditArch
            ? () => {
                if (!currentDiagramId) {
                  showToast('請先儲存圖表後再分享', 'error', { autoDismissMs: 4000 });
                  return;
                }
                setIsShareModalOpen(true);
              }
            : undefined
        }
        onReviewClick={
          canReviewArch
            ? () => showComingSoon('架構圖審核')
            : undefined
        }
      />

      <ShareModal
        isOpen={isShareModalOpen}
        onClose={() => setIsShareModalOpen(false)}
        diagramId={currentDiagramId}
        token={token || ''}
      />
    </div>
  );
};

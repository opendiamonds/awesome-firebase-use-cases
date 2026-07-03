import { useState } from 'react';
import { ChatBox } from '../components/ChatBox';
import type { Message } from '../components/ChatBox';
import { DrawioCanvas } from '../components/DrawioCanvas';
import { useAuth } from '../context/AuthContext';

type ToastType = 'success' | 'error' | null;

export const WorkspacePage = () => {
  const { token } = useAuth();
  const [xml, setXml] = useState<string>('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [progress, setProgress] = useState<string>('');
  const [toast, setToast] = useState<{ message: string; type: ToastType } | null>(null);
  
  const [messages, setMessages] = useState<Message[]>([
    { role: 'assistant', content: '嗨！我是您的 AI 雲端架構助理 👋\n請描述您想建立的雲端架構，例如：\n✨ 我要做一個電商網站\n✨ 我要一個包含 WAF 與 Aurora 的高可用架構' }
  ]);

  const showToast = (message: string, type: ToastType) => {
    setToast({ message, type });
    if (type === 'success') {
      setTimeout(() => setToast(null), 4000);
    }
  };

  const handleGenerate = async (prompt: string) => {
    setIsGenerating(true);
    setToast(null);
    setProgress('');
    
    const newMessages: Message[] = [...messages, { role: 'user', content: prompt }];
    setMessages(newMessages);
    
    try {
      const response = await fetch('http://localhost:8000/api/architecture/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ messages: newMessages })
      });
      
      if (!response.ok) {
        throw new Error('生成失敗');
      }

      setMessages(prev => [...prev, { role: 'assistant', content: '' }]);
      
      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      let assistantMessage = '';
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
                  setMessages(prev => {
                    const next = [...prev];
                    next[next.length - 1].content = assistantMessage;
                    return next;
                  });
                } else if (data.type === 'progress') {
                  setProgress(data.content);
                } else if (data.type === 'xml') {
                  setXml(data.content);
                  setProgress('');
                  showToast('雲端架構草圖已成功生成', 'success');
                } else if (data.type === 'error') {
                  setProgress('');
                  showToast(data.content, 'error');
                }
              } catch (e) {
                // ignore invalid JSON line
              }
            }
          }
        }
      }
    } catch (err) {
      const errMsg = err instanceof Error ? err.message : '生成失敗';
      showToast(errMsg, 'error');
    } finally {
      setIsGenerating(false);
    }
  };

  const handleLoadComplete = () => {
    showToast('雲端架構草圖已成功生成', 'success');
  };

  const handleReset = () => {
    setXml('');
    setToast(null);
    setMessages([
      { role: 'assistant', content: '嗨！我是您的 AI 雲端架構助理 👋\n請描述您想建立的雲端架構，例如：\n✨ 我要做一個電商網站\n✨ 我要一個包含 WAF 與 Aurora 的高可用架構' }
    ]);
  };

  return (
    <div className="relative flex h-full w-full overflow-hidden">
      {/* 錯誤警告 Toast (Top Center Floating) */}
      {toast?.type === 'error' && (
        <div className="absolute top-8 left-1/2 -translate-x-1/2 z-50 bg-white/90 backdrop-blur-xl border border-red-100 px-6 py-4 rounded-2xl shadow-[0_12px_40px_rgba(239,68,68,0.15)] flex items-center gap-4 animate-[slideInDown_0.4s_ease-out]">
          <div className="w-10 h-10 bg-red-50 text-red-500 rounded-full flex items-center justify-center shrink-0">
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>
          <span className="font-semibold text-gray-800 tracking-wide text-sm">{toast.message}</span>
          <button 
            onClick={() => setToast(null)}
            className="text-gray-400 hover:text-gray-700 ml-2 p-1 rounded-md hover:bg-gray-100 transition-colors"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" /></svg>
          </button>
        </div>
      )}

      {/* 成功提示 Toast (Center Modal Style) */}
      {toast?.type === 'success' && (
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 z-50 bg-white/95 backdrop-blur-2xl border border-white text-gray-900 px-10 py-8 rounded-[2rem] shadow-[0_24px_80px_rgba(37,99,235,0.15)] flex flex-col items-center gap-5 animate-[fadeInUp_0.4s_ease-out]">
          <div className="relative">
            <div className="absolute inset-0 bg-green-200 rounded-full blur-xl opacity-60 animate-pulse"></div>
            <div className="w-16 h-16 bg-gradient-to-br from-green-400 to-emerald-600 text-white rounded-2xl flex items-center justify-center relative z-10 shadow-lg shadow-green-500/30">
              <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
              </svg>
            </div>
          </div>
          <div className="text-center">
            <h3 className="text-xl font-bold tracking-tight text-gray-900">{toast.message}</h3>
            <p className="text-sm text-gray-500 mt-2 font-medium">現在您可以對圖面進行微調，或直接匯出代碼。</p>
          </div>
          <div className="flex gap-3 mt-4 w-full">
            <button 
              onClick={() => setToast(null)}
              className="flex-1 py-3 bg-brand-50 text-brand-700 text-sm font-bold rounded-xl hover:bg-brand-100 transition-colors"
            >
              繼續對話編輯
            </button>
            <button className="flex-1 py-3 bg-gradient-to-r from-brand-600 to-indigo-600 text-white text-sm font-bold rounded-xl shadow-md hover:shadow-lg hover:shadow-brand-500/20 transition-all hover:-translate-y-0.5">
              生成 IaC 代碼
            </button>
          </div>
        </div>
      )}

      {/* Main Content Area */}
      <ChatBox 
        messages={messages}
        onGenerate={handleGenerate} 
        onReset={handleReset} 
        isGenerating={isGenerating} 
        progress={progress}
      />
      <DrawioCanvas xml={xml} onLoadComplete={handleLoadComplete} />
    </div>
  );
};

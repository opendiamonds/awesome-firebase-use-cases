import { useState, useRef, useEffect } from 'react';

export interface Message {
  role: 'user' | 'assistant';
  content: string;
}

interface ChatBoxProps {
  messages: Message[];
  onGenerate: (prompt: string) => Promise<void>;
  /** A4：只清對話、保留畫布 */
  onClearChat: () => void;
  /** A1：全部重置（畫布 + 對話） */
  onFullReset: () => void;
  isGenerating: boolean;
  progress: string;
  /** 無編輯權時唯讀（可看對話、不可送出） */
  canEdit?: boolean;
  /** 有審核權時顯示審核提示（不可編輯時） */
  canReview?: boolean;
}

export const ChatBox = ({
  messages,
  onGenerate,
  onClearChat,
  onFullReset,
  isGenerating,
  progress,
  canEdit = true,
  canReview = false,
}: ChatBoxProps) => {
  const [prompt, setPrompt] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!canEdit || !prompt.trim() || isGenerating) return;
    onGenerate(prompt);
    setPrompt('');
  };

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = Math.min(textareaRef.current.scrollHeight, 120) + 'px';
    }
  }, [prompt]);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isGenerating]);

  return (
    <div className="flex flex-col h-full bg-[#fcfdff] border-r border-gray-200/60 w-[420px] relative z-10 shadow-[8px_0_30px_rgba(0,0,0,0.015)]">
      {/* Header */}
      <div className="h-20 flex items-center justify-between px-8 border-b border-gray-100 bg-white/80 backdrop-blur-md shrink-0">
        <div>
          <h2 className="text-[17px] font-bold text-gray-900 tracking-tight">AI 架構助理</h2>
          <p className="text-xs text-gray-500 mt-0.5 font-medium">多角色協同設計與自然語言建模</p>
        </div>
        <div className="flex items-center gap-2">
          {canEdit && (
            <>
              <button
                onClick={onClearChat}
                className="text-xs font-bold text-brand-600 hover:text-white hover:bg-brand-600 px-3 py-2 rounded-full border border-brand-100 transition-all duration-300 shadow-sm hover:shadow-brand-500/20"
                title="清空此架構圖的對話紀錄（不會刪除架構圖）"
              >
                清空對話
              </button>
              <button
                onClick={onFullReset}
                className="text-xs font-bold text-gray-600 hover:text-white hover:bg-gray-700 px-3 py-2 rounded-full border border-gray-200 transition-all duration-300"
                title="清空畫布與對話（全部重置）"
              >
                全部重置
              </button>
            </>
          )}
        </div>
      </div>

      {/* Chat History Area */}
      <div ref={scrollRef} className="flex-1 p-8 overflow-y-auto bg-transparent scroll-smooth">
        {messages.map((msg, idx) => (
          <div key={idx} className={`flex gap-4 mb-8 group ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
            
            {/* Avatar */}
            <div className={`w-9 h-9 rounded-full flex items-center justify-center shrink-0 shadow-md ${
              msg.role === 'assistant' 
                ? 'bg-gradient-to-br from-brand-500 to-indigo-600 shadow-brand-500/20' 
                : 'bg-gradient-to-br from-gray-700 to-gray-900 shadow-gray-900/20'
            }`}>
              {msg.role === 'assistant' ? (
                <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              ) : (
                <span className="text-white text-xs font-bold">Ian</span>
              )}
            </div>

            {/* Bubble */}
            <div className={`flex-1 bg-white border border-gray-100 shadow-[0_4px_20px_rgba(0,0,0,0.03)] p-5 text-[14px] leading-relaxed transition-all duration-300 hover:shadow-[0_8px_30px_rgba(0,0,0,0.06)] ${
              msg.role === 'assistant' 
                ? 'rounded-2xl rounded-tl-none text-gray-700' 
                : 'rounded-2xl rounded-tr-none text-gray-800 bg-brand-50/30'
            }`}>
              <p className="whitespace-pre-wrap">{msg.content}</p>
            </div>
          </div>
        ))}
        
        {isGenerating && (
          <div className="flex gap-4 mb-8">
            <div className="w-9 h-9 rounded-full bg-gradient-to-br from-brand-500 to-indigo-600 flex items-center justify-center shrink-0 shadow-md shadow-brand-500/20">
              <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <div className="bg-white border border-gray-100 shadow-[0_4px_20px_rgba(0,0,0,0.03)] rounded-2xl rounded-tl-none p-5 flex gap-2 items-center">
              {progress ? (
                <div className="flex items-center gap-2 text-[14px] text-brand-600 font-medium tracking-wide">
                  <svg className="animate-spin w-4 h-4 text-brand-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  {progress}
                </div>
              ) : (
                <>
                  <div className="w-2 h-2 bg-brand-500 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-brand-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  <div className="w-2 h-2 bg-brand-500 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
                </>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Input Area */}
      <div className="p-6 bg-white border-t border-gray-100 shadow-[0_-10px_40px_rgba(0,0,0,0.02)]">
        {!canEdit && (
          <div className="mb-3 text-center text-xs font-semibold text-amber-700 bg-amber-50 border border-amber-100 rounded-xl px-3 py-2">
            {canReview
              ? '審核模式：可檢視對話紀錄，無法與 AI 對話或修改架構圖'
              : '僅檢視：無法與 AI 對話或編輯架構圖'}
          </div>
        )}
        <form onSubmit={handleSubmit} className="relative group">
          <div className="absolute -inset-0.5 bg-gradient-to-r from-brand-500 to-indigo-500 rounded-2xl opacity-0 group-hover:opacity-20 transition duration-500 blur"></div>
          <div className="relative flex items-end bg-white border border-gray-200/80 rounded-2xl shadow-sm focus-within:ring-2 focus-within:ring-brand-500/20 focus-within:border-brand-500 transition-all duration-300 p-2">
            <textarea
              ref={textareaRef}
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              onKeyDown={(e) => { if(e.key === 'Enter' && (e.metaKey || e.ctrlKey)) { e.preventDefault(); handleSubmit(e); } }}
              placeholder={
                canEdit
                  ? '輸入您的架構需求... (Ctrl+Enter 或 Cmd+Enter 送出)'
                  : '唯讀模式：無法送出產圖請求'
              }
              className="w-full max-h-[120px] pl-3 pr-2 py-2 bg-transparent text-gray-900 text-[14px] resize-none focus:outline-none placeholder:text-gray-400 min-h-[44px]"
              rows={1}
              disabled={isGenerating || !canEdit}
            />
            <button
              type="submit"
              disabled={!canEdit || !prompt.trim() || isGenerating}
              className={`p-2.5 shrink-0 rounded-xl transition-all duration-300 ${
                !canEdit || !prompt.trim() || isGenerating 
                  ? 'bg-gray-100 text-gray-300 cursor-not-allowed' 
                  : 'bg-gradient-to-br from-brand-600 to-indigo-600 text-white shadow-md shadow-brand-500/30 hover:shadow-lg hover:shadow-brand-500/40 hover:-translate-y-0.5'
              }`}
            >
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
              </svg>
            </button>
          </div>
        </form>
        <div className="text-center mt-3 text-[11px] text-gray-400">
          AI 可能會產生錯誤資訊，請自行核對圖面細節。
        </div>
      </div>
    </div>
  );
};

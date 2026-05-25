import { useEffect, useRef } from 'react';

interface DrawioCanvasProps {
  xml: string;
}

export const DrawioCanvas = ({ xml }: DrawioCanvasProps) => {
  const iframeRef = useRef<HTMLIFrameElement>(null);

  useEffect(() => {
    if (xml && iframeRef.current) {
      const message = JSON.stringify({
        action: 'load',
        autosave: 1,
        xml: xml
      });
      iframeRef.current.contentWindow?.postMessage(message, '*');
    }
  }, [xml]);

  return (
    <div className="flex-1 flex flex-col h-full bg-[#f1f5f9] relative">
      
      {/* Top Toolbar */}
      <div className="h-20 bg-white/80 backdrop-blur-md border-b border-gray-200/60 flex items-center justify-between px-8 shrink-0 z-10 shadow-sm">
        <div className="flex items-center gap-4">
          <div className="p-2 bg-gray-100 rounded-lg text-gray-500">
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 5a1 1 0 011-1h14a1 1 0 011 1v2a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM4 13a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H5a1 1 0 01-1-1v-6zM16 13a1 1 0 011-1h2a1 1 0 011 1v6a1 1 0 01-1 1h-2a1 1 0 01-1-1v-6z" />
            </svg>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-lg font-bold text-gray-900 tracking-tight">電商網站架構 v1.0</h1>
              <span className="px-2 py-0.5 text-[10px] font-bold tracking-wider uppercase bg-amber-50 text-amber-600 rounded-full border border-amber-200/50">未儲存</span>
            </div>
            <p className="text-xs text-gray-500 mt-0.5 font-medium">最後更新：剛剛</p>
          </div>
        </div>
        
        <div className="flex items-center gap-3">
          <button className="flex items-center justify-center w-10 h-10 text-gray-400 hover:text-gray-700 hover:bg-gray-100 rounded-xl transition-all duration-200">
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h10a8 8 0 018 8v2M3 10l6 6m-6-6l6-6" />
            </svg>
          </button>
          <button className="flex items-center justify-center w-10 h-10 text-gray-400 hover:text-gray-700 hover:bg-gray-100 rounded-xl transition-all duration-200">
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" />
            </svg>
          </button>
          <div className="w-px h-6 bg-gray-200 mx-2"></div>
          <button className="px-5 py-2.5 bg-gray-900 hover:bg-black text-white text-sm font-semibold rounded-xl shadow-md hover:shadow-xl hover:-translate-y-0.5 transition-all duration-300">
            儲存架構圖
          </button>
        </div>
      </div>

      {/* Canvas Area */}
      <div className="flex-1 p-8 overflow-hidden">
        <div className="w-full h-full bg-white rounded-3xl shadow-[0_12px_60px_-15px_rgba(0,0,0,0.05)] border border-gray-200/50 overflow-hidden relative group">
          {!xml ? (
            <div className="absolute inset-0 flex items-center justify-center bg-gray-50/50 flex-col gap-6">
              <div className="relative">
                <div className="absolute inset-0 bg-brand-200 rounded-full blur-xl opacity-50 animate-pulse"></div>
                <div className="w-20 h-20 bg-white rounded-3xl shadow-lg border border-gray-100 flex items-center justify-center relative z-10">
                  <svg className="w-10 h-10 text-brand-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                </div>
              </div>
              <p className="text-gray-500 font-medium text-sm tracking-wide">請在左側輸入需求以生成架構草圖</p>
            </div>
          ) : (
            <iframe
              ref={iframeRef}
              className="w-full h-full border-0"
              src="https://embed.diagrams.net/?embed=1&ui=min&spin=1&modified=unsaved&proto=json"
              title="draw.io diagram"
            />
          )}
        </div>
      </div>

    </div>
  );
};

import type { ReactNode } from 'react';
import { Sidebar } from './Sidebar';

interface LayoutProps {
  children: ReactNode;
}

export const Layout = ({ children }: LayoutProps) => {
  return (
    <div className="flex h-screen w-full bg-gray-50 overflow-hidden font-sans">
      <Sidebar />
      {/* min-h-0 + overflow-y-auto：Admin／矩陣頁可用滾輪看完整內容 */}
      <div className="flex-1 flex flex-col min-w-0 min-h-0 overflow-y-auto overflow-x-hidden">
        {children}
      </div>
    </div>
  );
};

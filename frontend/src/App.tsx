import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { ProtectedRoute, AdminRoute } from './components/RouteGuard';
import { Layout } from './components/Layout';

// Pages
import { LoginPage } from './pages/LoginPage';
import { WorkspacePage } from './pages/WorkspacePage';
import { AdminPage } from './pages/AdminPage';
import { ForbiddenPage } from './pages/ForbiddenPage';

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          {/* 1. 公開路由 */}
          <Route path="/login" element={<LoginPage />} />
          <Route path="/403" element={<ForbiddenPage />} />

          {/* 2. 受保護路由 (Workspace Page) */}
          <Route 
            path="/workspace" 
            element={
              <ProtectedRoute>
                <Layout>
                  <WorkspacePage />
                </Layout>
              </ProtectedRoute>
            } 
          />

          {/* 3. 受保護路由 (Admin Panel) */}
          <Route 
            path="/admin" 
            element={
              <ProtectedRoute>
                <AdminRoute>
                  <Layout>
                    <AdminPage />
                  </Layout>
                </AdminRoute>
              </ProtectedRoute>
            } 
          />

          {/* 4. 根目錄自動轉向 */}
          <Route path="/" element={<Navigate to="/workspace" replace />} />
          <Route path="*" element={<Navigate to="/workspace" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;

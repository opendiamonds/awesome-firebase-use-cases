import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { ProtectedRoute, CapabilityRoute } from './components/RouteGuard';
import { Layout } from './components/Layout';

import { LoginPage } from './pages/LoginPage';
import { WorkspacePage } from './pages/WorkspacePage';
import { AdminPage } from './pages/AdminPage';
import { RolePermissionsPage } from './pages/RolePermissionsPage';
import { ForbiddenPage } from './pages/ForbiddenPage';

/** 依權限導向第一個可用頁；皆無則 403 */
const DefaultRedirect: React.FC = () => {
  const { canArch, can, isLoading } = useAuth();
  if (isLoading) return null;
  if (canArch('view')) return <Navigate to="/workspace" replace />;
  if (can('J3a', 'view')) return <Navigate to="/admin/users" replace />;
  if (can('J3b', 'view')) return <Navigate to="/admin/role-permissions" replace />;
  return <Navigate to="/403" replace />;
};

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/403" element={<ForbiddenPage />} />

          <Route
            path="/workspace"
            element={
              <ProtectedRoute>
                <CapabilityRoute storyId="A1" action="view">
                  <Layout>
                    <WorkspacePage />
                  </Layout>
                </CapabilityRoute>
              </ProtectedRoute>
            }
          />

          <Route
            path="/admin/users"
            element={
              <ProtectedRoute>
                <CapabilityRoute storyId="J3a" action="view">
                  <Layout>
                    <AdminPage />
                  </Layout>
                </CapabilityRoute>
              </ProtectedRoute>
            }
          />

          <Route
            path="/admin/role-permissions"
            element={
              <ProtectedRoute>
                <CapabilityRoute storyId="J3b" action="view">
                  <Layout>
                    <RolePermissionsPage />
                  </Layout>
                </CapabilityRoute>
              </ProtectedRoute>
            }
          />

          <Route path="/admin" element={<Navigate to="/admin/users" replace />} />
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <DefaultRedirect />
              </ProtectedRoute>
            }
          />
          <Route
            path="*"
            element={
              <ProtectedRoute>
                <DefaultRedirect />
              </ProtectedRoute>
            }
          />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;

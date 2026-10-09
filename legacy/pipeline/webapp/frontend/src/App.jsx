import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AuthProvider } from "./hooks/useCurrentUser";
import { ToastProvider } from "./components/ToastProvider";
import { Layout } from "./components/Layout";
import { ProtectedRoute, AdminRoute } from "./components/ProtectedRoute";
import { LoginPage } from "./routes/LoginPage";
import { MatchFlowPage } from "./routes/MatchFlowPage";
import { AdminDashboardPage } from "./routes/AdminDashboardPage";
import { TasksPage } from "./routes/TasksPage";
import { CourtTaskPage } from "./routes/CourtTaskPage";

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <ToastProvider>
          <Routes>
            <Route path="/login" element={<LoginPage />} />

            <Route element={<ProtectedRoute />}>
              <Route element={<Layout subtitle="Upload, process, correct" />}>
                <Route path="/" element={<MatchFlowPage />} />
                <Route path="/tasks" element={<TasksPage />} />
                <Route path="/court-task/:jobId" element={<CourtTaskPage />} />
              </Route>
            </Route>

            <Route element={<AdminRoute />}>
              <Route element={<Layout subtitle="Admin dashboard" />}>
                <Route path="/admin" element={<AdminDashboardPage />} />
              </Route>
            </Route>
          </Routes>
        </ToastProvider>
      </AuthProvider>
    </BrowserRouter>
  );
}

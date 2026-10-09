import { Navigate, Outlet } from "react-router-dom";
import { useCurrentUser } from "../hooks/useCurrentUser";

export function ProtectedRoute() {
  const { user, loading } = useCurrentUser();
  if (loading) return null;
  if (!user) return <Navigate to="/login" replace />;
  return <Outlet />;
}

export function AdminRoute() {
  const { user, loading } = useCurrentUser();
  if (loading) return null;
  if (!user) return <Navigate to="/login" replace />;
  if (user.role !== "admin") return <Navigate to="/" replace />;
  return <Outlet />;
}

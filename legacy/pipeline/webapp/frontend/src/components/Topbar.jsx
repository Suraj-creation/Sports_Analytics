import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useCurrentUser } from "../hooks/useCurrentUser";
import { ChangePasswordModal } from "./ChangePasswordModal";

export function Topbar({ subtitle }) {
  const { user, logout } = useCurrentUser();
  const navigate = useNavigate();
  const [pwOpen, setPwOpen] = useState(false);

  async function handleLogout() {
    await logout();
    navigate("/login");
  }

  return (
    <div className="topbar">
      <div className="topbar-inner">
        <div className="brand">
          <div className="brand-mark">
            <svg viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="2">
              <circle cx="12" cy="12" r="9" />
              <path d="M12 3v18M3 12h18" />
            </svg>
          </div>
          <div>
            <div className="brand-name">Rally Review</div>
            <div className="brand-sub">{subtitle}</div>
          </div>
        </div>
        {user && (
          <div className="topbar-user">
            <Link to={user.role === "admin" ? "/admin" : "/tasks"}>
              {user.role === "admin" ? "Admin" : "My tasks"}
            </Link>
            <span className="role-pill">{user.role}</span>
            <span>{user.username}</span>
            <a href="#" onClick={(e) => { e.preventDefault(); setPwOpen(true); }}>
              Change password
            </a>
            <a href="#" onClick={(e) => { e.preventDefault(); handleLogout(); }}>
              Log out
            </a>
          </div>
        )}
      </div>
      <ChangePasswordModal open={pwOpen} onClose={() => setPwOpen(false)} />
    </div>
  );
}

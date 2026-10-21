import { Outlet } from "react-router-dom";
import { Topbar } from "./Topbar";

export function Layout({ subtitle }) {
  return (
    <>
      <Topbar subtitle={subtitle} />
      <div className="app">
        <Outlet />
      </div>
    </>
  );
}

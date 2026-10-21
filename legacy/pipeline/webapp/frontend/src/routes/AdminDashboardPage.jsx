import { useState } from "react";
import { JobsTable } from "../features/admin/JobsTable";
import { BatchUploadForm } from "../features/admin/BatchUploadForm";
import { UsersPanel } from "../features/admin/UsersPanel";
import "../features/admin/admin.css";

export function AdminDashboardPage() {
  const [interns, setInterns] = useState([]);

  return (
    <div>
      <div className="hero-row" style={{ padding: "32px 0 20px" }}>
        <p className="eyebrow" style={{
          fontFamily: "var(--font-head)", fontSize: 11.5, fontWeight: 800,
          letterSpacing: "0.12em", textTransform: "uppercase", color: "var(--court)", margin: "0 0 8px",
        }}>Admin</p>
        <h1 style={{ fontFamily: "var(--font-head)", fontWeight: 800, fontSize: 24, margin: 0 }}>All jobs</h1>
      </div>

      {/* JobsTable polls every 2s on its own, so a fresh batch upload
          shows up shortly without needing an explicit refresh trigger. */}
      <BatchUploadForm onUploaded={() => {}} />
      <JobsTable interns={interns} />
      <UsersPanel onInternsChanged={setInterns} />
    </div>
  );
}

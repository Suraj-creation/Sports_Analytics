import { useState } from "react";
import { usePolling } from "../hooks/usePolling";
import { apiGet, apiPostJson } from "../lib/api";
import { useToast } from "../components/ToastProvider";
import { ReasonDialog } from "../components/ReasonDialog";
import { TaskList } from "../features/tasks/TaskList";
import "../features/tasks/tasks.css";

export function TasksPage() {
  const { data } = usePolling(() => apiGet("/api/my-tasks"), { intervalMs: 5000 });
  const [flagTarget, setFlagTarget] = useState(null); // { id, kind }
  const showToast = useToast();

  async function handleFlagSubmit(reason) {
    const { id, kind } = flagTarget;
    const url = kind === "court" ? `/api/court-task/${id}/flag` : `/api/jobs/${id}/flag-review`;
    try {
      await apiPostJson(url, { reason });
      showToast("Flagged for the admin");
    } catch (err) {
      showToast("Couldn't flag this task: " + err.message, true);
    } finally {
      setFlagTarget(null);
    }
  }

  return (
    <div>
      <div className="hero-row" style={{ padding: "32px 0 20px" }}>
        <p className="eyebrow" style={{
          fontFamily: "var(--font-head)", fontSize: 11.5, fontWeight: 800,
          letterSpacing: "0.12em", textTransform: "uppercase", color: "var(--court)", margin: "0 0 8px",
        }}>Assigned to you</p>
        <h1 style={{ fontFamily: "var(--font-head)", fontWeight: 800, fontSize: 24, margin: 0 }}>My tasks</h1>
      </div>

      <TaskList title="Court annotation" items={data?.court_tasks || []} kind="court"
                onFlag={(t) => setFlagTarget({ id: t.id, kind: "court" })} />
      <TaskList title="Review" items={data?.review_tasks || []} kind="review"
                onFlag={(t) => setFlagTarget({ id: t.id, kind: "review" })} />

      <ReasonDialog
        open={!!flagTarget}
        title="Can't complete this task"
        prompt="What's blocking this task? The admin will see this and reassign it."
        onSubmit={handleFlagSubmit}
        onCancel={() => setFlagTarget(null)}
      />
    </div>
  );
}

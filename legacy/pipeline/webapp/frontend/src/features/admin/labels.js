export const PIPELINE_LABEL = {
  pending_court_task: ["pill-amber", "Awaiting court task"],
  queued: ["pill-slate", "Queued"],
  running: ["pill-slate", "Running"],
  done: ["pill-court", "Done"],
  failed: ["pill-coral", "Failed"],
  cancelled: ["pill-slate", "Cancelled"],
};

export const TASK_LABEL = {
  not_needed: ["pill-slate", "Not needed"],
  not_ready: ["pill-slate", "Not ready"],
  extracting: ["pill-amber", "Extracting frames"],
  extraction_failed: ["pill-coral", "Extraction failed"],
  pending: ["pill-amber", "Pending"],
  in_progress: ["pill-amber", "In progress"],
  flagged: ["pill-coral", "Flagged -- needs attention"],
  submitted: ["pill-court", "Submitted"],
};

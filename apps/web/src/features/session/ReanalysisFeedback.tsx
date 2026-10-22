export function ReanalysisFeedback({
  accepted,
  sessionDetail,
  liveDetail,
}: {
  accepted: boolean;
  sessionDetail?: string | null;
  liveDetail?: string | null;
}) {
  const failure = [liveDetail, sessionDetail].find((detail) =>
    detail?.startsWith("Reanalysis could not start;"),
  );
  if (failure)
    return (
      <p role="alert" className="analysis-notice mt-5 text-alert">
        {failure}
      </p>
    );
  if (accepted)
    return (
      <p role="status" className="analysis-notice mt-5">
        Reanalysis requested. Processing status will update when it starts.
      </p>
    );
  return null;
}

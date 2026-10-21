export function ReportCard({ reportText, reportPdfUrl }) {
  if (!reportText) return null;
  return (
    <div className="card">
      <div className="card-head">
        <h2>Match Report</h2>
        {reportPdfUrl && (
          <a className="btn btn-sm" href={reportPdfUrl} target="_blank" rel="noreferrer" style={{ textDecoration: "none" }}>
            Download PDF
          </a>
        )}
      </div>
      <div className="report-text">{reportText}</div>
    </div>
  );
}

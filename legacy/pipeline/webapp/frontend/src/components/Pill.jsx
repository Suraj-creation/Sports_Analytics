export function Pill({ map, statusKey }) {
  const [cls, label] = map[statusKey] || ["pill-slate", statusKey || "--"];
  return <span className={`pill ${cls}`}>{label}</span>;
}

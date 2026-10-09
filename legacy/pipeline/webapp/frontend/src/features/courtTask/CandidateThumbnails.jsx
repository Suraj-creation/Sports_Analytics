export function CandidateThumbnails({ candidates, selectedIdx, onSelect }) {
  return (
    <div className="candidates-row">
      {candidates.map((c, i) => (
        <img
          key={i}
          src={c.image_url}
          className={"cand-thumb" + (i === selectedIdx ? " active" : "")}
          onClick={() => onSelect(i)}
          title={`Frame ${c.frame_no} (score ${c.score})`}
          alt={`Candidate frame ${i + 1}`}
        />
      ))}
    </div>
  );
}

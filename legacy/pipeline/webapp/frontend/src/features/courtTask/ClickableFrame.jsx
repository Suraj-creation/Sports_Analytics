import { useRef } from "react";

/* Ported from analysis/annotate_court.py's embedded click UI: click
   handler computes image-native pixel coords via getBoundingClientRect()
   + a scale factor (displayed size vs the candidate's true width/height),
   so submitted points are always in the original frame's pixel space
   regardless of how large the browser renders the image. */
export function ClickableFrame({ src, width, height, points, colors, labels, onClick }) {
  const imgRef = useRef(null);

  function handleClick(e) {
    if (points.length >= labels.length) return;
    const rect = imgRef.current.getBoundingClientRect();
    const scaleX = width / rect.width;
    const scaleY = height / rect.height;
    const x = Math.round((e.clientX - rect.left) * scaleX);
    const y = Math.round((e.clientY - rect.top) * scaleY);
    const px = ((e.clientX - rect.left) / rect.width) * 100;
    const py = ((e.clientY - rect.top) / rect.height) * 100;
    onClick([x, y], [px, py]);
  }

  return (
    <div style={{ position: "relative", display: "inline-block", maxWidth: "100%", background: "#000" }}>
      <img ref={imgRef} src={src} onClick={handleClick}
           style={{ display: "block", maxWidth: "100%", cursor: "crosshair" }} alt="Court frame to annotate" />
      {points.map((p, i) => (
        <div key={i} style={{
          position: "absolute", left: `${p.px}%`, top: `${p.py}%`, transform: "translate(-50%,-50%)",
          width: 16, height: 16, borderRadius: "50%", border: "2px solid #fff",
          fontSize: 9, fontWeight: "bold", color: "#000", display: "flex",
          alignItems: "center", justifyContent: "center", pointerEvents: "none",
          background: colors[i],
        }}>
          {labels[i]}
        </div>
      ))}
    </div>
  );
}

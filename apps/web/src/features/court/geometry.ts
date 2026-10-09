import { COURT_LINES, HALF, LENGTH, NET, WIDTH_DOUBLES } from "@/lib/court";

/** Margin of floor drawn around the doubles court, metres. */
export const MARGIN_M = 0.7;

/**
 * Top-down court laid out horizontally: the near end (court y < 0) on the left, the far end on
 * the right; seen from the near baseline, the court's left side (x < 0) is at the top.
 */
export class CourtView {
  readonly scale: number;
  readonly height: number;

  constructor(
    readonly width: number,
    readonly pad = 8,
  ) {
    this.scale = (width - 2 * pad) / (LENGTH + 2 * MARGIN_M);
    this.height = Math.round(2 * pad + (WIDTH_DOUBLES + 2 * MARGIN_M) * this.scale);
  }

  /** court metres → CSS pixels */
  map(x: number, y: number): [number, number] {
    return [
      this.pad + (y + HALF + MARGIN_M) * this.scale,
      this.pad + (x + WIDTH_DOUBLES / 2 + MARGIN_M) * this.scale,
    ];
  }

  /** CSS pixels → court metres (inverse of map) */
  unmap(px: number, py: number): [number, number] {
    return [
      (py - this.pad) / this.scale - WIDTH_DOUBLES / 2 - MARGIN_M,
      (px - this.pad) / this.scale - HALF - MARGIN_M,
    ];
  }

  drawCourt(g: CanvasRenderingContext2D, opts: { floor?: string; lines?: string } = {}): void {
    const [x0, y0] = this.map(-WIDTH_DOUBLES / 2, -HALF);
    const [x1, y1] = this.map(WIDTH_DOUBLES / 2, HALF);
    g.fillStyle = opts.floor ?? "#14382f";
    g.fillRect(Math.min(x0, x1), Math.min(y0, y1), Math.abs(x1 - x0), Math.abs(y1 - y0));
    g.strokeStyle = opts.lines ?? "rgba(232,239,234,0.55)";
    g.lineWidth = 1;
    g.beginPath();
    for (const [a, b] of COURT_LINES) {
      const pa = this.map(a[0], a[1]);
      const pb = this.map(b[0], b[1]);
      g.moveTo(Math.round(pa[0]) + 0.5, Math.round(pa[1]) + 0.5);
      g.lineTo(Math.round(pb[0]) + 0.5, Math.round(pb[1]) + 0.5);
    }
    g.stroke();
    const na = this.map(NET[0][0] - 0.25, NET[0][1]);
    const nb = this.map(NET[1][0] + 0.25, NET[1][1]);
    g.strokeStyle = "rgba(232,239,234,0.9)";
    g.lineWidth = 2;
    g.beginPath();
    g.moveTo(na[0], na[1]);
    g.lineTo(nb[0], nb[1]);
    g.stroke();
  }
}

/** Size a canvas for the device pixel ratio and return a context drawing in CSS pixels. */
export function prepareCanvas(c: HTMLCanvasElement, w: number, h: number): CanvasRenderingContext2D | null {
  const dpr = window.devicePixelRatio || 1;
  const W = Math.round(w * dpr);
  const H = Math.round(h * dpr);
  if (c.width !== W || c.height !== H) {
    c.width = W;
    c.height = H;
  }
  const g = c.getContext("2d");
  if (!g) return null;
  g.setTransform(dpr, 0, 0, dpr, 0, 0);
  g.clearRect(0, 0, w, h);
  return g;
}

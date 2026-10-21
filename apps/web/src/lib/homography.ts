import { project } from "./court";

type P = [number, number];

/**
 * Least-squares DLT homography court → image from ≥4 correspondences (h33 = 1). Used for the
 * live preview while placing points; the server refits with its own solver on save.
 * Image coordinates are normalised by `scale` for conditioning, then folded back into H.
 */
export function fitHomography(court: P[], image: P[]): number[][] | null {
  const n = court.length;
  if (n < 4 || image.length !== n) return null;
  const s = Math.max(1, ...image.flatMap(([u, v]) => [Math.abs(u), Math.abs(v)]));
  const A: number[][] = [];
  const b: number[] = [];
  for (let i = 0; i < n; i++) {
    const [x, y] = court[i] as P;
    const u = (image[i] as P)[0] / s;
    const v = (image[i] as P)[1] / s;
    A.push([x, y, 1, 0, 0, 0, -x * u, -y * u]);
    b.push(u);
    A.push([0, 0, 0, x, y, 1, -x * v, -y * v]);
    b.push(v);
  }
  // normal equations (AᵀA) h = Aᵀb
  const M: number[][] = Array.from({ length: 8 }, () => new Array<number>(9).fill(0));
  for (let r = 0; r < A.length; r++) {
    const row = A[r] as number[];
    for (let i = 0; i < 8; i++) {
      const Mi = M[i] as number[];
      for (let j = 0; j < 8; j++) Mi[j] = (Mi[j] as number) + (row[i] as number) * (row[j] as number);
      Mi[8] = (Mi[8] as number) + (row[i] as number) * (b[r] as number);
    }
  }
  const h = solve(M);
  if (!h) return null;
  const H = [
    [(h[0] as number) * s, (h[1] as number) * s, (h[2] as number) * s],
    [(h[3] as number) * s, (h[4] as number) * s, (h[5] as number) * s],
    [h[6] as number, h[7] as number, 1],
  ];
  return H.flat().every(Number.isFinite) ? H : null;
}

/** Gaussian elimination with partial pivoting on an n×(n+1) augmented matrix. */
function solve(M: number[][]): number[] | null {
  const n = M.length;
  for (let c = 0; c < n; c++) {
    let p = c;
    for (let r = c + 1; r < n; r++)
      if (Math.abs((M[r] as number[])[c] as number) > Math.abs((M[p] as number[])[c] as number)) p = r;
    const pivot = (M[p] as number[])[c] as number;
    if (Math.abs(pivot) < 1e-12) return null;
    [M[c], M[p]] = [M[p] as number[], M[c] as number[]];
    const Mc = M[c] as number[];
    for (let r = 0; r < n; r++) {
      if (r === c) continue;
      const Mr = M[r] as number[];
      const f = (Mr[c] as number) / (Mc[c] as number);
      if (f === 0) continue;
      for (let k = c; k <= n; k++) Mr[k] = (Mr[k] as number) - f * (Mc[k] as number);
    }
  }
  return M.map((row, i) => (row[n] as number) / (row[i] as number));
}

/** RMS reprojection error in pixels. */
export function reprojectionError(H: number[][], court: P[], image: P[]): number {
  let sum = 0;
  for (let i = 0; i < court.length; i++) {
    const [u, v] = project(H, court[i] as P);
    const [iu, iv] = image[i] as P;
    sum += (u - iu) ** 2 + (v - iv) ** 2;
  }
  return Math.sqrt(sum / Math.max(1, court.length));
}

// Court model in metres (mirrors sports/badminton/src/bai_badminton/court.py).
// Origin at the centre of the net; x across (left→right seen from the near end), y along
// (y < 0 near half, y > 0 far half).

export const LENGTH = 13.4;
export const WIDTH_DOUBLES = 6.1;
export const WIDTH_SINGLES = 5.18;
export const HALF = LENGTH / 2;
export const SHORT_SERVICE = 1.98;
export const LONG_SERVICE_INSET = 0.76;

type P = [number, number];
const hw = WIDTH_DOUBLES / 2;
const sw = WIDTH_SINGLES / 2;

export const COURT_LINES: [P, P][] = [
  [
    [-hw, -HALF],
    [hw, -HALF],
  ],
  [
    [-hw, HALF],
    [hw, HALF],
  ],
  [
    [-hw, -HALF],
    [-hw, HALF],
  ],
  [
    [hw, -HALF],
    [hw, HALF],
  ],
  [
    [-sw, -HALF],
    [-sw, HALF],
  ],
  [
    [sw, -HALF],
    [sw, HALF],
  ],
  [
    [-hw, -SHORT_SERVICE],
    [hw, -SHORT_SERVICE],
  ],
  [
    [-hw, SHORT_SERVICE],
    [hw, SHORT_SERVICE],
  ],
  [
    [-hw, -(HALF - LONG_SERVICE_INSET)],
    [hw, -(HALF - LONG_SERVICE_INSET)],
  ],
  [
    [-hw, HALF - LONG_SERVICE_INSET],
    [hw, HALF - LONG_SERVICE_INSET],
  ],
  [
    [0, -HALF],
    [0, -SHORT_SERVICE],
  ],
  [
    [0, SHORT_SERVICE],
    [0, HALF],
  ],
];
export const NET: [P, P] = [
  [-hw, 0],
  [hw, 0],
];

/** Apply a 3×3 homography (court → image) to a court point. */
export function project(H: number[][], [x, y]: P): P {
  const r0 = H[0] as number[];
  const r1 = H[1] as number[];
  const r2 = H[2] as number[];
  const w = (r2[0] as number) * x + (r2[1] as number) * y + (r2[2] as number);
  return [
    ((r0[0] as number) * x + (r0[1] as number) * y + (r0[2] as number)) / w,
    ((r1[0] as number) * x + (r1[1] as number) * y + (r1[2] as number)) / w,
  ];
}

/** Calibration reference points the user can click (names match the backend). */
export const REFERENCE_ORDER = [
  "far_left",
  "far_right",
  "near_right",
  "near_left",
  "net_left",
  "net_right",
] as const;
export const REFERENCE_LABEL: Record<string, string> = {
  far_left: "Far left corner",
  far_right: "Far right corner",
  near_right: "Near right corner",
  near_left: "Near left corner",
  net_left: "Net post, left (on the floor)",
  net_right: "Net post, right (on the floor)",
};

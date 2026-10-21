import { createContext, useContext, useReducer } from "react";

const ReviewStateContext = createContext(null);
const ReviewDispatchContext = createContext(null);

function timeToSec(val) {
  const parts = val.split(":").map(Number);
  if (parts.length !== 2 || parts.some(isNaN)) return null;
  return parts[0] * 60 + parts[1];
}

function reducer(state, action) {
  switch (action.type) {
    case "INIT": {
      const rallies = action.rallies.map((r) => ({ ...r }));
      const existingNegIds = rallies.map((r) => r.id).filter((id) => id < 0);
      return {
        ...state,
        rallies,
        comments: action.comments || "",
        confirmed: !!action.confirmed,
        dirtyCount: 0,
        total: action.total,
        fps: action.fps || 30,
        playerA: action.playerA,
        playerB: action.playerB,
        // Resume-safe: if saved corrections already contain user-added
        // rallies (negative ids), start below the lowest of those.
        nextTempId: existingNegIds.length ? Math.min(...existingNegIds) - 1 : -1,
        selectedId: null,
      };
    }
    case "SET_WINNER":
      return {
        ...state,
        dirtyCount: state.dirtyCount + 1,
        confirmed: false,
        rallies: state.rallies.map((r) => (r.id === action.id ? { ...r, winner: action.winner } : r)),
      };
    case "SET_REASON":
      return {
        ...state,
        dirtyCount: state.dirtyCount + 1,
        confirmed: false,
        rallies: state.rallies.map((r) => (r.id === action.id ? { ...r, reason: action.reason } : r)),
      };
    case "SET_TIME": {
      const secs = timeToSec(action.value);
      if (secs == null) return state; // invalid input -- caller re-renders from unchanged state
      return {
        ...state,
        dirtyCount: state.dirtyCount + 1,
        confirmed: false,
        rallies: state.rallies.map((r) => {
          if (r.id !== action.id) return r;
          if (action.field === "start") return { ...r, start: Math.min(secs, r.end - 2) };
          return { ...r, end: Math.max(secs, r.start + 2) };
        }),
      };
    }
    case "DRAG_UPDATE": {
      // Live redraw while dragging -- does not mark dirty (matches
      // vanilla's onDrag() vs endDrag() split: dirty only commits on release).
      return {
        ...state,
        rallies: state.rallies.map((r) => {
          if (r.id !== action.id) return r;
          if (action.edge === "start") return { ...r, start: Math.min(action.time, r.end - 2) };
          return { ...r, end: Math.max(action.time, r.start + 2) };
        }),
      };
    }
    case "DRAG_COMMIT":
      return { ...state, dirtyCount: state.dirtyCount + 1, confirmed: false };
    case "ADD_RALLY": {
      const id = state.nextTempId;
      const rally = {
        id, start: Math.round(action.start), end: Math.round(action.end),
        winner: null, reason: null, source: "user", flagged: false,
      };
      return {
        ...state,
        rallies: [...state.rallies, rally],
        nextTempId: state.nextTempId - 1,
        selectedId: id,
        dirtyCount: state.dirtyCount + 1,
        confirmed: false,
      };
    }
    case "DELETE_RALLY":
      return {
        ...state,
        rallies: state.rallies.filter((r) => r.id !== action.id),
        selectedId: state.selectedId === action.id ? null : state.selectedId,
        dirtyCount: state.dirtyCount + 1,
        confirmed: false,
      };
    case "SELECT_RALLY":
      return { ...state, selectedId: action.id };
    case "SET_COMMENTS":
      return { ...state, comments: action.value, dirtyCount: state.dirtyCount + 1, confirmed: false };
    case "SAVED":
      return { ...state, dirtyCount: 0, confirmed: action.confirmed };
    default:
      return state;
  }
}

const initialState = {
  rallies: [], selectedId: null, nextTempId: -1, dirtyCount: 0, confirmed: false,
  comments: "", total: 0, fps: 30, playerA: "Player A", playerB: "Player B",
};

export function ReviewProvider({ children }) {
  const [state, dispatch] = useReducer(reducer, initialState);
  return (
    <ReviewStateContext.Provider value={state}>
      <ReviewDispatchContext.Provider value={dispatch}>
        {children}
      </ReviewDispatchContext.Provider>
    </ReviewStateContext.Provider>
  );
}

export function useReviewState() {
  const ctx = useContext(ReviewStateContext);
  if (!ctx) throw new Error("useReviewState must be used within ReviewProvider");
  return ctx;
}

export function useReviewDispatch() {
  const ctx = useContext(ReviewDispatchContext);
  if (!ctx) throw new Error("useReviewDispatch must be used within ReviewProvider");
  return ctx;
}

export function sortedRallies(rallies) {
  return [...rallies].sort((a, b) => a.start - b.start);
}

export function computeScores(rallies) {
  let sa = 0, sb = 0;
  const map = {};
  sortedRallies(rallies).forEach((r) => {
    if (r.winner === "A") sa++;
    else if (r.winner === "B") sb++;
    map[r.id] = [sa, sb];
  });
  return map;
}

export function fmt(s) {
  s = Math.max(0, Math.round(s));
  return Math.floor(s / 60) + ":" + String(s % 60).padStart(2, "0");
}

import { useEffect, useRef, useState } from "react";

/* usePolling -- fetch once on mount/dependency change, then repeat every
   intervalMs, cleared on unmount. Transient fetch errors are swallowed
   (matches every existing poll loop's "catch { retry next tick }"
   behavior) rather than surfaced, since a single missed poll isn't
   actionable to the user. */
export function usePolling(fetchFn, { intervalMs = 2000, enabled = true, deps = [] } = {}) {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const alive = useRef(true);

  useEffect(() => {
    alive.current = true;
    return () => { alive.current = false; };
  }, []);

  useEffect(() => {
    if (!enabled) return;
    let timer = null;
    const tick = async () => {
      try {
        const result = await fetchFn();
        if (alive.current) { setData(result); setError(null); }
      } catch (err) {
        if (alive.current) setError(err);
      } finally {
        if (alive.current) timer = setTimeout(tick, intervalMs);
      }
    };
    tick();
    return () => { if (timer) clearTimeout(timer); };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [enabled, intervalMs, ...deps]);

  return { data, error, setData };
}

import { useEffect, useRef, useState } from "react";
import { getRunStatus } from "../api";

const IN_PROGRESS_STATUSES = ["validating", "training"];

export function usePipelineStatus(runId) {
  const [run, setRun] = useState(null);
  const [error, setError] = useState(null);
  const pollRef = useRef(null);

  useEffect(() => {
    if (!runId) return;
    setRun(null);
    setError(null);

    async function poll() {
      try {
        const data = await getRunStatus(runId);
        setRun(data);
        if (IN_PROGRESS_STATUSES.includes(data.status)) {
          pollRef.current = setTimeout(poll, 1500);
        }
      } catch (err) {
        setError(err.message);
      }
    }
    poll();
    return () => clearTimeout(pollRef.current);
  }, [runId]);

  return { run, error };
}

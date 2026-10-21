import { useState } from "react";
import { useSearchParams } from "react-router-dom";
import { UploadStep } from "../features/match/UploadStep";
import { ProcessingStep } from "../features/match/ProcessingStep";
import { ReviewStep } from "../features/match/ReviewStep";
import "../features/match/match.css";

export function MatchFlowPage() {
  const [searchParams] = useSearchParams();
  const deepLinkJob = searchParams.get("job");

  const [step, setStep] = useState(deepLinkJob ? 2 : 1);
  const [jobId, setJobId] = useState(deepLinkJob || null);

  function handleJobCreated(id) {
    setJobId(id);
    setStep(2);
  }
  function handleRetry(newId) {
    setJobId(newId);
  }
  function handleDone() {
    setStep(3);
  }
  function handleCancelledOrGiveUp() {
    setJobId(null);
    setStep(1);
  }

  return (
    <div>
      {step === 1 && <UploadStep onJobCreated={handleJobCreated} />}
      {step === 2 && jobId && (
        <ProcessingStep jobId={jobId} onDone={handleDone} onRetry={handleRetry}
                        onCancelledOrGiveUp={handleCancelledOrGiveUp} />
      )}
      {step === 3 && jobId && <ReviewStep jobId={jobId} />}
    </div>
  );
}

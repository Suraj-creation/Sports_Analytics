import { useReviewState, useReviewDispatch } from "./ReviewContext";

export function CommentsCard() {
  const { comments } = useReviewState();
  const dispatch = useReviewDispatch();

  return (
    <div className="card">
      <div className="card-head"><h2>Notes for this review</h2></div>
      <textarea
        className="comments-area"
        placeholder="e.g. Rally 5's winner looks wrong -- replay shows the shuttle clipped the line out."
        value={comments}
        onChange={(e) => dispatch({ type: "SET_COMMENTS", value: e.target.value })}
      />
      <div className="char-count">{comments.length} characters</div>
    </div>
  );
}

# Production-readiness annotation and split protocol

This adds cross-component gates to the existing shot, tracking and participant
annotation protocols. It creates no labels. All existing Test1 annotations and
historical evidence remain immutable.

1. Resolve authorized full-recording identity and match identity from metadata.
   Put every clip, re-encode and adjacent excerpt from one match in one partition.
   Preserve source/media/proxy digests, rights provenance and previous exposure.
   Unknown match identity or exposure stays quarantined. Different filenames are
   not evidence of independence.
2. Freeze the metadata split and selection rule before opening prospective
   held-out contents. The supplied metadata snapshot currently contains no new
   eligible holdout. Obtain the pending identity/authorization/review requirements
   before designating one; do not treat metadata contract validation as permission.
3. Independently review authorized original footage with model outputs hidden.
   Record source PTS/frame and canonical correspondence, actual FPS, dimensions,
   exhaustive labelled windows, empty negative spans, visibility and uncertainty.
   Do not infer a hidden shuttle, hitter, identity, contact or line call to complete
   a field. AI/model-assisted drafts remain drafts until actual independent human
   review and adjudication; changing a boolean is not review.
4. Label each component separately. Shuttle labels distinguish visible location,
   occluded/out-of-view, unresolvable blur and absence. Contact labels record one
   physical impact, its uncertainty and hitter/team if supported. Tracking labels
   preserve stable people through side changes/crossings and unknown identity
   separately from box visibility. Shot family, placement, subtype and winner are
   independent properties; accepted point/score decisions need their own evidence.
5. Define rally onset/termination convention explicitly before scoring. Preserve
   preparation/feed, first physical hit, terminal contact/landing, camera editing,
   left/right censoring and genuinely unobservable boundaries separately. Use
   half-open intervals. Record uncertainty ranges and disputed alternatives rather
   than manually fitting boundaries to a detector. A new clarified label version
   does not replace or silently repair the historical Test1 benchmark.
6. A second reviewer adjudicates disputed contact/identity/family/boundary cases.
   Store reviewer role, timestamp, source evidence, original draft and changes,
   independence from predictions, exhaustive-window scope and remaining unknowns.
   Provider-reviewed published anchors retain their provider provenance and timing
   semantics; they are not relabelled as project-reviewed physical impacts.
7. Freeze annotation/taxonomy/mapping hashes, source/model/configuration and metric
   policy before prediction inspection. Keep rally IoU/matching/export rules
   unchanged for historical comparisons. Declare contact timing tolerance and
   tracking matching thresholds without fitting observed errors. Use existing
   evaluators for their stated properties; no one evaluator validates all tasks.
8. Report all-GT and conditional denominators, coverage/abstention, localization,
   timing, identity/association, class confusion, point/score sequence and resource
   measurements. Unknown property labels do not become correct predictions or
   disappear from the task's detection support. Unlabelled spans are not reviewed
   negatives. Document exclusions without removing difficult original annotations.
9. Preserve every rejected run and source-bound output. Once evaluation results
   influence settings or algorithms, mark that material exposed for subsequent
   development and reserve a different authorized match for a new blind claim.

No independent human, rights or dataset-access attestation can be supplied by the
pipeline or the metadata validator. Current missing requirements are recorded in
`production_readiness_dataset_manifest.json`; promotion remains gated until the
relevant evidence is actually obtained and evaluated.

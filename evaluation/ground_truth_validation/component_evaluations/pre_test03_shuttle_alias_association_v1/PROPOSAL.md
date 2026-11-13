# Frozen-source causal finding and minimal proposal

**265/265 exact outputs reproduced** from the verified cut23279 through23543 using native5ae `CausalShuttleAssociation`, actual camera/epoch/configuration, raw coordinates/support and all retained acquisition candidates. Only the two diagnostic attributes actually consumed by this component were reconstructed: full candidates and the unique retained selected-peak target. No heatmap, probability, unused diagnostic entropy or threshold was invented. No NN or production edit occurred.

At23534/35/36/42 the floor hypothesis already has23–30 samples and7–8 co-observed motion witnesses. The failure is **compactness**, not lack of the three-pixel motion or witness quorum. Old peaks23512/13/14 are5.59017px from the history median, just outside its roughly5.24px median component spread. Their individual component spreads vary3.66–11.17px. The all-history all-samples check therefore fails even though the most recent10 consecutive observations lie within2.5px of their median.

| Bad frame | Existing recent10 compact | Witnesses retained by existing60-frame policy | Witnesses inside that same recent10 interval |
|---:|---|---:|---:|
|23534|yes|7|1|
|23535|yes|7|1|
|23536|yes|7|1|
|23542|yes|8|3|

The smallest static-contract correction is evaluate the declared `stationary_samples=10` most recent samples using the unchanged one-spread predicate. Keep the independently declared existing witness-expiry policy. Requiring three witnesses within those same ten samples would be an additional stronger policy and would leave23534–36 unresolved. An alternative paired-spread radius is less narrow and is not the preferred proposal.

That correction alone **abstains from the floor**; it does not restore the projectile. To select an actual alternative, require a uniquely supported observed moving branch after the raw winner has established contradictory-static evidence. Current above-threshold/mask-allowed candidates provide a unique positive four-frame path through23534/35 using existing moving-step and positive-direction criteria. At23536 and23542 the upper model peak repeats on adjacent frames; a fresh four-frame moving predicate fails, but the observed candidate continues the previously supported upper footprint hypothesis (IDs368 and373 respectively). A bounded branch-continuation state can retain positive prior motion while admitting the uniquely matched current observed point. Repeated/zero-motion points must not create new moving witnesses.

This is a proposed association contract, not a general object classifier. Preserve raw argmax, raw confidence and every candidate. No alternative should be forced on cut, gap, reacquisition, ambiguous ownership, multiple compatible branches or insufficient prior support. A genuine slow/floor shuttle without contradictory co-observation remains retained. Never use interpolation's `MAX_FILL_SPEED` as a physical cap or emit forecast coordinates as observations.

Implementation requires a new typed association schema/method: v2 forbids `selected_xy != raw_xy`. Bind selected candidate rank, selected support, exact observed coordinate source and causal proof references. Candidate `centroid_xy` is the0.1 diagnostic-floor centroid, not the old0.5 decode centroid. Use an explicitly identified observed peak, or extend candidate retention to carry its actual threshold centroid; do not silently conflate them. Engine selected support must follow the chosen candidate; its current `_sconf` still uses raw argmax support. Keep raw cache `s/c` and old v2 provenance intact. Version association component, pipeline/cache identity and parser; validate current-candidate membership and reject forged/downcast selection claims.

Required RED/GREEN controls include the exact265-frame case; old-outlier/recent-static10; a recent genuinely moving sample; real stationary shuttle without contradictory witness; uncertain or multiple alternatives; repeated current peak without new motion credit; rapid real projectile without an artificial fill-speed ceiling; missing/invalid/cut/registration changes; checkpoint/restore and chunk equivalence; and singles/doubles body-independent candidate association.

A controlled raw-neural-cache replay can validate this component and downstream semantic effects without new NN, but must explicitly declare source/selection intervention. It must never invent a normal fresh-NN completion. Changes to selected flight can alter in-play feedback and future detector/pose cadence, so feedback parity or a later fresh run is needed before an end-to-end equivalence claim.

Evidence: [exact state receipt](parity_receipt.json), [all actual state rows](actual_state_rows.json), [compact key rows](compact_causal_rows.json), [last10 policy probe](last10_existing_policy_probe.json), and [observed alternative path probe](positive_alternative_path_probe.json). The independent source review binds the lower hypothesis to printed HSBC floor graphics; that physical interpretation is source diagnostic, not a manufactured coordinate annotation.

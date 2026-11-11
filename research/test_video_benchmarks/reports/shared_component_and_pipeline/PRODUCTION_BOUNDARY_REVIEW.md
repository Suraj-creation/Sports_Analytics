# Production boundary review

## Scope and source identity

This is an offline review of the completed historical selected fresh inference at source `33d3a5b`, not a result from the production-continuation GPU pair. Its exact own-cache semantic trace is bound to all 288 cache-file hashes and the prediction CSV. These hashes were checked again while building this report. The original frames, labels, historical metrics and experimental evidence are unchanged.

The canonical video has 17,268 frames at 30 FPS. All intervals are zero-origin and half-open. Signed error is prediction minus annotation. An accepted coordinate or contact is a model/heuristic hypothesis, not physical ground truth. The onset probes have exact coordinate/support parity with the historical caches in their declared paired scopes; 5,081 diagnostic frames cover all 36 onset-review windows. They are component inference evidence, not additional full-pipeline inference.

The firsts column lists **model / provider / processed / movement / player motion / accepted contact**. Model/provider firsts cover the declared review window between annotation and surviving onset; the remaining firsts cover the annotated span. In early-start rows these different scopes must not be interpreted as a single chronological chain. The machine-readable artifact retains both windows and complete candidate cancellations.

## All 36 onset classifications

| GT | Historical prediction | Signed start/end | Firsts | Onset and observability status |
|---|---|---|---|---|
| 1 | [264, 717) | +21/+2 | 248/248/248/261/270/264 | Weak initial model support; admitted 248, movement 261, contact starts 264. Earlier physical onset unreviewed. |
| 2 | [890, 1255) | +3/-7 | 887/887/887/888/888/894 | Short motion-confirmation delay; recovered match retained. Physical onset convention unreviewed. |
| 3 | [1402, 1659) | +4/-5 | 1398/1398/1398/1399/1404/1407 | Short motion-confirmation delay. Physical onset convention unreviewed. |
| 4 | [1803, 2167) | -71/+6 | 1803/1803/1884/1885/1874/1894 | Pre-label contact 1803 and high serve/feed retained through upper flight. First-return versus serve convention unresolved. |
| 5 | [2308, 2496) | +98/-4 | 2210/2210/2210/2220/2243/2210 | Candidate 2210 closes at 2254 after loss and cancels 2277; next start 2308. Severe provisional-event continuity loss. |
| 6 | [2578, 2799) | +20/-7 | 2560/2574/2576/2585/2592/2578 | Raw 2560 is excluded close-up. Wide view 2574, valid context 2576, contact 2578; no close-up backdate justified. |
| 7 | [2977, 3377) | +1/+0 | 2976/2976/2976/2977/2977/2983 | Near-exact confirmation. Separate 2895 preparation/2917 launch is a retained maturity-gate negative control. |
| 8 | [3519, 3699) | +68/+4 | 3465/3465/3467/3519/3475/3540 | Annotation begins in reviewed preparation close-up. Accepted 3465 precedes sustained movement 3519; mixed visibility and sparse motion. |
| 9 | [3857, 4059) | +106/-14 | 3753/3769/3769/3785/3792/3771 | Raw 3753 is excluded close-up. Candidate 3771 cancels 3827 after loss ending 3804; surviving start 3857. Mixed causes. |
| 10 | [4272, 4804) | +25/-35 | 4260/4260/4260/4268/4278/4272 | Provider begins 4260, movement 4268, contact start 4272. Earlier physical onset unreviewed. |
| 11 | [4901, 5027) | +29/-18 | 4876/4876/4876/4898/4907/4901 | Provider 4876 precedes movement 4898/contact 4901. Sparse/weak-motion onset; physical onset unreviewed. |
| 12 | [5455, 5887) | +25/+16 | 5448/5448/5448/5455/5461/5459 | Earlier preparation candidate 5379 cancels 5434; current accepted 5448, motion start 5455. Earlier physical onset unreviewed. |
| 13 | [5979, 6315) | +21/+3 | 5958/5976/5976/5977/5981/5979 | Raw 5958 is excluded close-up; main view 5960, valid 5962, first accepted 5976, contact 5979. |
| 14 | [6450, 6639) | +68/-17 | 6382/6396/6396/6397/6404/6456 | Raw 6382 is excluded close-up; accepted 6396/motion 6397 lacks sustained confirmation until start 6450. |
| 15 | [6802, 6908) | +86/-5 | 6720/6720/6720/6737/6738/6732 | Candidate 6732 closes at 6750 and cancels 6773; start 6802. Severe loss before event maturity; no global duration reduction. |
| 16 | [7006, 7499) | +30/+41 | 6976/7005/7005/7006/7008/7024 | Raw 6976 is excluded close-up; wide 6991/valid 6993 precede accepted 7005 and start 7006. |
| 17 | [7535, 7731) | +3/-10 | 7532/7532/7532/7537/7543/7535 | Contact-confirmed 7535 shortly after provider 7532. Physical onset unreviewed. |
| 18 | [7953, 8052) | +6/-1 | 7952/7952/7952/7954/7968/7953 | Provider 7952, contact start 7953, motion 7954. Physical onset unreviewed. |
| 19 | [8110, 8627) | +4/-1 | 8106/8106/8106/8107/8114/8136 | First provider 8106 and motion 8107 yield start 8110. Previously recovered case retained. |
| 20 | [8715, 9947) | +32/-20 | 8708/8708/8708/8709/8712/8730 | Main view 8697/valid 8699, accepted 8708, movement 8709, start 8715. Previously recovered long rally retained. |
| 21 | [10250, 10539) | +5/-24 | 10247/10247/10247/10248/10254/10262 | Short provider/motion-confirmation delay, 10247/10248 to start 10250. Physical onset unreviewed. |
| 22 | [10578, 10737) | -29/+29 | 10578/10578/10607/10607/10616/10665 | Weak pre-edit contact starts 10578 across content edit 10604. Explicit scene counterfactual changes start to 10605; annotation 10607. |
| 23 | [10769, 11085) | +36/+7 | 10736/10736/10736/10740/10733/10737 | Preparation before real edit 10770; old contact start 10769 crosses edit. Later singleton continuity is separate; scene start 10777 regresses 8 frames. |
| 24 | [11274, 11397) | +3/+5 | 11273/11273/11273/11275/11286/11274 | Contact-confirmed start 11274 after provider 11273. Physical onset unreviewed. |
| 25 | [11613, 11867) | +45/+2 | 11568/11568/11568/11573/11586/11570 | Candidate 11570 closes 11587 and cancels 11610; new contact starts 11613. Provisional continuity loss. |
| 26 | [11982, 12196) | +6/-1 | 11980/11980/11980/11982/11994/11992 | Short motion confirmation: provider 11980/motion 11982, start 11982. Physical onset unreviewed. |
| 27 | [12455, 12954) | +4/-12 | 12454/12454/12454/12455/12462/12467 | Near-exact onset. Later recovered continuity depends on suspect T contact 12766 in historical selected run; boundary alone is insufficient. |
| 28 | [13115, 13439) | +61/-3 | 13054/13054/13112/13113/13128/13124 | Source-visible wide-view upper streak at 13054 is rejected by geometry reacquisition; no accepted return until 13112. Image validity and projection differ. |
| 29 | [13686, 13982) | +7/-12 | 13683/13683/13683/13684/13698/13748 | Provider 13683/motion 13684 to start 13686. Previously recovered match retained; physical onset unreviewed. |
| 30 | [14222, 14331) | +3/-4 | 14219/14219/14219/14222/14226/14244 | Short motion confirmation from first provider 14219 to start 14222. Physical onset unreviewed. |
| 31 | [14430, 15171) | +26/+20 | 14405/14425/14427/14430/14466/14440 | Raw 14405 is excluded close-up; main 14425/valid 14427, start 14430. Upper-mask repair preserves later flight without close-up backdate. |
| 32 | [15354, 15529) | +4/-6 | 15353/15353/15353/15354/15366/15377 | Short motion confirmation from provider 15353/motion 15354 to start 15354. Physical onset unreviewed. |
| 33 | [15664, 15951) | +68/+5 | 15599/15599/15599/15600/15606/15611 | Start 15602 closes 15615 and cancels 15638 after loss; surviving start 15664. Provisional continuity loss. |
| 34 | [15983, 16385) | -15/-2 | 15983/15983/15999/16001/16003/16000 | Pre-label contact 15983 precedes content edit 15985; scene counterfactual starts 16000. Earlier physical onset remains unadjudicated. |
| 35 | [16521, 17031) | +8/+5 | 16517/16517/16517/16518/16524/16543 | Provider 16517/motion 16518 yield start 16521. Physical onset unreviewed. |
| 36 | [17074, 17207) | +8/-19 | 17072/17072/17072/17074/17066/17086 | Weak raw support before provider 17072/motion start 17074. Physical onset unreviewed; endpoint is not EOF finalization. |

## All 36 terminal classifications

`gap` is an evidence-timeout decision; `stationary` is an engine reason, not a verified landing. The evidence kind at the proposal is listed separately because a retained stationary hypothesis can be acted on when the current observation is missing. Player motion cannot establish a terminal contact. No row has independently reviewed landing/contact-time labels, so the physical terminal mechanism remains unknown even where the numerical boundary is close.

| GT | Signed end | Final reason | Proposal → close → publication | Evidence at proposal | Terminal status |
|---|---|---|---|---|---|
| 1 | +2 | gap | 727 → 732 → 740 | missing, speed unknown | Physical endpoint unverified; late |
| 2 | -7 | stationary | 1264 → 1270 → 1278 | observed, speed 1.0118 | Physical endpoint unverified; early |
| 3 | -5 | gap | 1669 → 1674 → 1682 | reconstructed, speed unknown | Physical endpoint unverified; early |
| 4 | +6 | gap | 2177 → 2182 → 2190 | missing, speed unknown | Physical endpoint unverified; late |
| 5 | -4 | stationary | 2505 → 2511 → 2519 | observed, speed 2.3263 | Physical endpoint unverified; early |
| 6 | -7 | gap | 2809 → 2814 → 2822 | missing, speed unknown | Physical endpoint unverified; early |
| 7 | +0 | stationary | 3386 → 3392 → 3400 | observed, speed 0.4066 | Physical endpoint unverified; annotation-aligned |
| 8 | +4 | gap | 3709 → 3714 → 3722 | missing, speed unknown | Physical endpoint unverified; late |
| 9 | -14 | stationary | 4068 → 4074 → 4082 | missing, speed unknown | Physical endpoint unverified; early |
| 10 | -35 | stationary | 4813 → 4819 → 4827 | observed, speed 1.7419 | Physical endpoint unverified; early |
| 11 | -18 | stationary | 5036 → 5042 → 5050 | observed, speed 0.6247 | Physical endpoint unverified; early |
| 12 | +16 | stationary | 5896 → 5902 → 5910 | observed, speed 0.8529 | Physical endpoint unverified; late |
| 13 | +3 | gap | 6325 → 6330 → 6338 | missing, speed unknown | Physical endpoint unverified; late |
| 14 | -17 | gap | 6649 → 6654 → 6662 | reconstructed, speed unknown | Physical endpoint unverified; early |
| 15 | -5 | stationary | 6917 → 6923 → 6931 | observed, speed 0.9482 | Physical endpoint unverified; early |
| 16 | +41 | gap | 7509 → 7514 → 7522 | missing, speed unknown | Physical endpoint unverified; late; scene counterfactual worsens +41 to +44 |
| 17 | -10 | gap | 7741 → 7746 → 7754 | reconstructed, speed unknown | Physical endpoint unverified; early |
| 18 | -1 | stationary | 8061 → 8067 → 8075 | observed, speed 1.1631 | Physical endpoint unverified; early |
| 19 | -1 | gap | 8637 → 8642 → 8650 | missing, speed unknown | Physical endpoint unverified; early |
| 20 | -20 | gap | 9957 → 9962 → 9970 | missing, speed unknown | Physical endpoint unverified; early |
| 21 | -24 | stationary | 10548 → 10554 → 10562 | observed, speed 1.4916 | Physical endpoint unverified; early |
| 22 | +29 | stationary | 10746 → 10752 → 10760 | observed, speed 0.0101 | Physical endpoint unverified; late |
| 23 | +7 | stationary | 11094 → 11100 → 11108 | observed, speed 0.6953 | Physical endpoint unverified; late |
| 24 | +5 | stationary | 11406 → 11412 → 11420 | observed, speed 0.0044 | Physical endpoint unverified; late |
| 25 | +2 | gap | 11877 → 11882 → 11890 | missing, speed unknown | Physical endpoint unverified; late |
| 26 | -1 | stationary | 12205 → 12211 → 12219 | observed, speed 1.1047 | Physical endpoint unverified; early |
| 27 | -12 | stationary | 12963 → 12969 → 12977 | observed, speed 1.2007 | Physical endpoint unverified; early; intermediate closure at 12748 depends on suspect contact reopening |
| 28 | -3 | gap | 13449 → 13454 → 13462 | missing, speed unknown | Physical endpoint unverified; early |
| 29 | -12 | stationary | 13991 → 13997 → 14005 | observed, speed 0.2629 | Physical endpoint unverified; early |
| 30 | -4 | gap | 14341 → 14346 → 14354 | missing, speed unknown | Physical endpoint unverified; early |
| 31 | +20 | stationary | 15180 → 15186 → 15194 | observed, speed unknown | Physical endpoint unverified; late; stationary reason has no current speed at proposal |
| 32 | -6 | stationary | 15538 → 15544 → 15552 | observed, speed 1.0676 | Physical endpoint unverified; early |
| 33 | +5 | gap | 15961 → 15966 → 15974 | reconstructed, speed unknown | Physical endpoint unverified; late |
| 34 | -2 | stationary | 16394 → 16400 → 16408 | observed, speed 1.4012 | Physical endpoint unverified; early |
| 35 | +5 | gap | 17041 → 17046 → 17054 | missing, speed unknown | Physical endpoint unverified; late |
| 36 | -19 | gap | 17217 → 17222 → 17230 | reconstructed, speed unknown | Physical endpoint unverified; early |

## Discriminating mechanisms and bounds

Cancelled in-span provisional candidates remain material at GT5, GT9, GT15, GT25 and GT33. Waiting through an unsupported gap cannot confer event maturity. The existing qualified association deliberately does not extend these events merely because that improves an annotation score. Sparse early points without sustained motion are a separate mechanism at GT8 and GT14. GT12's earlier candidate predates the supplied onset and must not be conflated with those in-span cancellations.

Original-frame review shows excluded close-ups at GT6 frame2560, GT9 frame3753, GT13 frame5958, GT14 frame6382, GT16 frame6976 and GT31 frame14405. Those strong rejected model peaks do not justify earlier rally inference. GT8 frame3451 shows a shuttle held in preparation; preparation visibility does not establish a rally onset. These are assistant-reviewed examples, not independently adjudicated first-visible-frame labels. For other rows, the exact first physically observable sporting onset remains unknown unless explicitly described above.

GT28 frame13054 differs: a wide view and visible upper streak support the accepted provider point while projection is REACQUIRING. Geometry rejects two useful image-plane observations, but the following frame moves only 0.708 pixels before the long admission/visibility gap to13112. Separating image validity from floor calibration repairs evidence semantics; it alone does not prove an earlier start.

GT4 begins at weak accepted contact1803; pixels show a held shuttle near1803, launch around1828 and overhead preparation at1874. A serve-versus-first-return annotation convention remains unresolved. GT7's comparable preparation/launch is a negative regression control, not a pretext to fit one rally. Do not offset or edit either boundary.

GT23's later loss has a competing singleton10936 retained in raw observations; coherent top-flight brackets10906–10910 and10947–10951 support qualified continuity. This is separate from the physical content edit10769→10770. Historical GT31 continuity instead uses ordinary observed top-exit/return brackets14646–14650 and14683–14687 after upstream mask repair; no curve or invented point is needed.

GT27's historical result conceals an unreliable causal dependency: stationary evidence proposes12748, closes12763, and suspect T contact12766 reopens it. Removing only that contact fragments the rally while every processed shuttle step and the other35matched rows remain unchanged. The new association/contact consumer experiments must be evaluated jointly and must retain actual-floor, low-speed serve, fast flight and separate-rally controls. Historical perfect detection is not proof that this dependency is sound.

## Cached scene effects awaiting fresh validation

The separately executed cached association counterfactual retains all36historical intervals exactly and changes live contacts457→453. Association plus 13causal scene hypotheses retains36TP/0FP/0FN and changes only four rows. Start MAE29.1389→28.25 and mean IoU0.867622→0.871347 improve; end MAE10.3333→10.4167 worsens. Changed neural context windows and detector resets are not represented as fresh perception by this experiment.

| GT | Historical interval | Cached scene interval | Measured effect |
|---|---|---|---|
| 16 | [7006, 7499] | [7006, 7502] | End +41→+44: worsens3frames |
| 22 | [10578, 10737] | [10605, 10737] | Start −29→−2: improves27frames |
| 23 | [10769, 11085] | [10777, 11085] | Start +36→+44: worsens8frames |
| 34 | [15983, 16385] | [16000, 16385] | Start −15→+2: improves13absolute frames |

All other32rows remain endpoint-identical. GT22 and GT23 remain distinct. The 13automatically proposed edits have assistant original-frame review, not an independently labelled cut-recall denominator. The explicit experimental barrier does not recalibrate a valid same-camera court.

## Independently checked new full-pipeline pair

The completed actual inference runs are `prod_20261105_fresh_association_v1` and `prod_20261105_fresh_association_scene_v1`, both frozen at source `85993259a3a2838881ed2b18658a07967058d191`. These are fresh neural/perception runs, distinct from their subsequent cached semantic traces. Both retain 36 TP, zero FP and zero FN under the unchanged evaluator. Each own-cache replay matches all 36 finalized interval/end-reason triples, prediction CSV bytes and folded contact/stroke/rally timestamp multiplicities. This independent audit also rehashed all 288 cache files per run and verified each trace SHA against its replay metadata. Source guards remain true; no labels enter inference or replay.

Association alone retains the exact historical selected CSV and boundaries, with 453 live contacts/strokes. The scene arm has 446 live contacts/strokes and changes seven GT rows; the other 29 rows are endpoint-identical. Start MAE is 28.25 frames; end MAE is 10.472222 frames and mean IoU is 0.871025665. All metrics and denominators remain in the unchanged evaluator output; these counts do not measure physical contact accuracy.

Actual elapsed inference times are 1649.780 seconds / 10.46685 FPS and 1794.365 seconds / 9.62346 FPS respectively. The runs shared CPU resources and used separate leased GTX1080Ti devices concurrently. This is offline development throughput, below the 30 FPS source, not a real-time or independently isolated latency result.

| GT | Fresh association interval | Fresh scene interval | Scene signed start/end | First processed observed in scene GT span | Scene surviving start call |
|---|---|---|---|---|---|
| 1 | [264, 717) | [264, 717) | +21/+2 | 248 | contact@264 |
| 2 | [890, 1255) | [890, 1255) | +3/-7 | 887 | step@892 |
| 3 | [1402, 1659) | [1402, 1659) | +4/-5 | 1398 | step@1404 |
| 4 | [1803, 2167) | [1803, 2167) | -71/+6 | 1884 | contact@1803 |
| 5 | [2308, 2496) | [2308, 2496) | +98/-4 | 2220 | step@2310 |
| 6 | [2578, 2799) | [2578, 2799) | +20/-7 | 2576 | contact@2578 |
| 7 | [2977, 3377) | [2977, 3377) | +1/+0 | 2976 | step@2979 |
| 8 | [3519, 3699) | [3519, 3699) | +68/+4 | 3467 | step@3521 |
| 9 | [3857, 4059) | [3857, 4059) | +106/-14 | 3769 | step@3859 |
| 10 | [4272, 4804) | [4272, 4804) | +25/-35 | 4260 | contact@4272 |
| 11 | [4901, 5027) | [4901, 5027) | +29/-18 | 4884 | contact@4901 |
| 12 | [5455, 5887) | [5455, 5887) | +25/+16 | 5448 | step@5457 |
| 13 | [5979, 6315) | [5979, 6315) | +21/+3 | 5976 | contact@5979 |
| 14 | [6450, 6639) | [6450, 6639) | +68/-17 | 6396 | step@6452 |
| 15 | [6802, 6908) | [6802, 6908) | +86/-5 | 6720 | step@6804 |
| 16 | [7006, 7499) | [7006, 7502) | +30/+44 | 7005 | step@7008 |
| 17 | [7535, 7731) | [7537, 7731) | +5/-10 | 7535 | contact@7537 |
| 18 | [7953, 8052) | [7953, 8052) | +6/-1 | 7952 | contact@7953 |
| 19 | [8110, 8627) | [8111, 8627) | +5/-1 | 8106 | step@8113 |
| 20 | [8715, 9947) | [8715, 9947) | +32/-20 | 8708 | step@8717 |
| 21 | [10250, 10539) | [10249, 10538) | +4/-25 | 10248 | contact@10249 |
| 22 | [10578, 10737) | [10605, 10738) | -2/+30 | 10607 | step@10607 |
| 23 | [10769, 11085) | [10775, 11085) | +42/+7 | 10737 | contact@10775 |
| 24 | [11274, 11397) | [11274, 11397) | +3/+5 | 11273 | contact@11274 |
| 25 | [11613, 11867) | [11613, 11867) | +45/+2 | 11568 | contact@11613 |
| 26 | [11982, 12196) | [11982, 12196) | +6/-1 | 11980 | step@11984 |
| 27 | [12455, 12954) | [12455, 12954) | +4/-12 | 12454 | step@12457 |
| 28 | [13115, 13439) | [13115, 13439) | +61/-3 | 13112 | step@13117 |
| 29 | [13686, 13982) | [13686, 13982) | +7/-12 | 13683 | step@13688 |
| 30 | [14222, 14331) | [14222, 14331) | +3/-4 | 14219 | step@14224 |
| 31 | [14430, 15171) | [14430, 15171) | +26/+20 | 14427 | step@14432 |
| 32 | [15354, 15529) | [15354, 15529) | +4/-6 | 15353 | step@15356 |
| 33 | [15664, 15951) | [15664, 15951) | +68/+5 | 15600 | step@15666 |
| 34 | [15983, 16385) | [16000, 16385) | +2/-2 | 15999 | contact@16000 |
| 35 | [16521, 17031) | [16521, 17031) | +8/+5 | 16517 | step@16523 |
| 36 | [17074, 17207) | [17074, 17207) | +8/-19 | 17071 | step@17076 |

The firsts in the earlier historical table remain bound to the historical caches and parity-checked component probes. They are not relabelled as new perception firsts: scene barriers change actual model inputs/backgrounds, so historical raw-peak diagnostics cannot establish current raw-peak availability. New processed firsts above come only from the new own trace. Physical first-visible/contact/landing labels remain unknown unless separately reviewed source evidence establishes them.

### Fresh effects beyond the cached scene intervention

| GT | Cached scene → actual fresh scene | Verified trace/observation difference |
|---|---|---|
| 17 | Start 7535 → 7537 | Fresh scene lacks accepted 7532–7534; the accepted contact and start occur at 7537, versus 7535 in association. |
| 19 | Start 8110 → 8111 | Fresh scene lacks 8109; the three-sample movement confirmation occurs at 8113 with run start 8111, versus confirmation 8112/start 8110. |
| 21 | [10250, 10539) → [10249, 10538) | Scene contact starts 10249, replacing the old movement-confirmed onset. Stationary proposal occurs 10547 with endpoint10538; the control proposes10548 with endpoint10539. |
| 22 | End 10737 → 10738 | Last accepted contact becomes10738 rather than10737; stationary proposal moves10746→10747, then publication10760→10761. |
| 23 | Start 10777 → 10775 | Recomputed post-edit model stream gives accepted contact10775. No contact crossing the10770content boundary is borrowed. |

The two extra end-error frames are exactly GT21 and GT22, each worsening absolute end error by one; their combined contribution is 2/36 = 0.055556 frames. This explains cached end MAE10.416667→fresh10.472222. New GT17/19 start regressions (+2/+1 absolute) are exactly offset numerically by GT21/23 improvements (−1/−2 absolute), explaining why the aggregate start MAE remains28.25. This equality must not hide the changed rows.

All-source numerical comparison between the fresh arms finds 4354 changed raw selected coordinates, 4222 changed raw supports and 60 changed detector-run flags. A coordinate difference is not automatically a localization error. The content policy supplies composite keys to both eight-frame window partitioning and per-shot median backgrounds; it also resets player tracking at accepted barriers. These feedback effects are absent from a semantic-only barrier intervention. In the listed local boundary windows, detector-run flags and pose stride agree; the demonstrated difference is the recomputed shuttle/contact stream, not an established local pose-cadence cause.

At GT21 the fresh scene stream repeatedly selects coordinates near the previously reviewed court-T image footprint around10532–10539 and later; association marks relevant samples ambiguous, preserving raw points. The scene FSM sees ambiguous current evidence at10548 after its stationary proposal. The physical identity/landing at those new points has not been reviewed here. The own trace proves the changed decision chain; it does not independently prove a physical termination or isolate background versus window-phase contributions. A one-variable perception replay would be needed to separate those two mechanisms.

GT16 end +44 remains a three-frame regression relative to the historical selected end +41. GT23 fresh start +42 remains six frames worse than the historical +36, while improving two frames over the cached +44. GT22 start improves −29→−2, but its end +29→+30 worsens. GT34 start improves −15→+2. GT4/5/9/15/27/28/31 and previously recovered GT2/19/20 remain matched; all unreviewed onset/terminal uncertainty remains explicit. No frame adjustment, annotation removal, event-count forcing, new matching rule or production promotion follows.

Independent audit artifact: `artifacts/benchmarking/experiments/prod_20261105_boundary_fresh_audit_v1/fresh_boundary_audit.json`, with exact executed auditor and compact new-observation excerpts. Earlier baseline machine-readable rows and hashes remain immutable under `prod_20261105_boundary_review_baseline_v2/`.

### Exact new-trace references

The immutable association trace is
`artifacts/benchmarking/experiments/prod_20261105_owncache_association_v1/fsm_trace.jsonl`
(SHA256 `eb68719aeffecc8239d43ffcb1c6f891f5809bef7af44edc1ae706f0428708df`).
The scene trace is
`artifacts/benchmarking/experiments/prod_20261105_owncache_association_scene_v1/fsm_trace.jsonl`
(SHA256 `ab72b4c27f821d42b01625806176504aa94281e7212c35201a093c3335dccdcd`).
Line references below are one-origin JSONL lines, with canonical frames stated separately.
All 36 interval start/publication line references for both runs are in
`prod_20261105_boundary_fresh_audit_v1/trace_line_references.json`.

| Decision | Association trace line / frame | Scene trace line / frame |
|---|---|---|
| GT17 contact onset | 7986 / 7535 | 7989 / 7537 |
| GT19 movement onset confirmation | 8575 / 8112, start8110 | 8581 / 8113, start8111 |
| GT21 onset | 10804 / 10252, step start10250 | 10806 / 10249, contact start10249 |
| GT21 stationary proposal | 11111 / 10548, end10539 | 11115 / 10547, end10538 |
| GT22 stationary proposal | 11317 / 10746, end10737 | 11320 / 10747, end10738 |
| GT23 new post-edit onset | Historical contact10769 crosses edit; cached scene used10777 | 11349 / 10775 |

The trace references establish software causality and event publication. They do not
supply independently reviewed physical contact or terminal labels.

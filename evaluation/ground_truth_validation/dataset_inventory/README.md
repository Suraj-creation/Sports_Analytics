# Complete Part2 dataset understanding

Read these in order:

1. [Dataset inventory and all column profiles](dataset_manifest.json):62 files,48 CSVs,8 court JSONs,4 DOCX files plus supporting repository files. Counts include all original files; no raw inputs changed.
2. [Component schemas and coordinate contracts](component_schema_analysis.md).
3. [Outcome, scoring, Full2 and reference provenance](outcome_provenance_analysis.md).
4. [Current implementation and stage/output mapping](current_pipeline_mapping.md).
5. [Per-file evaluation eligibility manifest](evaluation_manifest.json): all56 CSV/JSON files are mapped; unsupported metrics remain unavailable, not zero.
6. [Live supplied Drive contents](drive_listing_20261110.json).

Test1 has36 coarse human-origin rows, a36-row generated timing reference, alternate35/38-row generated timing tables, a partial20-valid-row Full2 candidate plus literalellipsis, dense17,268-frame legacy shuttle/player outputs,36 legacy winner predictions, and manual court geometry at frame8634. Legacy prediction files are retained for disagreement diagnosis, not promoted to independent physical GT. No annotation enters baseline inference or calibration.

Quality gates: missing Test5/8 annotation folders; no Test8 video in supplied Drive; Test3 data row6 is structurally incomplete; Full2 row21 is a literalellipsis; A/B and score continuity conflicts remain explicit. Six court JSONs declare `source: manual`; Tests6/7 omit source provenance and remain unspecified. Do not infer those two are manual.

The fresh baseline is allowed only after these semantics, coverage limits and source bindings are reviewed. Diagnoses must distinguish geometric/reference disagreement, generated-model disagreement and independently supported physical error. No Test2 inference before Test1 diagnosis/fix/regression gates.

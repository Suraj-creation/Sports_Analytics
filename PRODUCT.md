# Rally analytics platform

<!-- impeccable:product-schema 1 -->

## Platform

web

## Product Purpose

Turn saved badminton recordings into an inspectable video workspace with source-linked observations, candidate shots, rallies, movement, and supported score evidence. The core job is reviewing a recording and understanding what the available evidence supports.

## Users

Players reviewing badminton recordings. This audience is established by the existing application and product documents; additional commercial roles are outside this redesign.

## Operating Context

The React analytics application lives in apps/web. The independent client-facing website lives in client-website and supplies the approved Rally identity assets. Recordings, calibration, events, and tracks persist on the GPU server. Opening saved work must remain read-only. Reanalysis is an explicit action with a backup.

## Capabilities and Constraints

Preserve authentication, uploads and YouTube imports, saved matches, evidence seeking, calibration, analytics, export, settings, accessibility, and all existing routes. Do not invent scores, classification accuracy, people, or progress. Missing or uncertain evidence remains explicit. The current shot classifier is a rule-based preview.

Author this redesign in the local Windows checkout as requested. Keep inference and application data on the existing GPU environment. Preserve unrelated local drafts, Part2, SportsVideoAnalysis, and the independent client website. Never commit application or SSH credentials.

## Brand Commitments

Use the exact approved Rally logo family from client-website/assets/brand. The user requests a coherent family of greens and a professional working interface, with readable controls and purposeful animation. Keep the client-facing website intact.

## Product Principles

- The recording and its evidence lead the workspace.
- Saved work should reopen without performing inference.
- Every metric must identify its basis and preserve uncertainty.
- Controls stay legible across focus, filled, autofill, disabled, light, and dark states.
- A user can enlarge or collapse the video workspace without losing playback position or analysis state.

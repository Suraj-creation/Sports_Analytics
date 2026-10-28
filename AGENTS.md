# Project workspace

Author code in the current local Windows checkout/worktree, following the user's
request to keep editing fast. Preserve unrelated local changes and untracked
folders, including `Part2/` and `SportsVideoAnalysis/`. Use Git to transfer tested
changes to an isolated checkout on the Remote GPU Server for inference and
end-to-end application testing. The server runtime and existing environment are
under `/home/administrator/Desktop/sport-analytics/Sports_Analytics`.
Do not store SSH passwords or application secrets in this repository.

## Runtime

On the GPU server, source `../gpu-env.sh` before inference, media processing or
tests and use the existing `.venv`. Run all tests, model inference and media
processing on the GPU server; the space-constrained Windows device is for
editing, Git and browser access only. The server's Pascal GPUs require its configured
CUDA/FFmpeg environment; do not replace that environment during routine work.
Do not stop unrelated GPU training jobs. Keep Cloudflare disabled during testing;
use localhost or an SSH local port forward for browser access.
Preserve existing untracked user files, including `apps/web/dist.old/`.

## Validation

The application is started with `../start-server.sh` on port 8010.
Court-isolation design and evaluation instructions are in
`docs/multi-court-isolation.md`. Back up session results before reanalysis.
Geometric exclusion metrics are not labelled shuttle/event accuracy.

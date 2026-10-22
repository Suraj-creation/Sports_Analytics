# Project workspace

The user's working project is on the Remote GPU Server at
`/home/administrator/Desktop/sport-analytics/Sports_Analytics`.
Use this repository for project changes, tests, and application operations.
The Windows `Badminton_analytics` folder is not the authoritative checkout.
Do not store SSH passwords or application secrets in this repository.

## Runtime

Source `../gpu-env.sh` before GPU inference, media processing, or tests, and
use the existing `.venv`. The server's Pascal GPUs require its configured
CUDA/FFmpeg environment; do not replace that environment during routine work.
Do not stop unrelated GPU training jobs or the Cloudflare tunnel.
Preserve existing untracked user files, including `apps/web/dist.old/`.

## Validation

The application is started with `../start-server.sh` on port 8010.
Court-isolation design and evaluation instructions are in
`docs/multi-court-isolation.md`. Back up session results before reanalysis.
Geometric exclusion metrics are not labelled shuttle/event accuracy.

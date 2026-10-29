#!/usr/bin/env bash
# Start the built web app, API and embedded analysis engine together.
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"

if [[ ! -x .venv/bin/python || ! -f apps/web/dist/index.html ]]; then
    echo "Install Python dependencies and build apps/web before starting." >&2
    exit 1
fi

# Make the virtual environment's NVIDIA libraries available to ONNX Runtime.
gpu_libs="$(.venv/bin/python - <<'PY'
import site
from pathlib import Path

dirs = []
for root in map(Path, site.getsitepackages()):
    dirs.extend(sorted(root.glob('nvidia/*/lib')))
    if (root / 'torch/lib').is_dir():
        dirs.append(root / 'torch/lib')
print(':'.join(dict.fromkeys(map(str, dirs))))
PY
)"
export LD_LIBRARY_PATH="${gpu_libs}${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}"

# Export .env values for SDK clients as well as pydantic-settings.
exec .venv/bin/python -m dotenv run --no-override -- .venv/bin/bai serve "$@"

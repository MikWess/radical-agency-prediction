#!/bin/sh
set -eu
cd "$(dirname "$0")/../.."
if [ ! -x .venv/bin/python ]; then
  uv venv --python 3.12 .venv
fi
uv pip install --python .venv/bin/python -r requirements.txt
HF_HOME="$PWD/models/huggingface" .venv/bin/python - <<'PY'
from huggingface_hub import snapshot_download
snapshot_download('mlx-community/Qwen3-4B-4bit', revision='4dcb3d101c2a062e5c1d4bb173588c54ea6c4d25', allow_patterns=['*.json', '*.safetensors', '*.jinja', '*.txt'])
PY

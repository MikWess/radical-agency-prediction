#!/bin/sh
set -eu
cd "$(dirname "$0")/../.."
exec .venv/bin/python experiments/response-prediction/server.py "$@"

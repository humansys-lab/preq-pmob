#!/bin/bash

n_experiments=10

if ! command -v uv >/dev/null 2>&1; then
    echo "uv is not installed. Please install uv to run the experiments." >&2
    exit 1
fi

for ((i=1; i<=n_experiments; i++)); do
    echo "Running experiment $i/$n_experiments"
    uv run python experiments/run_experiments.py
done

#!/bin/bash

n_experiments=10

for ((i=1; i<=n_experiments; i++))
do
    echo "Running experiment $i/$n_experiments"
    poetry run python experiments/run_experiments.py
done

#!/bin/bash

uv run snakemake

# starts n APIs for each sample

start_port=4000

# Counter for ports
port=$start_port

for file in data/*.tsv; do
  # Run the command in the background
  uv run --package api src/api/api/serve.py $file --port $port &
  
  # Increment the port number
  ((port++))
done
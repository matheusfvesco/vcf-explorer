#!/bin/bash

uv run snakemake

uv run fastapi run serve.py --port 4000
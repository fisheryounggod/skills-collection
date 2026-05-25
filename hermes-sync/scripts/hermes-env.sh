#!/usr/bin/env python3
"""hermes-env: Sources ~/.profile and extracts HERMES_GITHUB_TOKEN."""
import os

profile_path = os.path.expanduser("~/.profile")
if os.path.exists(profile_path):
    with open(profile_path) as f:
        for line in f:
            if line.startswith('export HERMES_GITHUB_TOKEN=') or line.startswith('HERMES_GITHUB_TOKEN='):
                parts = line.strip().split('=', 1)
                if len(parts) == 2:
                    val = parts[1].strip().strip('"').strip("'")
                    os.environ['HERMES_GITHUB_TOKEN'] = val
                    print(f"Loaded: HERMES_GITHUB_TOKEN")
                    break

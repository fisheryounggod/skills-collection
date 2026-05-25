# Background Batch Execution for Long-Task Skills

## Problem

Spikes often generate multiple independent output files (videos, images, data analyses). When each task takes >5 minutes, running them sequentially in a single terminal session hits the Hermes 60s polling timeout. The controller session times out while sub-processes are still running.

## Pattern: Subprocess Spawning with Background Polling

Spawn each unit of work as an independent `subprocess.Popen`, then poll from the controller until each completes. This works because:
- Individual animation renders take ~15s (well under the 60s timeout)
- The controller only needs to survive the *gap* between completions, not the full wall time
- Parallel execution reduces total wall time significantly

```python
import subprocess, time, os

PYTHON = "/opt/anaconda3/bin/python3"   # prefer conda env with dependencies
SCRIPT_TEMPLATE = """
import sys; ...
"""

jobs = {}
for item in items:
    script_path = f"/tmp/_gen_{item}.py"
    with open(script_path, "w") as f:
        f.write(SCRIPT_TEMPLATE.replace("{{ITEM}}", item))
    proc = subprocess.Popen(
        [PYTHON, script_path],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
    )
    jobs[item] = proc

while jobs:
    for item, proc in list(jobs.items()):
        ret = proc.poll()
        if ret is not None:
            output = proc.stdout.read()
            print(f"{'OK' if ret==0 else 'FAIL'} {item}")
            del jobs[item]
    if jobs:
        time.sleep(5)
```

## Key Rules

1. **Inline the script** rather than importing from the project — avoids import-time side effects
2. **Write result JSON** to a known path so the controller can collect results without waiting for stdout buffering
3. **conda Python path** — use `/opt/anaconda3/bin/python3` when the venv lacks required packages (wxpy, itchat, pandas with certain libs)
4. **Kill stragglers** — if a subprocess is still running long after its peers, kill it and restart directly in the foreground
5. **Never assume all background jobs are alive** — check `poll()` before reading stdout to avoid hanging on a dead pipe

## Signs This Is Needed

- Individual task wall time × task count > 60s (Hermes polling clamp)
- Background process output shows "Command timed out" before jobs finish
- Some jobs are visibly idle (0% CPU) while others are rendering

## Alternatives Considered

| Approach | Why Not |
|----------|---------|
| Single foreground loop | Times out at 60s polling clamp |
| `nohup ... &` in shell | Output not captured, hard to poll |
| `delegate_task` subagents | Each subagent has same terminal timeout problem |
| `screen` / `tmux` | Not reliably available on macOS by default |

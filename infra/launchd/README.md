# macOS launch-on-login (LaunchAgent)

Keeps Recall's headless daemon (`recall.py --service` — API + watcher +
capture, no GUI) running across reboots. macOS only; the GUI launcher is
**not** started by this agent.

`computer.recall.daemon.plist` is a template. Install it by substituting
the three placeholders with absolute paths (launchd does not expand `~`)
and loading it:

```sh
RECALL_DIR="$(pwd)"                 # repo root
VENV_PYTHON="$RECALL_DIR/.venv/bin/python"
PLIST=~/Library/LaunchAgents/computer.recall.daemon.plist

sed -e "s|__VENV_PYTHON__|$VENV_PYTHON|g" \
    -e "s|__RECALL_DIR__|$RECALL_DIR|g" \
    -e "s|__HOME__|$HOME|g" \
    infra/launchd/computer.recall.daemon.plist > "$PLIST"

launchctl unload "$PLIST" 2>/dev/null
launchctl load "$PLIST"
launchctl list | grep computer.recall.daemon   # PID + "0" exit = healthy
```

Logs stream to `~/.recall/service.log`. To stop and remove:

```sh
launchctl unload ~/Library/LaunchAgents/computer.recall.daemon.plist
rm ~/Library/LaunchAgents/computer.recall.daemon.plist
```

#!/usr/bin/env sh
set -e

# 1) warm up a loopback server
ollama serve &
OLLSRV=$!

# 2) wait for it
until curl -s http://127.0.0.1:11434/ping >/dev/null; do sleep 1; done

# 3) pull the model
ollama pull llama3

# 4) tear down the warm-up server
kill $OLLSRV
wait $OLLSRV 2>/dev/null || true

# 5) start the real server
exec ollama serve
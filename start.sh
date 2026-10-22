#!/bin/bash
cd "$(dirname "$0")" || exit 1
(while true; do date +%H:%M:%S > .now.tmp && mv .now.tmp .now; sleep 0.1; done) &
SYNC=$!
trap 'kill $SYNC 2>/dev/null; rm -f .now .now.tmp' EXIT
python3 clock.py

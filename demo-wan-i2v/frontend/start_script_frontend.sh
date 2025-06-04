#!/usr/bin/env bash
set -e

cd /app
echo "Installing frontend dependencies…"
npm install

echo "Starting Vite dev server…"
npm run dev -- --host 0.0.0.0 --port 3000

#!/bin/bash
set -e

export TP_TOKEN="$API_TOKEN"
export TP_URL="https://example.tpondemand.com"

echo "Testing tpcli discover..."
echo "Token: ${TP_TOKEN:0:20}..."
echo "URL: $TP_URL"
echo

cd "$(dirname "$0")"
./tpcli discover -v

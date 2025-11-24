#!/bin/bash

# set-anthropic-env.sh
# Sets Anthropic API environment variables for current shell session

export ANTHROPIC_BASE_URL="https://api.z.ai/api/anthropic"
export ANTHROPIC_AUTH_TOKEN="d6f54479e1ab4a92b74c3f9051545957.PefeUXsmyMOpdGTJ"

echo "✅ Environment variables set:"
echo "   ANTHROPIC_BASE_URL = $ANTHROPIC_BASE_URL"
echo "   ANTHROPIC_AUTH_TOKEN = [HIDDEN FOR SECURITY]"  # Avoid exposing in logs

# Optional: Verify they're set
# echo "ANTHROPIC_AUTH_TOKEN = $ANTHROPIC_AUTH_TOKEN"  # Uncomment only for deb$
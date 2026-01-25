#!/bin/bash

echo "🚀 LLM Dashboard - Quick Setup Guide"
echo "===================================="
echo ""

echo "📋 Step 1: Create GitHub Personal Access Token"
echo "   1. Go to: https://github.com/settings/tokens"
echo "   2. Click 'Generate new token (classic)'"
echo "   3. Select scopes: repo, user:email"
echo "   4. Copy the token"
echo ""

echo "🔑 Step 2: Get Nebius API Key"
echo "   1. Log into Nebius: https://studio.nebius.ai"
echo "   2. Navigate to API settings"
echo "   3. Copy your API key"
echo ""

echo "☁️  Step 3: Deploy to Render"
echo "   1. Go to: https://render.com"
echo "   2. Create new Web Service"
echo "   3. Connect this repository"
echo "   4. Set these environment variables:"
echo "      - NEBIUS_API_KEY=<your_key>"
echo "      - NEBIUS_API_URL=https://api.studio.nebius.ai/v1/chat/completions"
echo "      - GITHUB_TOKEN=<your_token>"
echo "      - GITHUB_EMAIL=<your_email>"
echo "      - GITHUB_NAME=<your_name>"
echo "   5. Build Command: pip install -r requirements.txt"
echo "   6. Start Command: gunicorn app:app"
echo ""

echo "✅ Once deployed, visit your Render URL and start chatting!"
echo ""

# Optionally run locally
read -p "Would you like to test locally first? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
    echo ""
    echo "Setting up local environment..."
    
    read -p "Enter your Nebius API Key: " nebius_key
    read -p "Enter your GitHub Token: " github_token
    read -p "Enter your GitHub Email: " github_email
    read -p "Enter your GitHub Name: " github_name
    
    export NEBIUS_API_KEY=$nebius_key
    export NEBIUS_API_URL="https://api.studio.nebius.ai/v1/chat/completions"
    export GITHUB_TOKEN=$github_token
    export GITHUB_EMAIL=$github_email
    export GITHUB_NAME=$github_name
    
    echo ""
    echo "Installing dependencies..."
    pip install -r requirements.txt
    
    echo ""
    echo "🎉 Starting server on http://localhost:5000"
    python app.py
fi

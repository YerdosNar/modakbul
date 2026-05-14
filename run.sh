#!/usr/bin/env bash

# 1. 마스터 디렉터리에 venv 폴더가 없으면 최초 1회 생성
if [ ! -f "venv/bin/activate" ]; then
    echo "[System] 'venv' folder not found."
    echo "[System] Creating 'venv' folder"
    if command -v python3 &>/dev/null; then
        python3 -m venv venv
    else
        python -m venv venv
    fi
fi

# 2. Check if Virtual env is active
if [ ! -n "$VIRTUAL_ENV" ]; then
        echo "[System] Activating VENV"
        source venv/bin/activate
fi

# 3. Check package state
echo "[System] Installing packages"
pip install -r requirements.txt

# 4. Wake up the server
echo "[System] Starting the server..."
uvicorn main:app --reload

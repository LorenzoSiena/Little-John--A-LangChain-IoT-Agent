#!/bin/bash


# =======================================================
# File: curl_test.sh
# Author: Lorenzo Siena
# Date: October 2025
# Description: POST request test for Microdot web server for remote LED control (Pin 17: Red, Pin 27: Blue).
# Requirements: curl 
# License: GNU General Public License v3.0 (GPLv3) 
# =======================================================


# Your Raspberry Pi's IP address
IP="192.168.1.50"
PORT="5000"
URL="http://${IP}:${PORT}/"

echo "Starting CURL sequence. Waiting 5 seconds for initial delay..."

# Initial delay of 5 seconds
sleep 5

# --- 1. FIRST COMMAND: red ON, blue OFF ---
echo "Executing Command 1: red ON, blue OFF"
curl -X POST -H "Content-Type: application/json" -d '[{"color": "red", "status": "high"}, {"color": "blue", "status": "low"}]' "$URL"

# 2-second interval
sleep 2

# --- 2. SECOND COMMAND: eed OFF, blue ON ---
echo "Esecuzione Comando 2: red OFF, blue ON"
curl -X POST -H "Content-Type: application/json" -d '[{"color": "red", "status": "low"}, {"color": "blue", "status": "high"}]' "$URL"

# 2-second interval
sleep 2

# --- 3. THIRD COMMAND: red ON, blue ON ---
echo "Executing Command 3: red ON, blue ON"
curl -X POST -H "Content-Type: application/json" -d '[{"color": "red", "status": "high"}, {"color": "blue", "status": "high"}]' "$URL"

# 2-second interval
sleep 2

# --- 4. FOURTH COMMAND: red OFF, blue OFF ---
echo "Executing Command 4: red OFF, blue OFF"
curl -X POST -H "Content-Type: application/json" -d '[{"color": "red", "status": "low"}, {"color": "blue", "status": "low"}]' "$URL"

echo "Sequence completed."

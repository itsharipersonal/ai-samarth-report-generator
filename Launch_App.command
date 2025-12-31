#!/bin/bash
cd "$(dirname "$0")"
echo "Starting AI Samarth Report Generator..."
python3 -m streamlit run app.py

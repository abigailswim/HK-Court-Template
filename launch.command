#!/bin/bash
cd "$(dirname "$0")"
pip3 install -r requirements.txt -q --break-system-packages
open http://localhost:8501
streamlit run app.py

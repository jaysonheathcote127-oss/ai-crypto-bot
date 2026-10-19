#!/bin/zsh
cd "${0:A:h}"
exec .venv/bin/python live_dashboard.py

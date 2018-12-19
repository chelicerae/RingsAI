#!/usr/bin/env bash

export FLASK_ENV=production
export FLASK_APP=main.py
export python=venv/bin/python3.6

kill -9 $(lsof -t -i:5002)

nohup flask run --host=0.0.0.0 --port=5002 &
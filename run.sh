#!/bin/bash
uvicorn backend.api.main:app --reload --host 0.0.0.0 --port 8000 --reload

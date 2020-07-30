#!/usr/bin/env bash


python -m backend.db_init
gunicorn -k aiohttp.worker.GunicornWebWorker -b 0.0.0.0:9000 backend.app:app
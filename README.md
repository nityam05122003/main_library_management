# Student Management API (Modular)

This repository contains a modularized FastAPI application for a multi-tenant student management system. Key points:

- Separated master DB and per-college databases
- Modular routers under `app/routers`
- Models under `app/models`
- DB utilities under `app/utils`
- Config in `app/core/config.py`

Run locally:

1. Install dependencies:

```bash
python -m pip install -r requirements.txt
```

2. Start Uvicorn:

```bash
uvicorn main:app --reload
```

Adjust DB credentials in `app/core/config.py` as needed.

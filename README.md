
# semantic — lightweight semantic search demo

This repository contains a small FastAPI application that demonstrates storing items in PostgreSQL with pgvector embeddings and performing semantic search using OpenAI embeddings + pgvector distance queries.

The project is intentionally small and opinionated so it’s easy to read and extend.

## Key components

- `app/main.py` — FastAPI app factory and startup lifecycle (creates DB tables).
- `app/core/config.py` — pydantic-settings configuration (reads `.env`).
- `app/core/db.py` — SQLModel engine/session and `init_db()`.
- `app/models/item.py` — SQLModel data models (includes a `pgvector` `embedding` column).
- `app/services/embeddings.py` — wrapper around OpenAI embeddings.
- `app/services/text_builder.py` — builds the textual input used to embed an item.
- `app/api/items.py` — CRUD endpoints for items (`/items`).
- `app/api/search.py` — semantic search endpoints (`/search`, `/search/reembed`).
- `populate_items.py` — small script that posts a set of example items to the running API.
- `tests/` — pytest tests that exercise the search functionality.

## Requirements

- Python >= 3.13 (see `pyproject.toml`)
- PostgreSQL with `pgvector` extension installed and reachable by the app (default credentials are in `app/core/config.py`).
- OpenAI API key for embeddings unless you replace or stub the embedding functions for local/dev testing.

Dependencies are declared in `pyproject.toml`.

## Quickstart (development)

1. Create and activate a virtual environment (PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install the package (this will install dependencies listed in `pyproject.toml`):

```powershell
pip install .
```

3. Provide configuration via a `.env` file at the repository root or by setting environment variables. Example `.env` (DEV):

```env
OPENAI_API_KEY=sk-...            # required for embeddings
DB_HOST=localhost
DB_PORT=5432
DB_NAME=semantic
DB_USER=postgres
DB_PASSWORD=postgres
APP_ENV=dev
```

4. Run PostgreSQL with pgvector. If you have `docker-compose.yml` configured for Postgres in this repo, you can start it with:

```powershell
docker-compose up -d
```

5. Start the app:

```powershell
uvicorn app.main:app --reload
```

6. Open the docs at `http://127.0.0.1:8000/docs` (the root `/` redirects to `/docs`).

7. Populate example items (optional):

```powershell
python populate_items.py
```

Notes:
- On item creation and update the app calls the OpenAI Embeddings API and stores the vector in the `embedding` column (pgvector).
- `search` endpoint embeds the query and runs a nearest-neighbour query in PostgreSQL using the pgvector `<=>` operator.

## API overview

- POST `/items/` — create an item. Body: `name`, `title`, `description`, `tags` (list of strings). Returns created item (with embedding stored).
- GET `/items/` — list all items (no pagination in this demo).
- GET `/items/{id}` — get a single item.
- PUT `/items/{id}` — update an item (recomputes embedding if text fields change).
- DELETE `/items/{id}` — delete an item.
- POST `/search` — semantic search. Body: `query` (string), optional `min_similarity` and `tag` filter.
- POST `/search/reembed` — recompute embeddings for all items (uses current embedding model).

## Running tests

Important: the tests as provided are integration-style and assume both a working PostgreSQL (with pgvector) and access to OpenAI embeddings. Running the tests without these will likely fail.

If you want to run the tests as-is:

1. Ensure Postgres + pgvector are available and the `.env` points to the test DB.
2. Ensure `OPENAI_API_KEY` is set (the test fixture posts items which triggers embedding calls).
3. Run:

```powershell
pytest -q
```

For easier local development and CI you may prefer to:

- Stub or monkeypatch `app.services.embeddings.get_embedding_for_text` in tests to return deterministic fake embeddings.
- Or provide a test-only configuration that uses an in-memory SQLite DB (note: the current model uses pgvector and Postgres-specific types, so a SQLite test DB will need schema adjustments or mocks for embedding/search).

## Known gaps and suggestions

- Tests are not isolated: they call the real OpenAI API and expect a Postgres instance. Consider stubbing embeddings and using a test DB or dependency overrides for reliable CI.
- `app/models/base.py` is currently unused/empty — remove or implement a shared base if needed.
- No migrations (the app uses `SQLModel.metadata.create_all()`) — add Alembic for production apps.
- No authentication, rate-limiting, or input throttling — add as needed for public APIs.
- Embedding dimension is hard-coded (`Vector(1536)`) — if you change embedding models, validate dimension consistency.
- `list_items` has no pagination and could become slow with many records.

## Next steps (recommended)

1. Add a testing fixture that monkeypatches `get_embedding_for_text` so tests don't call the real OpenAI API.
2. Add a config override for tests to point to a disposable DB and create tables in the test setup.
3. Add a small script or Makefile to spin up a test Postgres with pgvector using docker-compose for CI.
4. Add embedding-dimension validation and better error messages when OpenAI responses are unexpected.

If you'd like, I can implement one or more of the recommended changes (for example: safe test stubs for embeddings + pytest fixtures) and run the test suite here.

---

License: none — adapt as you prefer.

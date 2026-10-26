# Product Site

A small Amazon-style product catalogue.

- **Frontend:** React 19 + Vite + React Router (`frontend/`)
- **Backend:** Python FastAPI + SQLAlchemy (`backend/`)
- **Database:** SQLite (`database/shop.db`, created automatically on first run)

## Run locally

You need Python 3.12+ and Node 20.19+ (or 22.12+).

### 1. Backend (port 8000)

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # optional: only needed if you want to change settings
python -m app.seed          # optional: load 5 demo categories + 25 demo products
- [x] Configuration via `.env` files, with committed `.env.example` templates
uvicorn app.main:app --reload --port 8000
```

The seed script also creates a demo account: **demo@example.com / demo1234**.
It does nothing if the database already has categories. To start fresh, stop the
server, delete `database/shop.db` and run the seed script again.

API docs: http://localhost:8000/docs

### 2. Frontend (port 5173)

In a second terminal:

```bash
cd frontend
npm install
cp .env.example .env        # optional: only needed if the backend isn't on port 8000
npm run dev
```

Open http://localhost:5173. Vite forwards `/api/*` requests to the backend on port 8000.

### 3. Configuration

Settings come from `.env` files. Each folder has a `.env.example` with safe dummy values that is
committed to git; copy it to `.env` and edit. `.env` files are ignored by git, so put real secrets only there.
Everything has a default, so the app runs without any `.env` file.

| File | Variable | Default | Purpose |
|------|----------|---------|---------|
| `backend/.env` | `DATABASE_URL` | `database/shop.db` | SQLite connection (use an absolute path if set) |
| | `CORS_ORIGINS` | `http://localhost:5173` | Frontend URLs allowed to call the API, comma-separated |
| | `SESSION_TTL_HOURS` | `12` | How long a login session lasts |
| | `DEMO_EMAIL` / `DEMO_PASSWORD` | `demo@example.com` / `demo1234` | Demo account created by the seed script |
| `frontend/.env` | `API_URL` | `http://localhost:8000` | Backend the Vite dev server forwards `/api` to |

Real environment variables override values in `backend/.env`.

### 4. First use

1. If you ran the seed script, log in with **demo@example.com / demo1234**. Otherwise click **Login** → **Register** to create an account.
2. Open **Categories** to see or add categories.
3. Click **+ Add product** to create products.

## Tests (run before pushing to production)

```bash
cd backend
source .venv/bin/activate
pytest -v
```

Without activating the venv: `cd backend && .venv/bin/pytest -v`. To run one test: `pytest -v -k <test name>`.

Tests use their own database (`database/test_shop.db`), which is reset before each test. All 5 must pass:

| # | Test | What it checks |
|---|------|----------------|
| 1 | `test_1_register_login_and_session` | Register, duplicate email rejected, wrong password rejected, login gives a working session |
| 2 | `test_2_writes_blocked_without_valid_session` | Create/update with no token, a fake token, or a logged-out token returns 401 |
| 3 | `test_3_server_side_validation` | Blank name, price ≤ 0, negative stock, unknown category, duplicate category, bad email, short password are all rejected |
| 4 | `test_4_create_and_update_product` | Products can be created and updated by a logged-in user; updating a missing product returns 404 |
| 5 | `test_5_listing_search_filter_pagination` | Listing supports search, category filter, price range, and pagination |

You may see one warning suggesting `httpx2` instead of `httpx`. It is harmless and doesn't affect the results.

## How auth works

- Passwords are hashed with PBKDF2-SHA256 (Python standard library).
- Login/register creates a random session token stored in the `sessions` table (valid for `SESSION_TTL_HOURS`, default 12 hours).
- The frontend sends it as `Authorization: Bearer <token>`.
- Every create/update endpoint checks the token against the database. If the session is missing, expired, or logged out, the server returns **401** and nothing is written.
- When the frontend gets a 401, it clears the stored token and sends the user to the login page.

## API

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/auth/register` | – | Create account, returns token |
| POST | `/api/auth/login` | – | Log in, returns token |
| POST | `/api/auth/logout` | ✔ | End session |
| GET | `/api/auth/me` | ✔ | Current user |
| GET | `/api/categories` | – | List categories |
| POST | `/api/categories` | ✔ | Create category |
| GET | `/api/products` | – | List with `search`, `category_id`, `min_price`, `max_price`, `page`, `page_size` |
| GET | `/api/products/{id}` | – | One product |
| POST | `/api/products` | ✔ | Create product |
| PUT | `/api/products/{id}` | ✔ | Update product |

## Project structure

```
database/         # SQLite files (shop.db, test_shop.db), not committed to git
backend/
  .env.example    # backend settings template (copy to .env)
  app/
    main.py       # routes
    config.py     # settings from backend/.env (see .env.example)
    auth.py       # password hashing + session check
    models.py     # SQLAlchemy tables
    schemas.py    # Pydantic validation rules
    database.py   # SQLite connection (points to database/shop.db)
    seed.py       # demo data: 5 categories, 25 products, demo user
  tests/          # the 5 pre-production tests
frontend/
  .env.example    # frontend settings template (copy to .env)
  src/
    api.js        # fetch wrapper, handles token + 401
    App.jsx       # nav + routes
    pages/        # Login, Products, ProductForm, Categories
```

## Progress

**Done (v0.1, 2026-10-27)**
- [x] Categories: list and create
- [x] Products: create, edit, server-side validation, errors shown next to each form field
- [x] Product listing: search, category filter, price range, pagination (filters kept in the URL)
- [x] Register / login / logout with sessions stored in the database
- [x] All writes blocked without a valid session
- [x] 5 backend tests, all passing
- [x] SQLite moved to its own `database/` folder; seed script with 5 categories and 25 demo products
- [x] Configuration via `.env` files, with committed `.env.example` templates

**Possible next steps**
- [ ] Product images
- [ ] Product detail page
- [ ] Delete products and categories
- [ ] Sorting (price, newest)
- [ ] Cart / orders
- [ ] Roles (admin vs. customer) so only admins can edit the catalogue
- [ ] Frontend tests

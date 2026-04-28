# 🍰 Baking E-Commerce Backend

A production-grade REST API for a baking e-commerce platform built with **FastAPI** and **MongoDB**.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Framework | FastAPI |
| Database | MongoDB (via Motor async driver) |
| Auth | JWT (python-jose) + bcrypt (passlib) |
| Config | pydantic-settings |
| Testing | pytest + httpx |

---

## Project Structure

```
baking-ecommerce-backend/
├── app/
│   ├── main.py              # FastAPI app factory + lifespan hooks
│   ├── core/
│   │   ├── config.py        # Settings loaded from .env
│   │   └── security.py      # Password hashing & JWT helpers
│   ├── models/              # Database document models (added Week 2+)
│   ├── schemas/             # Pydantic request/response schemas (Week 2+)
│   ├── api/
│   │   └── v1/
│   │       └── __init__.py  # Central API router
│   └── database/
│       └── connection.py    # Motor client + collection helpers
├── .env                     # Local secrets (git-ignored)
├── .env.example             # Template — safe to commit
├── requirements.txt
└── README.md
```

---

## Quick Start

### 1. Clone & enter the project
```bash
git clone <your-repo-url>
cd baking-ecommerce-backend
```

### 2. Create a virtual environment
```bash
python -m venv venv

# macOS / Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment
```bash
cp .env.example .env
# Edit .env with your local values (MongoDB URL, secret key, etc.)
```

### 5. Start MongoDB locally
Make sure MongoDB is running on `localhost:27017`.  
If you have the MongoDB Community Server installed:
```bash
# macOS (Homebrew)
brew services start mongodb-community

# Linux (systemd)
sudo systemctl start mongod

# Windows — start the MongoDB service from Services panel
```

### 6. Run the server
```bash
uvicorn app.main:app --reload
```

The API will be available at:
- **Swagger UI** → http://127.0.0.1:8000/docs
- **ReDoc**       → http://127.0.0.1:8000/redoc
- **Health check** → http://127.0.0.1:8000/health

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_NAME` | `Baking E-Commerce API` | Application display name |
| `DEBUG` | `True` | Enable debug logging |
| `MONGODB_URL` | `mongodb://localhost:27017` | MongoDB connection string |
| `MONGODB_DB_NAME` | `baking_ecommerce` | Database name |
| `SECRET_KEY` | *(set this!)* | JWT signing key — change before production |
| `ALGORITHM` | `HS256` | JWT algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Token TTL in minutes |
| `ALLOWED_ORIGINS` | `http://localhost:3000,...` | Comma-separated CORS origins |

---

## Auth Endpoints

| Method | URL | Auth required | Description |
|--------|-----|---------------|-------------|
| POST | `/api/v1/auth/register` | No | Create a new account |
| POST | `/api/v1/auth/login` | No | Login, receive JWT token |
| GET | `/api/v1/auth/me` | Yes (Bearer token) | Get your own profile |
| GET | `/api/v1/auth/me/admin-test` | Yes (admin only) | Test admin access |

### How to use the token

After login, copy the `access_token` from the response and include it in all protected requests:
```
Authorization: Bearer <your_token_here>
```

In Swagger UI (`/docs`) click **Authorize** and paste the token there.

---

## Setup scripts

```bash
# Create MongoDB indexes (run once after setup)
python setup_indexes.py

# Create your first admin user interactively
python create_admin.py
```

---

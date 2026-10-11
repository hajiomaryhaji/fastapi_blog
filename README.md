# FastAPI Blog

This is a learning project for building a maintainable FastAPI application with
an API layer, application services, domain entities, and infrastructure
repositories.

## Run locally

```bash
uv sync
cp .env.example .env  # replace JWT_SECRET_KEY with a random value
uv run fastapi dev main.py
```

Open the interactive API documentation at <http://127.0.0.1:8000/docs>.

The first local run creates `database/blog.db`. It is ignored by Git. In a
production deployment, replace `AUTO_CREATE_TABLES` with Alembic migrations.

## Current API

- `POST /api/v1/users` creates a user and hashes the password with Argon2.
- `POST /api/v1/auth/login` verifies credentials and returns a JWT bearer token.
- `GET /api/v1/users` lists users without exposing password hashes.
- `GET /api/v1/users/me` returns the authenticated user.
- `PATCH /api/v1/users/me` updates the authenticated user's profile.
- `DELETE /api/v1/users/me` deactivates the authenticated user (soft delete).
- `POST /api/v1/posts/` creates a post for the authenticated user.
- `PATCH /api/v1/posts/{post_id}` updates only fields supplied by its owner.
- `GET /api/v1/posts/` lists posts with their authors.

Post creation deliberately accepts only post data. The client cannot choose the
owner by sending a `user_id`; the route gets `current_user` from the auth
dependency and passes `current_user.id` to the service. Protected endpoints use
OAuth2 password login to issue a JWT bearer token. The login form uses the
user's email as `username`:

```bash
TOKEN=$(curl -s -X POST http://127.0.0.1:8000/api/v1/auth/login \
  -H 'content-type: application/x-www-form-urlencoded' \
  -d 'username=haji@example.com&password=change-me-123' | jq -r .access_token)
```

Send the token as a Bearer token to protected endpoints:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/posts/ \
  -H "Authorization: Bearer $TOKEN" \
  -H 'content-type: application/json' \
  -d '{"title":"My first post","content":"This is the content of my first blog post."}'
```

To update a post, use the same token:

```bash
curl -X PATCH http://127.0.0.1:8000/api/v1/posts/<post-id> \
  -H "Authorization: Bearer $TOKEN" \
  -H 'content-type: application/json' \
  -d '{"title":"An updated title"}'
```

Example user creation:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/users \
  -H 'content-type: application/json' \
  -d '{"name":"Haji Omary Haji","email":"haji@example.com","password":"change-me-123"}'
```

Set `JWT_SECRET_KEY` in `.env` to a long random value in deployed
environments. Do not use the example value in production.

## Structure

```text
app/
├── api/                 # HTTP routes and dependency wiring
├── application/         # DTOs and use-case services
├── core/                # settings, database, security
├── domain/              # framework-independent entities and interfaces
└── infrastructure/      # SQLAlchemy models and repository implementations
```

## Suggested learning order

1. Add Alembic and an initial migration; stop relying on `create_all` outside
   local development.
2. Add short-lived refresh-token rotation if the application needs long-lived
   sessions.
3. Implement posts through the same service/repository flow, including
   pagination, ownership checks, and transactions.
4. Add pytest tests for services, repositories, and API behavior.
5. Add Ruff, type checking, CI, structured logging, and health/readiness
   endpoints.

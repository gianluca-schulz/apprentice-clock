# Apprentice Clock

A web application for tracking apprentices' work hours. It requires the user to write a daily report for their training log before clocking out.

## Problem

Daily reports are easy to forget. Often nobody checks them right away, so apprentices end up writing the reports for several missing weeks at once. Apprentice Clock makes the report a condition for clocking out, so the training log stays up to date.

## Who it is for

- **Apprentices**, who have to clock in and out anyway and no longer need to remember the reports separately.

## Features (first version)

- Sign-up and login
- Clock-in and clock-out functions
- A required daily report before clocking out
- Download of the written reports

## Out of scope for now

- Generating a weekly report as a PDF from the daily reports
- Signing of reports by the company

## Stack

- Backend: Python 3.13 with FastAPI, managed with `uv`
- Database: PostgreSQL
- Frontend: Next.js with TypeScript
- Docker for running the backend as a container

## Data

The data is stored in a database. Each entry has these fixed fields:

- Entry ID
- Clock-in
- Clock-out
- User ID
- Daily report

## Run it locally

The backend currently has one endpoint, a health check.

1. Install [`uv`](https://docs.astral.sh/uv/getting-started/installation/). It also downloads the right Python version for the project.
2. Go to the backend folder:

   ```bash
   cd backend
   ```

3. Install the dependencies:

   ```bash
   uv sync
   ```

4. Start the development server. It reloads automatically when you change a file:

   ```bash
   uv run fastapi dev
   ```

5. Open the health check in your browser: <http://localhost:8000/api/v1/health>. It should answer with `{"status":"ok"}`. The API docs are at <http://localhost:8000/docs>.
6. Optional: call the health check from a second terminal with `curl`. The option `-i` also shows the status code and the headers of the response:

   ```bash
   curl -i http://localhost:8000/api/v1/health
   ```

## Run the tests

The tests use [`pytest`](https://docs.pytest.org/). They live in `backend/tests/`, split into `unit/` and `integration/`. The test client calls the app directly, so you do not need to start the server first.

1. Go to the backend folder and install the dependencies, if you have not done so yet:

   ```bash
   cd backend
   uv sync
   ```

2. Run all tests. The option `-v` shows the name and the result of every test:

   ```bash
   uv run pytest -v
   ```

3. A passing run ends with a line like `1 passed`. If a test fails, pytest shows which `assert` failed and the expected and the actual value.

## Run the database

PostgreSQL runs in a container, described in `docker-compose.yml` in the root folder. You need [Docker Desktop](https://www.docker.com/products/docker-desktop/), and it must be running. The backend does not use the database yet, but it will once the user model is added.

1. In the root folder, start the database. The option `-d` runs it in the background:

   ```bash
   docker compose up -d
   ```

2. Check the status. Wait until the column `STATUS` shows `healthy`. That is the health check of the service passing:

   ```bash
   docker compose ps
   ```

3. Connect to the database with `psql`, the command line client of PostgreSQL. It runs inside the container, so you do not have to install it. Leave it again with `\q`:

   ```bash
   docker compose exec postgres psql -U apprentice-clock -d apprentice-clock
   ```

4. Stop the database. The data stays in the named volume `apprentice-clock_postgresql`, so it is still there after the next `docker compose up -d`:

   ```bash
   docker compose down
   ```

5. To start from an empty database, delete the volume as well. The option `-v` removes the volume and with it all data, so only do this on your computer:

   ```bash
   docker compose down -v
   ```

Port 5433 on your computer is mapped to port 5432 in the container. That is why the connection from the backend uses `localhost:5433`.

## Configure the backend

The backend reads its settings from environment variables, or from the file `backend/.env`. Right now there is one setting, `DATABASE_URL`, the address of the database.

1. Go to the backend folder and copy the example file. `.env.example` is committed to Git, `.env` is ignored by Git, so your own values never end up in the repository:

   ```bash
   cd backend
   cp .env.example .env
   ```

2. Open `backend/.env` and replace the placeholders with the values from `docker-compose.yml`: user, password, database name and the port on your computer. The format of the URL is:

   ```
   postgresql+psycopg://<user>:<password>@<host>:<port>/<database>
   ```

3. If `DATABASE_URL` is missing, creating the settings fails with `Field required`. That is on purpose: the app should not start with a wrong or guessed database.

The password in `docker-compose.yml` only protects a throwaway database on your own computer. A password for production never goes into Git. It is set as an environment variable on the server.

## Run the migrations

The tables of the database are created and changed only through migrations, never directly from the models. A migration is a versioned script in `backend/migrations/versions/`. [Alembic](https://alembic.sqlalchemy.org/) runs them in order and remembers in the table `alembic_version` which one a database has already received. The database must be running and `backend/.env` must be set up, as described above. All commands run in the backend folder.

1. Bring the database up to date. `head` means the newest migration. Alembic runs every migration the database does not have yet, so this is also the command for a new, empty database:

   ```bash
   cd backend
   uv run alembic upgrade head
   ```

2. Check which migration the database is at. The output shows the revision ID, and `(head)` means it is the newest one:

   ```bash
   uv run alembic current
   ```

3. To change the schema, first change the model in `backend/app/models/`. Then let Alembic compare the models with the database and write a new migration. The option `-m` is a short description of the change:

   ```bash
   uv run alembic revision --autogenerate -m "add email_confirmed_at to users"
   ```

   This only creates the file, it does not change the database. Open the new file in `backend/migrations/versions/` and read `upgrade()` and `downgrade()` before you continue. Autogenerate is a helper and misses some changes, such as a renamed column, which it sees as one column removed and another added. If the file is right, run step 1 to apply it.

4. To undo the last migration, run its `downgrade()`. Afterwards, check the tables in `psql`:

   ```bash
   uv run alembic downgrade -1
   ```

   Be careful: a downgrade that drops a table or a column deletes the data in it for good. Use it on your own computer, not on a database with real data. To fix a mistake there, write a new migration instead.

5. The migration files are generated and use the old style of Python typing. That is why `ruff` ignores some rules in `backend/migrations/`, and why you run `uv run ruff format .` after generating a migration.

## Run it in Docker

The backend also runs as a container. You need [Docker Desktop](https://www.docker.com/products/docker-desktop/), and it must be running.

1. Go to the backend folder:

   ```bash
   cd backend
   ```

2. Build the image. The option `-t` gives it a name, and the dot at the end is the folder with the `Dockerfile`:

   ```bash
   docker build -t apprentice-clock-backend .
   ```

3. Start a container from the image. The option `-p` maps port 8000 on your computer to port 8000 in the container, and `--rm` removes the container when it stops:

   ```bash
   docker run --rm -p 8000:8000 apprentice-clock-backend
   ```

4. In a second terminal, call the health check. It should answer with `{"status":"ok"}`:

   ```bash
   curl -i http://localhost:8000/api/v1/health
   ```

5. Stop the container with `Ctrl + C` in the first terminal.

If port 8000 is already in use, for example by `uv run fastapi dev`, stop that server first or choose another port on your computer, such as `-p 9000:8000`. Then call `http://localhost:9000/api/v1/health`.

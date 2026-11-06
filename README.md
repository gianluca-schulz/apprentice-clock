# Apprentice Clock

A web application for tracking apprentices' work hours. It requires the user to write a daily report for their training log before clocking out.

## Problem

Daily reports are easy to forget. Often nobody checks them right away, so apprentices end up writing the reports for several missing weeks at once. Apprentice Clock makes the report a condition for clocking out, so the training log stays up to date.

## Who it is for

- **Apprentices**, who have to clock in and out anyway and no longer need to remember the reports separately.
- **Companies**, who no longer need to ask apprentices for their reports. The reports are already in the database and can be signed quickly.

## Features (first version)

- Clock-in and clock-out functions
- A required daily report before clocking out
- Every user has their own unique ID

## Out of scope for now

- Login function (planned for a later phase)
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

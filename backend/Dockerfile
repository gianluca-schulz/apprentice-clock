FROM python:3.13-slim
WORKDIR /app
COPY --from=ghcr.io/astral-sh/uv:0.13.6 /uv /bin/
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev
ENV PATH="/app/.venv/bin:$PATH"
COPY /scripts/startup.sh /app/scripts/startup.sh
COPY alembic.ini /app/alembic.ini
COPY /migrations /app/migrations
COPY /app /app/app
CMD ["bash", "scripts/startup.sh"]
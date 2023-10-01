FROM python:3.11-slim-bullseye AS python-base
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    PYSETUP_PATH="/opt/pysetup" \
    VENV_PATH="/opt/pysetup/.venv"

ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

# builder-base is used to build dependencies
FROM python-base AS builder-base
RUN apt-get update \
    # dependencies for building Python packages
    && apt-get install -y build-essential \
    # psycopg2 dependencies
    && apt-get install -y libpq5 \
    # Additional dependencies
    && apt-get install -y telnet netcat \
    # Install curl and vim
    && apt-get install -y curl vim \
    # cleaning up unused files
    && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
    && rm -rf /var/lib/apt/lists/*

SHELL ["/bin/bash", "-o", "pipefail", "-c"]
RUN curl -sSL https://install.python-poetry.org | POETRY_HOME=${POETRY_HOME} python3 - && \
    chmod a+x /opt/poetry/bin/poetry

WORKDIR $PYSETUP_PATH
COPY poetry.lock ./pyproject.toml ./
RUN poetry install --no-root --only main  # respects

FROM python-base as production
ENV APP_ENV=Production

RUN apt-get update \
    && apt-get install -y telnet netcat

COPY --from=builder-base $VENV_PATH $VENV_PATH

COPY compose/api/entrypoint /entrypoint
RUN sed -i 's/\r$//g' /entrypoint
RUN chmod +x /entrypoint

COPY compose/api/start_prod /start_prod
RUN sed -i 's/\r$//g' /start_prod
RUN chmod +x /start_prod

COPY .. /app

WORKDIR /app

ENTRYPOINT ["/entrypoint"]

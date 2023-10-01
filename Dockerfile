FROM python:3.11-slim-bookworm
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    PYSETUP_PATH="/opt/pysetup" \
    VENV_PATH="/opt/pysetup/.venv" \
    APP_ENV="Development"

ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

RUN apt-get update \
    # dependencies for building Python packages
    && apt-get install -y build-essential \
    # psycopg2 dependencies
    && apt-get install -y libpq-dev \
    # Additional dependencies \
    && apt-get install telnet netcat-openbsd netcat-traditional inetutils-telnet \
    # Install curl and vim
    && apt-get install -y curl vim \
    # cleaning up unused files
    && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
    && rm -rf /var/lib/apt/lists/*

SHELL ["/bin/bash", "-o", "pipefail", "-c"]
RUN curl -sSL https://install.python-poetry.org | POETRY_HOME=${POETRY_HOME} python3 - && \
    chmod a+x /opt/poetry/bin/poetry

WORKDIR $PYSETUP_PATH
COPY poetry.lock ../pyproject.toml ./
RUN poetry install --no-root --only main

COPY compose/api/entrypoint /entrypoint
RUN sed -i 's/\r$//g' /entrypoint
RUN chmod +x /entrypoint

COPY compose/api/start /start
RUN sed -i 's/\r$//g' /start
RUN chmod +x /start

WORKDIR /app
COPY .. .

ENTRYPOINT ["/entrypoint"]

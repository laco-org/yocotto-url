FROM python:3.8.2
ENV POETRY_VIRTUALENVS_CREATE=false
EXPOSE 8080

RUN python -m pip install gunicorn poetry

WORKDIR /tmp/myapp
COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root --no-dev

RUN useradd --home-dir /app --create-home app
USER app
WORKDIR /app

COPY . .
CMD ["gunicorn", "-c", "gunicorn.conf.py", "--reload", "--bind", "0.0.0.0:8080", "yocotto_url.application:setup_app()"]

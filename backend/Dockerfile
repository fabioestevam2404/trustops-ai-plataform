FROM python:3.12-slim

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends git curl \
    && rm -rf /var/lib/apt/lists/*

RUN curl -sL https://github.com/gitleaks/gitleaks/releases/download/v8.30.1/gitleaks_8.30.1_linux_x64.tar.gz \
        | tar -xz -C /usr/local/bin gitleaks \
    && curl -sL https://github.com/aquasecurity/trivy/releases/download/v0.74.0/trivy_0.74.0_Linux-64bit.tar.gz \
        | tar -xz -C /usr/local/bin trivy \
    && chmod +x /usr/local/bin/gitleaks /usr/local/bin/trivy

COPY requirements/ requirements/
RUN pip install --no-cache-dir -r requirements/dev.txt

COPY pyproject.toml .
COPY app/ app/
COPY tests/ tests/
COPY alembic/ alembic/
COPY alembic.ini .

RUN useradd --create-home appuser \
    && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

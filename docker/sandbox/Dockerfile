# Air-gapped sandbox for execution-based semantic-correctness verification.
# Build context is the repository root (see docker-compose.yml).
FROM python:3.11.9-slim
ENV PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
WORKDIR /sandbox
COPY pyproject.toml README.md ./
COPY halluguard ./halluguard
COPY experiments ./experiments
RUN pip install --no-cache-dir . pytest==8.2.2
RUN useradd --create-home --shell /usr/sbin/nologin runner
USER runner
ENTRYPOINT ["python", "-m", "experiments.verify_scr"]

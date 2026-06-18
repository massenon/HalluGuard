# docker/sandbox/Dockerfile
# Air-gapped execution sandbox for Semantic Correctness Rate (SCR) verification.
# Used to safely run unit tests against repaired snippets and to handle the
# adversarial benchmark packages without risk of live malware execution.
#
# Reproduces the methodology in Section 5.2.2 and Algorithm 5
# (Execution-Based SCR Verification).

FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Python 3.11 + Node.js 20 LTS, per the manuscript's stated sandbox spec
RUN apt-get update && apt-get install -y --no-install-recommends \
    software-properties-common curl ca-certificates gnupg \
    && add-apt-repository ppa:deadsnakes/ppa -y \
    && apt-get update && apt-get install -y --no-install-recommends \
        python3.11 python3.11-venv python3-pip \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /sandbox

COPY requirements-sandbox.txt /sandbox/requirements-sandbox.txt
RUN pip3 install --no-cache-dir -r requirements-sandbox.txt

COPY . /sandbox

# CRITICAL: no outbound network access at runtime (enforced via
# docker-compose.yml `network_mode: none`). This prevents any
# adversarial benchmark package from exfiltrating data or reaching
# a live command-and-control server during evaluation.

ENTRYPOINT ["python3", "/sandbox/experiments/verify_scr.py"]

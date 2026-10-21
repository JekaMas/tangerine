FROM python:3.12.12-slim-bookworm@sha256:593bd06efe90efa80dc4eee3948be7c0fde4134606dd40d8dd8dbcade98e669c
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg=7:5.1.9-0+deb12u1 espeak-ng=1.51+dfsg-10+deb12u2 libsndfile1 build-essential cmake && rm -rf /var/lib/apt/lists/*
ARG TARGETARCH
COPY services/speech/requirements.${TARGETARCH}.lock /tmp/requirements.lock
RUN pip install --no-cache-dir --require-hashes --extra-index-url https://download.pytorch.org/whl/cpu -r /tmp/requirements.lock
COPY services/speech/requirements.diagnostics.${TARGETARCH}.lock /tmp/diagnostics.lock
RUN pip install --no-cache-dir --require-hashes -r /tmp/diagnostics.lock
ENV PYTHONDONTWRITEBYTECODE=1 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 TANGERINE_MODEL_DIR=/models NUMBA_CACHE_DIR=/tmp/numba-cache
WORKDIR /app
RUN mkdir -p /models && chown 65532:65532 /models
COPY services/speech/ ./
USER 65532:65532
EXPOSE 8090
CMD ["python", "-B", "server.py"]

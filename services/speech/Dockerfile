FROM python:3.14.7-slim-bookworm@sha256:82bc3c539b8813ada9d68c63b40158fa002f7f33de9bf3312a3dfdc0620dff56
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg=7:5.1.9-0+deb12u1 && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY services/speech/ ./
USER 65532:65532
EXPOSE 8090
CMD ["python", "-B", "server.py"]

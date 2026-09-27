FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    SDL_AUDIODRIVER=dummy \
    PYTHONPATH=/app

RUN apt-get update && apt-get install -y --no-install-recommends \
        libfreetype6 \
        libglib2.0-0 \
        libsdl2-2.0-0 \
        libsdl2-image-2.0-0 \
        libsdl2-mixer-2.0-0 \
        libsdl2-ttf-2.0-0 \
        libx11-6 \
        libxext6 \
        fonts-dejavu-core \
        xvfb \
        xauth \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .
COPY mouse_gaze ./mouse_gaze
COPY assets ./assets
COPY scripts ./scripts

RUN useradd --create-home --uid 1000 appuser \
    && chown -R appuser:appuser /app
USER appuser

# Virtual display so the process can run on a server with no monitor.
# To use a real display instead, override this command and set DISPLAY.
CMD ["xvfb-run", "-a", "--server-args=-screen 0 960x720x24", "python", "main.py"]

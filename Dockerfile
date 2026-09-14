# ============================================================
# School_Timetable_Fresh
# Python + CPLEX + Faker + Plotly
# ============================================================

FROM python:3.10-slim

# ------------------------------------------------------------
# Environment
# ------------------------------------------------------------

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app


# ------------------------------------------------------------
# System dependencies
# ------------------------------------------------------------

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        nginx \
        wget \
    && rm -rf /var/lib/apt/lists/*


# ------------------------------------------------------------
# Python requirements
# ------------------------------------------------------------

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt


# ------------------------------------------------------------
# Project files
# ------------------------------------------------------------

COPY config.py .

COPY src/ ./src/


# Create output directory

RUN mkdir -p /app/output


# ------------------------------------------------------------
# Generate timetable
# ------------------------------------------------------------

RUN python -m src.data_generation.generate_data \
    && python -m src.model.build_model \
    && python -m src.visualization.build_dashboard


# ------------------------------------------------------------
# Configure nginx
# ------------------------------------------------------------

RUN rm -f /etc/nginx/sites-enabled/default

COPY Deploy/nginx/default.conf \
     /etc/nginx/conf.d/default.conf


# ------------------------------------------------------------
# Expose HTTP
# ------------------------------------------------------------

EXPOSE 80


# ------------------------------------------------------------
# Start nginx
# ------------------------------------------------------------

CMD ["nginx", "-g", "daemon off;"]
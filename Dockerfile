# -------------- STAGE 1: BUILDER --------------
FROM python:3.12-slim AS builder

WORKDIR /build

# Install only what we need for the wheel build
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt

# -------------- STAGE 2: PRODCUTION --------------
FROM python:3.12-slim

# Non-root user for security
RUN addgroup --system app && adduser --system --ingroup app app

WORKDIR /app

# Copy pre-built wheels from builder and install without downloading
COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir --no-index --find-links /wheels /wheels/*.whl \
    && rm -rf /wheels

# Copy application source: app.py for function, templates/index.html for frontend
COPY app.py .
COPY templates/ templates/

# Drop to non-root
USER app

EXPOSE 5000

ENV FLASK_ENV=production

CMD ["python", "app.py"]

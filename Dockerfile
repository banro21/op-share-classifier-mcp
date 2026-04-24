FROM python:3.12-slim AS builder
WORKDIR /app
RUN pip install uv
COPY pyproject.toml .
COPY src/ src/
RUN uv pip install --system --no-cache-dir .

FROM python:3.12-slim
WORKDIR /app
RUN adduser --disabled-password --gecos "" --uid 10001 appuser
COPY --from=builder /usr/local/lib/python3.12 /usr/local/lib/python3.12
COPY --from=builder /usr/local/bin /usr/local/bin
COPY src/ src/
USER appuser
EXPOSE 8080
CMD ["python", "-m", "op_share_classifier"]

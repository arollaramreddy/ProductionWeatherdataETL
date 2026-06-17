FROM apache/superset:5.0.0

USER root
RUN /app/.venv/bin/pip install --no-cache-dir psycopg2-binary redis

COPY superset_config.py /app/pythonpath/superset_config.py
ENV SUPERSET_CONFIG_PATH=/app/pythonpath/superset_config.py

USER superset

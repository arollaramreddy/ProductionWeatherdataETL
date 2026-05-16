FROM apache/superset:5.0.0

USER root
RUN uv pip install --python /app/.venv/bin/python psycopg2-binary redis

COPY superset_config.py /app/pythonpath/superset_config.py
ENV SUPERSET_CONFIG_PATH=/app/pythonpath/superset_config.py

USER superset

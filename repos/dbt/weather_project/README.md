# Weather dbt Project

This dbt project transforms raw Weatherstack observations in Postgres into analytics-ready tables.

## Models

| Model | Purpose |
| --- | --- |
| `silver` | De-duplicates raw weather observations and standardizes timestamp fields. |
| `gold` | Aggregates daily city-level weather metrics for Superset dashboards. |

Run from `repos/`:

```bash
docker compose run --rm dbt run
docker compose run --rm dbt test
docker compose run --rm dbt source freshness
```

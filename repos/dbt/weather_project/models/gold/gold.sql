select
    city,
    date(weather_time_local) as weather_date,
    count(*) as observation_count,
    round(avg(temperature)::numeric, 2) as avg_temperature,
    round(avg(wind_speed)::numeric, 2) as avg_wind_speed,
    max(weather_time_local) as latest_observation_at
from {{ ref('silver') }}
group by 1, 2
order by 1, 2

with source_data as (
    select *
    from {{ source('weatherstack', 'weather_data') }}
),

deduplicated as (
    select
        *,
        row_number() over (
            partition by city, time
            order by inserted_at desc, id desc
        ) as row_number
    from source_data
)

select
    id,
    city,
    temperature,
    weather_description,
    wind_speed,
    time as weather_time_local,
    inserted_at as inserted_at_utc,
    inserted_at + (nullif(utc_offset, '')::numeric * interval '1 hour') as inserted_at_local
from deduplicated
where row_number = 1

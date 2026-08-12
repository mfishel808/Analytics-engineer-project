{{ config(
    materialized='table'
) }}

select
genre_id,
genre_name,
loaded_at

from {{ source('raw', 'genres') }}

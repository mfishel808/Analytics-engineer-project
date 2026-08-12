{{ config(
    materialized='incremental',
    unique_key=['movie_id', 'genre_id'],
    incremental_strategy='merge'
) }}

select
    movie_id,
    genre_id,
    loaded_at

from {{ source('raw', 'movie_genres') }}

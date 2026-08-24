{{
    config(
        materialized='incremental',
        unique_key='movie_id',
        incremental_strategy='merge',
        on_schema_change='append_new_columns'
    )
}}

select
    movie_id,
    title,
    original_title,
    release_date,
    original_language,
    average_rating,
    rating_count,
    popularity,
    case when revenue = 0 then null else revenue end revenue,
    case when budget = 0 then null else budget end budget,
    runtime,
    adult,
    loaded_at

from {{ source('raw', 'movies') }}

{{
    config(
        materialized='incremental',
        incremental_strategy='merge',
        unique_key=['movie_id', 'company_id'],
        on_schema_change='append_new_columns'
    )
}}

select
    movie_id,
    company_id,
    loaded_at

from {{ source('raw', 'movie_studios') }}


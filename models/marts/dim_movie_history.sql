{{ config(
    materialized='table'
) }}

select movie_id,
    average_rating,
    rating_count,
    popularity,
    revenue,
    cast(dbt_valid_from as date) as date_entered
from {{ref('movies_snapshot')}}
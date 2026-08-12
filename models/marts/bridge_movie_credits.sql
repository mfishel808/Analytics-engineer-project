{{
    config(
        materialized='incremental',
        unique_key='credit_id',
        incremental_strategy='merge'
    )
}}

select
credit_id,
movie_id,
person_id,
credit_type,
character_name,
department,
job,
cast_order
loaded_at
from {{source('raw', 'movie_credits')}}
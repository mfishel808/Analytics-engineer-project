{{
    config(
        materialized='incremental',
        unique_key='person_id',
        incremental_strategy='merge'
    )
}}

select
 person_id,
 person_name,
 known_for_department,
 gender,
 popularity,
 profile_path,
 loaded_at

from {{ source('raw', 'people') }}

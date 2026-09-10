{{
    config(
        materialized='incremental',
        incremental_strategy='merge',
        unique_key='person_id',
        on_schema_change='append_new_columns'
    )
}}

with raw_people as (

    select
        person_id,
        person_name,
        known_for_department,
        gender,
        popularity,
        birthday,
        deathday,
        place_of_birth,
        loaded_at

    from {{ source('raw', 'people') }}

),

{% if is_incremental() %}

existing_people as (

    select
        person_id,
        birthday,
        deathday,
        place_of_birth

    from {{ this }}

),

{% endif %}

final as (

    select

        r.person_id,
        r.person_name,
        r.known_for_department,
        r.gender,
        r.popularity,

        {% if is_incremental() %}

        coalesce(
            r.birthday,
            e.birthday
        ) as birthday,

        coalesce(
            r.deathday,
            e.deathday
        ) as deathday,

        coalesce(
            r.place_of_birth,
            e.place_of_birth
        ) as place_of_birth,

        {% else %}

        r.birthday,
        r.deathday,
        r.place_of_birth,

        {% endif %}

        r.loaded_at

    from raw_people as r

    {% if is_incremental() %}

    left join existing_people as e
        on r.person_id = e.person_id

    {% endif %}

)

select *
from final
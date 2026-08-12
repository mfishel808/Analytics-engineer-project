{{ config(
    materialized='table'
) }}

with people_history as (

    select
        person_id,
        popularity,
        dbt_valid_from,

        first_value(popularity) over (
            partition by person_id
            order by dbt_valid_from
            rows between unbounded preceding and unbounded following
        ) as first_popularity,


        lag(popularity) over (
            partition by person_id
            order by dbt_valid_from
        ) as previous_popularity,


        row_number() over (
            partition by person_id
            order by dbt_valid_from desc
        ) as version_rank

    from {{ ref('people_snapshot') }}

),

latest_history as (

    select *
    from people_history
    where version_rank = 1

),

final as (

    select
        m.person_id,
        m.person_name,
        m.known_for_department,
        m.gender,

        -- Current values
        m.popularity,

        -- First recorded values
        h.first_popularity,

        -- Previous recorded values
        coalesce(
            h.previous_popularity,
            m.popularity
        ) as previous_popularity,

        -- Change since first observation
        m.popularity
            - h.first_popularity
            as popularity_change_since_first,

        -- Change since previous observation
        m.popularity
            - coalesce(
                h.previous_popularity,
                m.popularity
            )
            as popularity_change_since_last,

        m.loaded_at

    from {{ ref('stg_people') }} as m

    left join latest_history as h
        on m.person_id = h.person_id

)

select *
from final


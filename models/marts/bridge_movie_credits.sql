{{ config(
    materialized='table'
) }}

select
credit_id,
mc.movie_id,
mc.person_id,
credit_type,
character_name,
department,
job,
cast_order,
mc.loaded_at
from {{ref('stg_bridge_movie_credits')}} as mc
inner join {{ref('stg_movies')}} as m on m.movie_id = mc.movie_id
inner join {{ref('stg_people')}} as p on mc.person_id = p.person_id
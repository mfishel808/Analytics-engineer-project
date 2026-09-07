{{ config(
    materialized='table'
) }}

select
    ms.movie_id,
    ms.company_id,
    ms.loaded_at

from {{ref('stg_bridge_movie_company')}} as ms
inner join {{ref('stg_movies')}} as m on ms.movie_id = m.movie_id
inner join {{ref('stg_companies')}} as c on ms.company_id = c.company_id

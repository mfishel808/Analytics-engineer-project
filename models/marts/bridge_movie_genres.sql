{{ config(
    materialized='table'
) }}

select
mg.movie_id,
genre_id,
mg.loaded_at
from {{ref('stg_bridge_movie_genre')}} as mg
inner join {{ref('stg_movies')}} as m on m.movie_id = mg.movie_id

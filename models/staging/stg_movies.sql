select
    movie_id,
    title,
    original_title,
    release_date,
    original_language,
    average_rating,
    rating_count,
    popularity,
    adult,
    loaded_at

from {{ source('raw', 'movies') }}

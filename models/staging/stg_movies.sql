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
    ingested_at

from {{ source('raw', 'movies') }}

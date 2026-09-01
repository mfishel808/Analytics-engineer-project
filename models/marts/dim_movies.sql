{{ config(
    materialized='table'
) }}

with movie_history as (

    select
        movie_id,
        popularity,
        average_rating,
        rating_count,
        revenue,
        dbt_valid_from,

        first_value(popularity) over (
            partition by movie_id
            order by dbt_valid_from
            rows between unbounded preceding and unbounded following
        ) as first_popularity,

        first_value(average_rating) over (
            partition by movie_id
            order by dbt_valid_from
            rows between unbounded preceding and unbounded following
        ) as first_average_rating,

        first_value(rating_count) over (
            partition by movie_id
            order by dbt_valid_from
            rows between unbounded preceding and unbounded following
        ) as first_rating_count,

        first_value(revenue) ignore nulls over (
            partition by movie_id
            order by dbt_valid_from
            rows between unbounded preceding and unbounded following
        ) as first_revenue,

        min(dbt_valid_from) over (
            partition by movie_id
        ) as first_value_date,

        lag(popularity) over (
            partition by movie_id
            order by dbt_valid_from
        ) as previous_popularity,

        lag(average_rating) over (
            partition by movie_id
            order by dbt_valid_from
        ) as previous_average_rating,

        lag(rating_count) over (
            partition by movie_id
            order by dbt_valid_from
        ) as previous_rating_count,

        lag(revenue) over (
            partition by movie_id
            order by dbt_valid_from
        ) as previous_revenue,

        lag(dbt_valid_from) over (
            partition by movie_id
            order by dbt_valid_from
        ) as previous_value_date,

        row_number() over (
            partition by movie_id
            order by dbt_valid_from desc
        ) as version_rank

    from {{ ref('movies_snapshot') }}

),

latest_history as (

    select *
    from movie_history
    where version_rank = 1

),

final as (

    select
        m.movie_id,
        m.title,
        m.original_title,
        m.release_date,
        m.original_language,
        m.adult,

        -- Current values
        m.budget,
        m.runtime,
        m.popularity,
        m.average_rating,
        m.rating_count,
        m.revenue,

        h.dbt_valid_from as current_value_date,

        -- First recorded values
        coalesce(
            h.first_popularity,
            h.previous_popularity,
            m.popularity
        ) as first_popularity,

        coalesce(
            h.first_average_rating,
            h.previous_average_rating,
            m.average_rating
        ) as first_average_rating,

        coalesce(
            h.first_rating_count,
            h.previous_rating_count,
            m.rating_count
        ) as first_rating_count,

        coalesce(
            h.first_revenue,
            h.previous_revenue,
            m.revenue
        ) as first_revenue,

        coalesce(
            h.first_value_date,
            h.previous_value_date,
            h.dbt_valid_from
        ) as first_value_date,

        -- Previous recorded values
        coalesce(
            h.previous_popularity,
            m.popularity
        ) as previous_popularity,

        coalesce(
            h.previous_average_rating,
            m.average_rating
        ) as previous_average_rating,

        coalesce(
            h.previous_rating_count,
            m.rating_count
        ) as previous_rating_count,

        coalesce(
            h.previous_revenue,
            m.revenue
        ) as previous_revenue,

        coalesce(
            h.previous_value_date,
            h.dbt_valid_from
        ) as previous_value_date,

        -- Change since first observation
        m.popularity
            - coalesce(
                h.first_popularity,
                h.previous_popularity,
                m.popularity
            )
            as popularity_change_since_first,

        m.average_rating
            - coalesce(
                h.first_average_rating,
                h.previous_average_rating,
                m.average_rating
            )
            as average_rating_change_since_first,

        m.rating_count
            - coalesce(
                h.first_rating_count,
                h.previous_rating_count,
                m.rating_count
            )
            as rating_count_change_since_first,

        m.revenue
            - coalesce(
                h.first_revenue,
                h.previous_revenue,
                m.revenue
            )
            as revenue_change_since_first,

        -- Change since previous observation
        m.popularity
            - coalesce(
                h.previous_popularity,
                m.popularity
            )
            as popularity_change_since_last,

        m.average_rating
            - coalesce(
                h.previous_average_rating,
                m.average_rating
            )
            as average_rating_change_since_last,

        m.rating_count
            - coalesce(
                h.previous_rating_count,
                m.rating_count
            )
            as rating_count_change_since_last,

        m.revenue
            - coalesce(
                h.previous_revenue,
                m.revenue
            )
            as revenue_change_since_last,

        m.loaded_at

    from {{ ref('stg_movies') }} as m

    left join latest_history as h
        on m.movie_id = h.movie_id

)

select *
from final
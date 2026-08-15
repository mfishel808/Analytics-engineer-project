# -*- coding: utf-8 -*-
"""
Created on Tue Aug  4 22:25:15 2026

@author: maxfi
"""
import pandas as pd
def popular_movies_clean(all_movies):
    movie_rows = []
    
    for movie in all_movies:
        movie_rows.append(
            {
                "movie_id": movie.get("id"),
                "title": movie.get("title"),
                "original_title": movie.get("original_title"),
                "release_date": movie.get("release_date"),
                "original_language": movie.get("original_language"),
                "average_rating": movie.get("vote_average"),
                "rating_count": movie.get("vote_count"),
                "popularity": movie.get("popularity"),
                "adult": movie.get("adult"),
            }
        )
    
    movies_df = pd.DataFrame(movie_rows)
    
    movies_df["release_date"] = (pd.to_datetime(
        movies_df["release_date"],
        errors="coerce",).dt.date
    )
    
    print(movies_df.shape)
    print(movies_df.head())
    
    
    movies_df = movies_df.drop_duplicates(
        subset="movie_id",
        keep="last",
    )
    
    print("Rows:", len(movies_df))
    print("Unique movies:", movies_df["movie_id"].nunique())
    
    return movies_df
    
def create_genres_dataframe(genres: list[dict]):
    genres_df = pd.DataFrame(genres)

    genres_df = genres_df.rename(
        columns={
            "id": "genre_id",
            "name": "genre_name",
        }
    )

    return genres_df

def create_people_dataframe(
    people_records: list[dict],
):

    people_df = pd.DataFrame(people_records)

    people_df = people_df.rename(
        columns={
            "person_id": "PERSON_ID",
            "person_name": "PERSON_NAME",
            "known_for_department": "KNOWN_FOR_DEPARTMENT",
            "gender": "GENDER",
            "popularity": "POPULARITY",
            "profile_path": "PROFILE_PATH",
        }
    )

    people_df = people_df.drop_duplicates(
        subset="PERSON_ID"
    )


    return people_df
def create_movie_credits_dataframe(
    movie_credit_records: list[dict],
) -> pd.DataFrame:

    movie_credits_df = pd.DataFrame(movie_credit_records)

    movie_credits_df = movie_credits_df.rename(
        columns={
            "movie_id": "MOVIE_ID",
            "person_id": "PERSON_ID",
            "credit_id": "CREDIT_ID",
            "credit_type": "CREDIT_TYPE",
            "character_name": "CHARACTER_NAME",
            "department": "DEPARTMENT",
            "job": "JOB",
            "cast_order": "CAST_ORDER",
        }
    )


    return movie_credits_df

def create_movie_genres_dataframe(movies: list[dict]):

    movie_genre_records = []

    for movie in movies:
        movie_id = movie.get("id")
        for genre_id in movie.get("genre_ids", []):
            movie_genre_records.append(
                {
                    "MOVIE_ID": movie_id,
                    "GENRE_ID": genre_id
                }
            )

    movie_genres_df = pd.DataFrame(movie_genre_records)

    movie_genres_df = movie_genres_df.drop_duplicates(
        subset=[
            "MOVIE_ID",
            "GENRE_ID",
        ]
    )

    return movie_genres_df
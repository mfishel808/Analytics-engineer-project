# -*- coding: utf-8 -*-
"""
Created on Tue Aug  4 22:41:24 2026

@author: maxfi
"""

from tmdb_api import full_download, page_download,get_movie_credits,get_movie_details, get_company_details
from transformations import (popular_movies_clean,create_genres_dataframe,
                            create_people_dataframe,create_movie_credits_dataframe, 
                            create_movie_genres_dataframe, create_studio_dataframe, 
                            create_movie_studio_dataframe)
from snowflake_loader import snowflake_uploader

def main():
    try:
        unconnected = []
        download = []
        connected = []
        try:
            all_movies = full_download(page_first = 1,page_last = 25, max_errors=5, url = "https://api.themoviedb.org/3/movie/popular")
            details, studio, not_loaded = get_movie_details(all_movies)
            movies= popular_movies_clean(main = all_movies, detail = details)
            movie_studio_df = create_movie_studio_dataframe(studio)
            download.append(movies)
            connected.append("MOVIES")
            download.append(movie_studio_df)
            connected.append("MOVIE_STUDIOS")
        except:
            unconnected.append("movies")
            unconnected.append("movie_studios")
        else:
            try:
                person, credit, NI =get_movie_credits(all_movies)
                person_df = create_people_dataframe(person)
                download.append(person_df)
                connected.append("PEOPLE")
                credit_df = create_movie_credits_dataframe(credit)
                download.append(credit_df)
                connected.append("MOVIE_CREDITS")
            except:
                unconnected.append("person")
                unconnected.append("credit")
            try:
                movie_genres_df = create_movie_genres_dataframe(all_movies)
                download.append(movie_genres_df)
                connected.append('MOVIE_GENRES')
            except:
                unconnected.append("movie_genre")
            try:
                studio_detail, not_loaded = get_company_details(studio)
                studio_df = create_studio_dataframe(studio_detail)
                download.append(studio_df)
                connected.append("STUDIOS")
            except:
                unconnected.append("studios")
                
        try:
            genres = page_download(page = 1, max_attempts = 10, url="https://api.themoviedb.org/3/genre/movie/list", pages = False)
            genre_df = create_genres_dataframe(genres = genres)
            download.append(genre_df)
            connected.append("GENRES")
        except:
            unconnected.append("genre")
    except Exception as e:
        print(e)
        raise
    else:
        no_upload = []
        upload = []
        for dataframe, table_name in zip(download, connected):
            try:
                snowflake_uploader(dataframe=dataframe, table_name = table_name)
                upload.append(table_name)
            except:
                no_upload.append(table_name)
        print(f"The following tables were updated: {upload}")
        print(f"The following tables were NOT updated: {no_upload}")
    if unconnected or no_upload:
        raise RuntimeError(
            "TMDb ingestion pipeline failed. "
            f"Download failures: {unconnected}. "
            f"Upload failures: {no_upload}."
        )
if __name__ == "__main__":
    main()
    
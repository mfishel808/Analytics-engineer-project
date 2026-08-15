

import requests
import pandas as pd
import time

from config import TMDB_TOKEN

headers = {
    "Authorization": f"Bearer {TMDB_TOKEN}",
    "accept": "application/json"
}

def page_download(url:str, page: int, max_attempts: int = 5, pages: bool = True, endpoint:str = "genres") -> list[dict]:
    url = url
    if pages:
        params = {
            "language": "en-US",
            "page": page,
        }
    elif not pages:
        params = {
            "language": "en-US",
        }

    for attempt in range(1, max_attempts + 1):

        try:
            response = requests.get(
                url,
                headers=headers,
                params=params,
                timeout=30,
            )

            response.raise_for_status()
            if pages:
                print(f"Page {page} successfully downloaded")
            if not pages:
                print("Download complete")
            return response.json()[endpoint]

        except Exception as error:

            print(
                f"Page {page} failed "
                f"on attempt {attempt}: {error}"
            )

            if attempt == max_attempts:
                raise

            wait_seconds = attempt * 2

            print(f"Waiting {wait_seconds} seconds before retrying...")
            time.sleep(wait_seconds)


def full_download(url: str, page_first: int=1, page_last: int=25, max_errors: int=5, endpoint: str = "results"):
    download = []
    errors = 0
    while errors < max_errors+1 and page_first<page_last:
        try:
            for page in range(page_first, page_last+1):
                    print(f"Downloading page {page}")
                    page_first = page
                    loaded = page_download(page = page, url=url,endpoint = endpoint)
                    download.extend(loaded)
                    time.sleep(0.25)
        except Exception as e:
            print(f"Failed on page {page}: {e} restarting at said page")
            errors +=1
            print(f'Error: {errors}')
    if errors > max_errors:
        print("errors exceeded max allowed")
        raise
    return download

def get_movie_credits(movies: list[dict]) -> list[dict]|list:

    people_records = []
    movie_credit_records = []
    movie_list = [movie["id"] for movie in movies]
    movie_unique = list(set(movie_list))
    id_not_loaded = movie_unique
    while len(id_not_loaded) > 10:
        movie_unique = id_not_loaded
        id_not_loaded = []
        for movie_id in movie_unique:
            try:
                url = (
                    f"https://api.themoviedb.org/3/movie/{movie_id}/credits"
                )
    
                response = requests.get(
                    url,
                    headers=headers,
                    timeout=30,
                )
    
                response.raise_for_status()
    
                credit_data = response.json()
    
                # CAST
                for person in credit_data["cast"]:
    
                    people_records.append(
                        {
                            "person_id": person.get("id"),
                            "person_name": person.get("name"),
                            "known_for_department":
                                person.get("known_for_department"),
                            "gender": person.get("gender"),
                            "popularity": person.get("popularity"),
                            "profile_path": person.get("profile_path"),
                        }
                    )
    
                    movie_credit_records.append(
                        {
                            "movie_id": movie_id,
                            "person_id": person.get("id"),
                            "credit_id": person.get("credit_id"),
                            "credit_type": "CAST",
                            "character_name": person.get("character"),
                            "department": None,
                            "job": None,
                            "cast_order": person.get("order"),
                        }
                    )
    
                # CREW
                for person in credit_data["crew"]:
    
                    people_records.append(
                        {
                            "person_id": person.get("id"),
                            "person_name": person.get("name"),
                            "known_for_department": person.get("known_for_department"),
                            "gender": person.get("gender"),
                            "popularity": person.get("popularity"),
                            "profile_path": person.get("profile_path"),
                        }
                    )
    
                    movie_credit_records.append(
                        {
                            "movie_id": movie_id,
                            "person_id": person.get("id"),
                            "credit_id": person.get("credit_id"),
                            "credit_type": "CREW",
                            "character_name": None,
                            "department": person.get("department"),
                            "job": person.get("job"),
                            "cast_order": None,
                        }
                    )
            
            except requests.exceptions.RequestException as error:
                print(
                    f"Could not load credits for movie "
                    f"{movie_id}: {error}"
                )
                id_not_loaded.append(movie_id)

    return people_records, movie_credit_records, id_not_loaded
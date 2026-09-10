

import requests
import pandas as pd
import time
import snowflake.connector
from config import (TMDB_TOKEN,
                    SNOWFLAKE_ACCOUNT,
                    SNOWFLAKE_DATABASE,
                    SNOWFLAKE_PAT,
                    SNOWFLAKE_ROLE,
                    SNOWFLAKE_SCHEMA,
                    SNOWFLAKE_USER,
                    SNOWFLAKE_WAREHOUSE)
from time import perf_counter

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
            start = perf_counter()
            response = requests.get(
                url,
                headers=headers,
                params=params,
                timeout=30,
            )
            print( f"Page {page} took {perf_counter() - start:.2f} seconds")
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
    print('downloading movie credits...')
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
                
    print('movie credits downloaded')
    return people_records, movie_credit_records, id_not_loaded

def get_movie_details(movies: list[dict]) -> list[dict]|list:

    movie_detail_records = []
    movie_studio = []

    movie_list = [movie["id"] for movie in movies]
    movie_unique = list(set(movie_list))

    id_not_loaded = movie_unique

    while len(id_not_loaded) > 10:
        movie_unique = id_not_loaded
        id_not_loaded = []

        for movie_id in movie_unique:
            try:
                url = (
                    f"https://api.themoviedb.org/3/movie/{movie_id}"
                )

                response = requests.get(
                    url,
                    headers=headers,
                    timeout=30,
                )

                response.raise_for_status()

                movie_data = response.json()

                movie_detail_records.append(
                    {
                        "movie_id": movie_id,
                        "budget": movie_data.get("budget"),
                        "revenue": movie_data.get("revenue"),
                        "runtime": movie_data.get("runtime"),
                    }
                )
                for company_id in movie_data.get("production_companies", []):
                    movie_studio.append(
                        {
                            "MOVIE_ID": movie_id,
                            "Company_ID": company_id['id']
                        }
                    )

            except requests.exceptions.RequestException as error:
                print(
                    f"Could not load details for movie "
                    f"{movie_id}: {error}"
                )

                id_not_loaded.append(movie_id)
            

    return movie_detail_records,movie_studio, id_not_loaded

def get_company_details(companies: list[dict]):

    company_detail_records = []

    company_list = [
        company["Company_ID"]
        for company in companies
    ]

    company_unique = list(set(company_list))

    id_not_loaded = company_unique

    while len(id_not_loaded) > 10:
        company_unique = id_not_loaded
        id_not_loaded = []

        for company_id in company_unique:
            try:
                url = (
                    f"https://api.themoviedb.org/3/company/{company_id}"
                )

                response = requests.get(
                    url,
                    headers=headers,
                    timeout=30,
                )

                response.raise_for_status()

                company_data = response.json()

                parent_company = company_data.get("parent_company")

                company_detail_records.append(
                    {
                        "company_id": company_id,
                        "company_name": company_data.get("name"),
                        "origin_country": company_data.get(
                            "origin_country"
                        ),
                        "headquarters": company_data.get(
                            "headquarters"
                        ),
                        "parent_company_id": (
                            parent_company.get("id")
                            if parent_company
                            else None
                        ),
                        "parent_company_name": (
                            parent_company.get("name")
                            if parent_company
                            else None
                        ),
                    }
                )

            except requests.exceptions.RequestException as error:
                print(
                    f"Could not load details for company "
                    f"{company_id}: {error}"
                )

                id_not_loaded.append(company_id)

    return company_detail_records, id_not_loaded

def get_people_details(people: list[dict]) -> list[dict] | list:
    print('downloading people details...')
    connection = snowflake.connector.connect(
        account=SNOWFLAKE_ACCOUNT,
        user=SNOWFLAKE_USER,
        password=SNOWFLAKE_PAT,
        warehouse=SNOWFLAKE_WAREHOUSE,
        database=SNOWFLAKE_DATABASE,
        schema=SNOWFLAKE_SCHEMA,
        role=SNOWFLAKE_ROLE,
    )

    cursor = connection.cursor()
    
    try:
        cursor.execute(
            """
            SELECT DISTINCT PERSON_ID
            FROM STREAMSIGHT.RAW.PERSON_DETAIL
            """
        )
    
        person_ids = {
            row[0]
            for row in cursor.fetchall()
        }
    
    finally:
        cursor.close()
        connection.close()
    print(person_ids)
    people_detail_records = []
    
    people_list = [person["person_id"] for person in people]
    people_unique = list(set(people_list))

    id_not_loaded = people_unique

    people_unique = id_not_loaded
    id_not_loaded = []
    count = 0
    for person_id in people_unique:
        count+=1
        if person_id not in person_ids:
            try:
                url = (
                    f"https://api.themoviedb.org/3/person/{person_id}"
                )
    
                response = requests.get(
                    url,
                    headers=headers,
                    timeout=30,
                )
    
                response.raise_for_status()
    
                person_data = response.json()
    
                people_detail_records.append(
                    {
                        "PERSON_ID": person_id,
                        "birthday": person_data.get("birthday"),
                        "deathday": person_data.get("deathday"),
                        "place_of_birth": person_data.get("place_of_birth"),
                    }
                )
    
            except:
                pass
            if count % 1000 == 0:
                print(f"finished {count} out of {len(people_unique)} people")
            
    print('people details downloaded')
    return people_detail_records, id_not_loaded
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 18 16:30:31 2026

@author: maxfi
"""

import time

import requests

from DBT_config import (
    DBT_ACCOUNT_ID,
    DBT_API_TOKEN,
    DBT_JOB_ID,
)


DBT_HOST = "th157.us1.dbt.com"

HEADERS = {
    "Authorization": f"Token {DBT_API_TOKEN}",
    "Content-Type": "application/json",
}

def trigger_dbt_job() -> int:
    url = (
        f"https://{DBT_HOST}/api/v2/accounts/"
        f"{DBT_ACCOUNT_ID}/jobs/{DBT_JOB_ID}/run/"
    )

    response = requests.post(
        url,
        headers=HEADERS,
        json={
            "cause": "Triggered after successful TMDB ingestion"
        },
        timeout=30,
    )

    response.raise_for_status()

    run_id = response.json()["data"]["id"]

    print(f"Triggered dbt run: {run_id}")

    return run_id


def get_dbt_run_status(run_id: int) -> int:
    url = (
        f"https://{DBT_HOST}/api/v2/accounts/"
        f"{DBT_ACCOUNT_ID}/runs/{run_id}/"
    )

    response = requests.get(
        url,
        headers=HEADERS,
        timeout=30,
    )

    response.raise_for_status()

    return response.json()["data"]["status"]


def monitor_dbt_run(
    run_id: int,
    check_interval: int = 15,
) -> None:

    status_names = {
        1: "Queued",
        2: "Starting",
        3: "Running",
        10: "Success",
        20: "Error",
        30: "Cancelled",
    }

    while True:
        status_code = get_dbt_run_status(run_id)

        status_name = status_names.get(
            status_code,
            f"Unknown ({status_code})",
        )

        print(f"dbt run {run_id}: {status_name}")

        if status_code == 10:
            print("dbt production job completed successfully.")
            return

        if status_code in (20, 30):
            raise RuntimeError(
                f"dbt run {run_id} finished with "
                f"status: {status_name}"
            )

        time.sleep(check_interval)


def main():
    run_id = trigger_dbt_job()
    monitor_dbt_run(run_id)


if __name__ == "__main__":
    main()

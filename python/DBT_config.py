# -*- coding: utf-8 -*-
"""
Created on Tue Aug 18 18:13:05 2026

@author: maxfi
"""


import os

from dotenv import load_dotenv


load_dotenv(override=True)


def require_environment_variable(name: str) -> str:
    """Return a required environment variable or raise a clear error."""
    value = os.getenv(name)

    if not value:
        raise ValueError(
            f"Required environment variable {name!r} was not found."
        )

    return value.strip()

#DBT info
DBT_API_TOKEN = require_environment_variable("DBT_API_TOKEN")
DBT_ACCOUNT_ID = require_environment_variable("DBT_ACCOUNT_ID")
DBT_JOB_ID = require_environment_variable("DBT_JOB_ID")
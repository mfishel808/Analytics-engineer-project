# -*- coding: utf-8 -*-
"""
Created on Tue Aug  4 21:40:24 2026

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


TMDB_TOKEN = require_environment_variable("TMDB_TOKEN")

SNOWFLAKE_ACCOUNT = require_environment_variable("SNOWFLAKE_ACCOUNT")
SNOWFLAKE_USER = require_environment_variable("SNOWFLAKE_USER")
SNOWFLAKE_PAT = require_environment_variable("SNOWFLAKE_PAT")
SNOWFLAKE_WAREHOUSE = require_environment_variable(
    "SNOWFLAKE_WAREHOUSE"
)
SNOWFLAKE_DATABASE = require_environment_variable(
    "SNOWFLAKE_DATABASE"
)
SNOWFLAKE_SCHEMA = require_environment_variable("SNOWFLAKE_SCHEMA")
SNOWFLAKE_ROLE = require_environment_variable("SNOWFLAKE_ROLE")
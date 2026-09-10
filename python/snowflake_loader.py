import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas
from datetime import datetime, UTC
from time import sleep

from config import (
    SNOWFLAKE_ACCOUNT,
    SNOWFLAKE_DATABASE,
    SNOWFLAKE_PAT,
    SNOWFLAKE_ROLE,
    SNOWFLAKE_SCHEMA,
    SNOWFLAKE_USER,
    SNOWFLAKE_WAREHOUSE,
)


def snowflake_uploader(dataframe, table_name: str):

    connection = snowflake.connector.connect(
        account=SNOWFLAKE_ACCOUNT,
        user=SNOWFLAKE_USER,
        password=SNOWFLAKE_PAT,
        warehouse=SNOWFLAKE_WAREHOUSE,
        database=SNOWFLAKE_DATABASE,
        schema=SNOWFLAKE_SCHEMA,
        role=SNOWFLAKE_ROLE,
    )

    if dataframe.empty:
        connection.close()

        raise ValueError(
            f"{table_name} dataframe is empty. "
            "Refusing to load table."
        )

    dataframe["loaded_at"] = datetime.now(UTC)

    dataframe.columns = [
        column.upper()
        for column in dataframe.columns
    ]

    cursor = connection.cursor()

    try:

        # =========================================================
        # PERSON DETAIL
        # Persistent table — do NOT replace existing data
        # =========================================================

        if table_name == "PERSON_DETAIL":

            load_table = "PERSON_DETAIL_LOAD"

            # 1. Remove IDs that haven't been refreshed in 1 year
            cursor.execute(
                f"""
                DELETE FROM
                    {SNOWFLAKE_DATABASE}.{SNOWFLAKE_SCHEMA}.{table_name}
                WHERE
                    LOADED_AT < DATEADD(
                        year,
                        -1,
                        CURRENT_TIMESTAMP()
                    )
                """
            )

            # 2. Create a temporary staging table
            cursor.execute(
                f"""
                CREATE OR REPLACE TEMP TABLE
                    {load_table}
                LIKE
                    {SNOWFLAKE_DATABASE}.{SNOWFLAKE_SCHEMA}.{table_name}
                """
            )

            # 3. Upload this run's successful person IDs
            success, number_of_chunks, number_of_rows, output = (
                write_pandas(
                    conn=connection,
                    df=dataframe,
                    table_name=load_table,
                )
            )

            if not success:
                raise RuntimeError(
                    f"Upload failed for {table_name}"
                )

            # 4. Validate temporary table
            cursor.execute(
                f"""
                SELECT COUNT(*)
                FROM {load_table}
                """
            )

            loaded_rows = cursor.fetchone()[0]

            if loaded_rows != len(dataframe):
                raise RuntimeError(
                    f"{table_name}: expected "
                    f"{len(dataframe)} rows "
                    f"but loaded {loaded_rows}"
                )

            # 5. Add only person IDs that aren't already stored
            cursor.execute(
                f"""
                MERGE INTO
                    {SNOWFLAKE_DATABASE}.{SNOWFLAKE_SCHEMA}.{table_name}
                    AS target

                USING
                    {load_table} AS source

                ON
                    target.PERSON_ID = source.PERSON_ID

                WHEN NOT MATCHED THEN
                    INSERT (
                        PERSON_ID,
                        LOADED_AT
                    )
                    VALUES (
                        source.PERSON_ID,
                        source.LOADED_AT
                    )
                """
            )

            print(f"{table_name} successfully updated")
            print("Chunks uploaded:", number_of_chunks)
            print("Rows processed:", number_of_rows)

        # =========================================================
        # ALL OTHER RAW TABLES
        # Existing replace/swap behavior
        # =========================================================

        else:

            load_table = f"{table_name}_LOAD"

            # 1. Create a fresh shadow table
            cursor.execute(
                f"""
                CREATE OR REPLACE TABLE
                    {SNOWFLAKE_DATABASE}.{SNOWFLAKE_SCHEMA}.{load_table}
                LIKE
                    {SNOWFLAKE_DATABASE}.{SNOWFLAKE_SCHEMA}.{table_name}
                """
            )

            # 2. Load dataframe into shadow table
            success, number_of_chunks, number_of_rows, output = (
                write_pandas(
                    conn=connection,
                    df=dataframe,
                    table_name=load_table,
                    database=SNOWFLAKE_DATABASE,
                    schema=SNOWFLAKE_SCHEMA,
                )
            )

            if not success:
                raise RuntimeError(
                    f"Upload failed for {table_name}"
                )

            # 3. Validate row count
            cursor.execute(
                f"""
                SELECT COUNT(*)
                FROM
                    {SNOWFLAKE_DATABASE}.{SNOWFLAKE_SCHEMA}.{load_table}
                """
            )

            loaded_rows = cursor.fetchone()[0]

            if loaded_rows != len(dataframe):
                raise RuntimeError(
                    f"{table_name}: expected "
                    f"{len(dataframe)} rows "
                    f"but loaded {loaded_rows}"
                )

            # 4. Replace live table with validated shadow table
            cursor.execute(
                f"""
                ALTER TABLE
                    {SNOWFLAKE_DATABASE}.{SNOWFLAKE_SCHEMA}.{table_name}
                SWAP WITH
                    {SNOWFLAKE_DATABASE}.{SNOWFLAKE_SCHEMA}.{load_table}
                """
            )

            # 5. LOAD now contains the old live data
            cursor.execute(
                f"""
                DROP TABLE
                    {SNOWFLAKE_DATABASE}.{SNOWFLAKE_SCHEMA}.{load_table}
                """
            )

            print("Success:", success)
            print("Chunks uploaded:", number_of_chunks)
            print("Rows uploaded:", number_of_rows)

    except Exception as e:
        print(e)
        raise

    finally:
        cursor.close()
        connection.close()
        sleep(2)
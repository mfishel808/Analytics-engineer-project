# -*- coding: utf-8 -*-
"""
Created on Tue Aug  4 21:40:36 2026

@author: maxfi
"""




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



def snowflake_uploader(dataframe,  table_name: str):
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
        raise ValueError(
            f"{table_name} dataframe is empty. "
            "Refusing to replace live RAW table."
        )
    
    dataframe["loaded_at"] =datetime.now(UTC)
    dataframe.columns = [
        column.upper()
        for column in dataframe.columns
    ]
    cursor = connection.cursor()
    load_table = f"{table_name}_LOAD"
    try:
        # 1. Create a fresh shadow table
        cursor.execute(
             f"""
             CREATE OR REPLACE TABLE
             {SNOWFLAKE_DATABASE}.{SNOWFLAKE_SCHEMA}.{load_table}
             LIKE
             {SNOWFLAKE_DATABASE}.{SNOWFLAKE_SCHEMA}.{table_name}
             """)
        success, number_of_chunks, number_of_rows, output = write_pandas(
            conn=connection,
            df= dataframe,
            table_name=load_table,
            database=SNOWFLAKE_DATABASE,
            schema=SNOWFLAKE_SCHEMA,
        )
        if not success:
           raise RuntimeError(
               f"Upload failed for {table_name}"
           )

       # 3. Validate
        cursor.execute(
           f"""
           SELECT COUNT(*)
           FROM {SNOWFLAKE_DATABASE}.{SNOWFLAKE_SCHEMA}.{load_table}
           """
       )

        loaded_rows = cursor.fetchone()[0]

        if loaded_rows != len(dataframe):
           raise RuntimeError(
               f"{table_name}: expected {len(dataframe)} rows "
               f"but loaded {loaded_rows}"
           )
        

       # 4. Only now replace the live table
        cursor.execute(
           f"""
           ALTER TABLE
           {SNOWFLAKE_DATABASE}.{SNOWFLAKE_SCHEMA}.{table_name}
           SWAP WITH
           {SNOWFLAKE_DATABASE}.{SNOWFLAKE_SCHEMA}.{load_table}
           """
       )

       # 5. LOAD now contains the OLD live data
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

# @contextmanager
# def snowflake_connection() -> Iterator[SnowflakeConnection]:
#     """Open a Snowflake connection and always close it afterward."""
#     connection = snowflake.connector.connect(
#         account=SNOWFLAKE_ACCOUNT,
#         user=SNOWFLAKE_USER,
#         password=SNOWFLAKE_PAT,
#         warehouse=SNOWFLAKE_WAREHOUSE,
#         database=SNOWFLAKE_DATABASE,
#         schema=SNOWFLAKE_SCHEMA,
#         role=SNOWFLAKE_ROLE,
#     )

#     try:
#         yield connection
#     finally:
#         connection.close()


# def replace_table_from_dataframe(
#     dataframe: pd.DataFrame,
#     table_name: str,
# ) -> int:
#     """
#     Truncate a Snowflake table and reload it from a DataFrame.

#     This is a full-refresh strategy suitable for the first project version.
#     """
#     if dataframe.empty:
#         raise ValueError(
#             f"Cannot load an empty DataFrame into {table_name}."
#         )

#     table_name = table_name.upper()

#     dataframe_to_load = dataframe.copy()
#     dataframe_to_load.columns = [
#         column.upper()
#         for column in dataframe_to_load.columns
#     ]

#     with snowflake_connection() as connection:
#         cursor = connection.cursor()

#         try:
#             cursor.execute(f"TRUNCATE TABLE {table_name}")

#             success, chunks, rows, output = write_pandas(
#                 conn=connection,
#                 df=dataframe_to_load,
#                 table_name=table_name,
#                 database=SNOWFLAKE_DATABASE,
#                 schema=SNOWFLAKE_SCHEMA,
#             )

#             if not success:
#                 raise RuntimeError(
#                     f"Snowflake load failed for table {table_name}."
#                 )

#             print(
#                 f"Loaded {rows} rows into "
#                 f"{SNOWFLAKE_DATABASE}."
#                 f"{SNOWFLAKE_SCHEMA}."
#                 f"{table_name} "
#                 f"using {chunks} chunk(s)."
#             )

#             return rows

#         except Exception:
#             connection.rollback()
#             raise

#         finally:
#             cursor.close()
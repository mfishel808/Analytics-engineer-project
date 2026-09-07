{{
    config(
        materialized='incremental',
        incremental_strategy='merge',
        unique_key='company_id',
        on_schema_change='append_new_columns'
    )
}}

select
    company_id,
    company_name,
    origin_country,
    headquarters,
    parent_company_id,
    parent_company_name,
    loaded_at

from {{ source('raw', 'studios') }}
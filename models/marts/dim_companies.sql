{{ config(
    materialized='table'
) }}

select
    company_id,
    company_name,
    origin_country,
    headquarters,
    case when parent_company_id is null then company_id
    else parent_company_id end as parent_company_id,
    case when parent_company_name is null then company_name
    else parent_company_name end as parent_company_name,
    loaded_at

from {{ ref('stg_companies') }}
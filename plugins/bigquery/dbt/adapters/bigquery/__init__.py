from dbt.adapters.bigquery.connections import BigQueryConnectionManager  # noqa
from dbt.adapters.bigquery.connections import BigQueryCredentials
from dbt.adapters.bigquery.relation import BigQueryRelation  # noqa
from dbt.adapters.bigquery.impl import BigQueryAdapter

from dbt.adapters.base import AdapterPlugin
from dbt.include import bigquery

Plugin = AdapterPlugin(
    adapter=BigQueryAdapter,
    credentials=BigQueryCredentials,
    include_path=bigquery.PACKAGE_PATH)

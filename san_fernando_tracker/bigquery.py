from __future__ import annotations

import json
from typing import Dict

from google.cloud import bigquery
from google.oauth2 import service_account

from . import config


class BigQueryClient:
    def __init__(self):
        credentials = service_account.Credentials.from_service_account_file(config.SERVICE_ACCOUNT_JSON_PATH)
        self.client = bigquery.Client(project=config.BIGQUERY_PROJECT_ID, credentials=credentials)
        self.table = f"{config.BIGQUERY_PROJECT_ID}.{config.BIGQUERY_DATASET}.{config.BIGQUERY_TABLE}"

    def insert_weekly_row(self, row: Dict) -> None:
        row = row.copy()
        for key in ("channel_breakdown", "category_breakdown"):
            row[key] = json.dumps(row.get(key, {}), ensure_ascii=False)
        errors = self.client.insert_rows_json(self.table, [row])
        if errors:
            raise RuntimeError(f"BigQuery insert error: {errors}")

## cne-airbyte-template

Basic Airbyte config template that integrates with the `cne-dagster-template` orchestrator and the `cne-dbt-template` warehouse conventions.

This repo provides:
- Basic config skeleton for Airbyte connections targeting BigQuery
- A simple trigger script to run a sync for a given connection
- A canonical connections config file that Dagster can read to build Airbyte assets
- Copy-paste snippets to integrate Airbyte assets into `cne-dagster-template`

### Prerequisites
- An Airbyte instance (local or remote). For local quickstart, see Airbyte OSS docs.
- BigQuery project and service account JSON, aligned with your DBT profile.
- Existing Airbyte connections (create via UI), then place their IDs into `config/connections.yaml`.

### Environment alignment with DBT
The DBT profile in `cne-dbt-template/profiles.yml` uses BigQuery with env vars:
- `DBT_PROFILE_PROJECT`
- `DATASET_PREFIX`
- `BIGQUERY_KEYFILE_PATH`

This template mirrors those for Airbyte’s destination dataset:
- BigQuery dataset for raw (Airbyte landings): `${DATASET_PREFIX}_RAW`
- DBT transforms write to: `${DATASET_PREFIX}_DWH`

### Setup
1) Copy env example and set values
```
cp .env.example .env
```

2) Create your Airbyte source and destination in the Airbyte UI, then create the connection(s).

3) Put connection IDs into `config/connections.yaml` (see `config/connections.example.yaml`).

### Trigger a connection sync (optional utility)
```
uvx python scripts/trigger_connection.py --name example_connection
# or by id
uvx python scripts/trigger_connection.py --id d290f1ee-6c54-4b01-90e6-d701748f0851
```
Env used: `AIRBYTE_URL` and optional `AIRBYTE_API_KEY` (for Airbyte Cloud).

### Integrate with Dagster
In your `cne-dagster-template`, add a new file `cne_dagster/cne_dagster/assets_airbyte.py` with the contents from `dagster_snippets/assets_airbyte.py` (in this repo).

Then modify `cne_dagster/cne_dagster/definitions.py` to include these assets and resource:
```python
from .assets_airbyte import airbyte_assets, airbyte_resource

defs = Definitions(
    assets=[tikal_dbt_dbt_assets, *airbyte_assets],
    schedules=schedules,
    resources={
        "dbt": DbtCliResource(project_dir=tikal_dbt_project),
        "airbyte": airbyte_resource,
    },
)
```

The snippet resolves the `connections.yaml` from `../cne-airbyte-template/config/connections.yaml` relative to the Dagster project and wires Airbyte connection-based assets using `dagster-airbyte`.

### Notes
- This repo intentionally does not provision sources/destinations programmatically. Use the Airbyte UI or your preferred IaC approach. Place resulting connection IDs in `config/connections.yaml`.
- Keep secrets out of Git. Use `.env` and your secrets manager.

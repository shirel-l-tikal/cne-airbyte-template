import os
import yaml
from pathlib import Path
from urllib.parse import urlparse
from dotenv import load_dotenv

from dagster_airbyte import AirbyteResource, load_assets_from_connections

load_dotenv()

# Resolve Airbyte URL and API key
_airbyte_url = os.getenv("AIRBYTE_URL", "http://localhost:8001")
_api_key = os.getenv("AIRBYTE_API_KEY", None)
parsed = urlparse(_airbyte_url)
_use_https = parsed.scheme == "https"
_host = parsed.hostname or "localhost"
_port = parsed.port or (443 if _use_https else 80)

# Default path: sibling repo `cne-airbyte-template/config/connections.yaml`
_default_connections_file = Path(__file__).joinpath(
    "..", "..", "..", "cne-airbyte-template", "config", "connections.yaml"
).resolve()
_connections_file = Path(os.getenv("AIRBYTE_CONNECTIONS_FILE", str(_default_connections_file)))


def _load_connection_ids(path: Path) -> list[str]:
    if not path.exists():
        return []
    data = yaml.safe_load(path.read_text()) or {}
    return [c["id"] for c in data.get("connections", []) if "id" in c]


airbyte_resource = AirbyteResource(
    host=_host,
    port=_port,
    use_https=_use_https,
    request_max_retries=3,
    request_retry_delay=5,
    api_key=_api_key,
)

_airbyte_connection_ids = _load_connection_ids(_connections_file)

airbyte_assets = load_assets_from_connections(
    connection_ids=_airbyte_connection_ids,
    asset_key_prefix=["raw"],
    group_name="airbyte",
    resource_key="airbyte",
)



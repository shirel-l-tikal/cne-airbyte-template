import argparse
import os
import sys
import yaml
import requests
from pathlib import Path
from urllib.parse import urlparse
from dotenv import load_dotenv


def load_connections_map(config_path: Path) -> dict:
    if not config_path.exists():
        return {}
    data = yaml.safe_load(config_path.read_text()) or {}
    by_name = {c["name"]: c["id"] for c in data.get("connections", []) if "name" in c and "id" in c}
    return by_name


def resolve_connection_id(arg_id: str | None, arg_name: str | None, config_path: Path) -> str:
    if arg_id:
        return arg_id
    if arg_name:
        by_name = load_connections_map(config_path)
        if arg_name in by_name:
            return by_name[arg_name]
        print(f"Connection named '{arg_name}' not found in {config_path}", file=sys.stderr)
        sys.exit(2)
    print("Must pass --id or --name", file=sys.stderr)
    sys.exit(2)


def airbyte_request(session: requests.Session, base_url: str, path: str, payload: dict, api_key: str | None):
    url = f"{base_url.rstrip('/')}{path}"
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    resp = session.post(url, json=payload, headers=headers, timeout=60)
    if resp.status_code >= 300:
        raise RuntimeError(f"Airbyte API error {resp.status_code}: {resp.text}")
    return resp.json()


def main():
    load_dotenv()
    parser = argparse.ArgumentParser()
    parser.add_argument("--id", dest="connection_id")
    parser.add_argument("--name", dest="connection_name")
    parser.add_argument("--config", default=str(Path(__file__).parent.parent / "config" / "connections.yaml"))
    args = parser.parse_args()

    base_url = os.getenv("AIRBYTE_URL", "http://localhost:8001")
    api_key = os.getenv("AIRBYTE_API_KEY")

    config_path = Path(args.config)
    connection_id = resolve_connection_id(args.connection_id, args.connection_name, config_path)

    with requests.Session() as s:
        result = airbyte_request(
            s,
            base_url,
            "/api/v1/connections/sync",
            {"connectionId": connection_id},
            api_key,
        )
    print(result)


if __name__ == "__main__":
    main()



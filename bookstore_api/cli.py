import argparse
import json
import sys
from pathlib import Path
from typing import Any

import requests

from bookstore_api.config import Settings
from bookstore_api.http_client import HttpClient
from bookstore_api.resources import AuthorsApi, BooksApi, ResourceApi


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Send one request to the FakeRestAPI Books or Authors API."
    )
    resources = parser.add_subparsers(dest="resource", required=True)

    for resource in ("books", "authors"):
        resource_parser = resources.add_parser(resource)
        operations = resource_parser.add_subparsers(dest="operation", required=True)
        operations.add_parser("list", help="List all items")

        for operation in ("get", "delete"):
            operation_parser = operations.add_parser(operation)
            operation_parser.add_argument("id", help="Item ID")

        for operation in ("create", "update"):
            operation_parser = operations.add_parser(operation)
            if operation == "update":
                operation_parser.add_argument("id", help="Item ID")
            payload_source = operation_parser.add_mutually_exclusive_group(required=True)
            payload_source.add_argument(
                "--data",
                help="JSON object to send, for example '{\"title\":\"Example\"}'",
            )
            payload_source.add_argument(
                "--data-file",
                type=Path,
                help="Path to a JSON file containing the request body",
            )

    return parser


def _read_payload(args: argparse.Namespace, parser: argparse.ArgumentParser) -> dict[str, Any]:
    try:
        if args.data_file is not None:
            raw_payload = args.data_file.read_text(encoding="utf-8")
        else:
            raw_payload = args.data
        payload = json.loads(raw_payload)
    except OSError as error:
        parser.error(f"Cannot read payload file: {error}")
    except json.JSONDecodeError as error:
        parser.error(f"Invalid JSON payload: {error}")

    if not isinstance(payload, dict):
        parser.error("Request payload must be a JSON object.")
    return payload


def _send_request(api: ResourceApi, args: argparse.Namespace, parser: argparse.ArgumentParser) -> requests.Response:
    if args.operation == "list":
        return api.list_all()
    if args.operation == "get":
        return api.get_by_id(args.id)
    if args.operation == "delete":
        return api.delete(args.id)

    payload = _read_payload(args, parser)
    if args.operation == "create":
        return api.create(payload)
    return api.update(args.id, payload)


def _print_response(response: requests.Response) -> None:
    print(f"HTTP {response.status_code}")
    if not response.text:
        print("(empty response body)")
        return

    try:
        body = response.json()
    except requests.exceptions.JSONDecodeError:
        print(response.text)
    else:
        print(json.dumps(body, indent=2, ensure_ascii=False))


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    api_type = BooksApi if args.resource == "books" else AuthorsApi
    client = HttpClient(Settings.from_env())

    try:
        response = _send_request(api_type(client), args, parser)
        _print_response(response)
        return 1 if response.status_code >= 400 else 0
    except requests.RequestException as error:
        print(f"Request failed: {error}", file=sys.stderr)
        return 1
    finally:
        client.close()


if __name__ == "__main__":
    raise SystemExit(main())

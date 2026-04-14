"""
Elasticsearch search script for Dynamic Docs QA.

Usage:
  python scripts/elasticsearch/es_search.py --content-id 6418715 --system-id 28
  python scripts/elasticsearch/es_search.py --content-id 6418715
  python scripts/elasticsearch/es_search.py --system-id 28
  python scripts/elasticsearch/es_search.py --content-id 6418715 --system-id 28 --index documents --size 10

Required in .env (repo root):
  ES_URL, ES_USER, ES_PASSWORD
"""

import argparse
import json
import os
import sys

import requests
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

ES_URL = os.getenv('ES_URL', '').rstrip('/')
ES_USER = os.getenv('ES_USER', '')
ES_PASSWORD = os.getenv('ES_PASSWORD', '')


def build_query(content_id: int | None, system_id: int | None, size: int) -> dict:
    must_clauses = []
    if content_id is not None:
        must_clauses.append({"term": {"content_id": content_id}})
    if system_id is not None:
        must_clauses.append({"term": {"system_id": system_id}})

    if not must_clauses:
        return {"query": {"match_all": {}}, "size": size}

    return {
        "query": {
            "bool": {
                "must": must_clauses
            }
        },
        "size": size
    }


def search(index: str, query: dict) -> dict:
    url = f"{ES_URL}/{index}/_search"
    response = requests.post(
        url,
        auth=HTTPBasicAuth(ES_USER, ES_PASSWORD),
        headers={"Content-Type": "application/json"},
        json=query,
        timeout=30
    )
    response.raise_for_status()
    return response.json()


def print_results(data: dict) -> None:
    hits = data.get("hits", {})
    total = hits.get("total", {}).get("value", 0)
    results = hits.get("hits", [])

    print(f"\nTotal hits: {total}")
    print("-" * 60)

    if not results:
        print("No documents found.")
        return

    for i, hit in enumerate(results, 1):
        source = hit.get("_source", {})
        print(f"\n[{i}] _id: {hit.get('_id')} | _score: {hit.get('_score')}")
        print(json.dumps(source, indent=2, default=str))


def main() -> None:
    if not ES_URL or not ES_USER or not ES_PASSWORD:
        print("Error: ES_URL, ES_USER, ES_PASSWORD must be set in .env", file=sys.stderr)
        sys.exit(1)

    parser = argparse.ArgumentParser(description="Query Elasticsearch for DD documents")
    parser.add_argument("--content-id", type=int, help="content_id field value")
    parser.add_argument("--system-id", type=int, help="system_id field value (tenant)")
    parser.add_argument("--index", default="documents", help="Index to search (default: documents)")
    parser.add_argument("--size", type=int, default=10, help="Max results to return (default: 10)")
    args = parser.parse_args()

    if args.content_id is None and args.system_id is None:
        parser.error("Provide at least --content-id or --system-id")

    query = build_query(args.content_id, args.system_id, args.size)

    print(f"\nQuery sent to {ES_URL}/{args.index}/_search:")
    print(json.dumps(query, indent=2))
    print("-" * 60)

    try:
        data = search(args.index, query)
        print_results(data)
    except requests.HTTPError as e:
        print(f"HTTP error: {e.response.status_code} - {e.response.text}", file=sys.stderr)
        sys.exit(1)
    except requests.ConnectionError:
        print(f"Connection error: could not reach {ES_URL}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

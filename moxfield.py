import re

import requests

API_BASE = "https://api2.moxfield.com/v1/collections"

COLLECTION_URL_RE = re.compile(r"moxfield\.com/collection/([A-Za-z0-9_-]+)", re.IGNORECASE)


def parse_collection_id(value):
    """Accept either a bare collection id or a full Moxfield collection URL."""
    value = value.strip()
    match = COLLECTION_URL_RE.search(value)
    if match:
        return match.group(1)
    if re.fullmatch(r"[A-Za-z0-9_-]+", value):
        return value
    raise ValueError("Not a valid Moxfield collection link or id")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "application/json",
}

PAGE_SIZE = 100


def _unit_price(card, finish):
    prices = card.get("prices", {})
    if finish == "foil":
        return prices.get("usd_foil")
    if finish == "etched":
        return prices.get("usd_etched") or prices.get("usd_foil")
    return prices.get("usd")


def fetch_collection(collection_id):
    """Fetch every entry in a public Moxfield collection, paginating as needed.

    Moxfield's pagination order can drift slightly between page requests for
    larger collections, which occasionally duplicates one entry across two
    pages while silently dropping another. Deduplicating by entry id (first
    occurrence wins) prevents a duplicate from double-counting a card's value
    in this snapshot; the rare dropped entry just reappears on the next fetch.
    """
    items = {}
    page = 1
    while True:
        resp = requests.get(
            f"{API_BASE}/{collection_id}",
            headers=HEADERS,
            params={"pageNumber": page, "pageSize": PAGE_SIZE},
            timeout=30,
        )
        resp.raise_for_status()
        payload = resp.json()

        for entry in payload["data"]:
            entry_id = entry["id"]
            if entry_id in items:
                continue
            card = entry["card"]
            finish = entry["finish"]
            quantity = entry["quantity"]
            unit_price = _unit_price(card, finish)
            items[entry_id] = {
                "entry_id": entry_id,
                "name": card["name"],
                "set_code": card["set"],
                "set_name": card["set_name"],
                "collector_number": card["cn"],
                "finish": finish,
                "quantity": quantity,
                "unit_price_usd": unit_price,
                "scryfall_id": card.get("scryfall_id"),
            }

        if page >= payload["totalPages"]:
            break
        page += 1

    return list(items.values())

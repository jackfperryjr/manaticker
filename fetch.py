from datetime import datetime, timezone

import db
from moxfield import fetch_items


def fetch_for_collection(collection_id):
    collection = db.get_collection(collection_id)
    items = fetch_items(collection["kind"], collection["moxfield_collection_id"])
    return db.save_snapshot(collection_id, items, datetime.now(timezone.utc))


def fetch_for_all_collections():
    results = []
    for collection in db.get_all_collections():
        try:
            snapshot_id = fetch_for_collection(collection["id"])
            results.append((collection["id"], snapshot_id, None))
        except Exception as exc:
            results.append((collection["id"], None, str(exc)))
    return results

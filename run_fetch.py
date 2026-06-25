from db import init_db
from fetch import fetch_for_all_collections


def main():
    init_db()
    results = fetch_for_all_collections()
    for collection_id, snapshot_id, error in results:
        if error:
            print(f"Collection {collection_id}: FAILED - {error}")
        else:
            print(f"Collection {collection_id}: saved snapshot {snapshot_id}")


if __name__ == "__main__":
    main()

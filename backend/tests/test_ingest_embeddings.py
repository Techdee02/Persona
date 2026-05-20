import json

from backend.ingest_embeddings import ingest_dataset


def test_ingest_dataset_builds_store(tmp_path):
    data_path = tmp_path / "items.jsonl"
    with data_path.open("w", encoding="utf-8") as handle:
        handle.write(json.dumps({"id": "a", "text": "hello", "name": "A"}))
        handle.write("\n")
        handle.write(json.dumps({"id": "b", "text": "world", "name": "B"}))
        handle.write("\n")

    store = ingest_dataset(
        dataset_path=str(data_path),
        text_field="text",
        id_field="id",
        metadata_fields=["name"],
        model_name="all-MiniLM-L6-v2",
    )

    results = store.query([1.0] * len(store.items[0].vector), top_k=1)
    assert len(results) == 1

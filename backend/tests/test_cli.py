import json
import subprocess
import sys


def test_cli_ingest(tmp_path):
    data_path = tmp_path / "yelp.jsonl"
    with data_path.open("w", encoding="utf-8") as handle:
        handle.write(
            json.dumps(
                {
                    "business_id": "b1",
                    "text": "Nice food",
                    "name": "Spot",
                    "categories": "Food",
                    "stars": 4.0,
                }
            )
        )
        handle.write("\n")

    output_path = tmp_path / "store.json"

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "backend.cli",
            "--dataset",
            "yelp",
            "--input",
            str(data_path),
            "--output",
            str(output_path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert output_path.exists()

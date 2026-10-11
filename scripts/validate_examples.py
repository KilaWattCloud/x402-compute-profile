import json
from pathlib import Path

from jsonschema import validate


ROOT = Path(__file__).resolve().parent.parent
EXAMPLES = (
    ("examples/quote-request.json", "schemas/request.schema.json"),
    ("examples/status-ready.json", "schemas/status.schema.json"),
    ("examples/error-payment-already-used.json", "schemas/error.schema.json"),
)


def main():
    for example_path, schema_path in EXAMPLES:
        with (ROOT / schema_path).open(encoding="utf-8") as schema_file:
            schema = json.load(schema_file)
        with (ROOT / example_path).open(encoding="utf-8") as example_file:
            example = json.load(example_file)
        validate(instance=example, schema=schema)
        print(f"Validated {example_path}")


if __name__ == "__main__":
    main()

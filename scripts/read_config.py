import sys
import yaml
from pathlib import Path


def main() -> None:
    if len(sys.argv) != 3:
        print("Usage: read_config.py <config_path> <environment>")
        sys.exit(1)

    config_path = Path(sys.argv[1])
    environment = sys.argv[2]

    data = yaml.safe_load(config_path.read_text())
    env = data.get("environments", {}).get(environment)
    if not env:
        print(f"Error: environment '{environment}' not found in config")
        sys.exit(2)

    customer = env.get("customer", "")
    catalog = env.get("catalog", "")
    schemas = env.get("schemas", [])

    # Print shell-parseable exports
    print(f"export CUSTOMER='{customer}'")
    print(f"export CATALOG='{catalog}'")
    print(f"export SCHEMAS='{','.join(schemas)}'")


if __name__ == "__main__":
    main()

import argparse

from config.settings import get_settings
from db.connection import get_connection
from db.migrations.runner import run_migrations


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Database migration tool")
    parser.add_argument(
        "--status",
        action="store_true",
        help="Show migration status",
    )
    return parser.parse_args()


def show_status(conn) -> None:
    from db.migrations.runner import (
        _discover_migrations,
        _ensure_tracking_table,
        _get_applied_versions,
    )

    _ensure_tracking_table(conn)
    applied = _get_applied_versions(conn)
    discovered = _discover_migrations()

    print("Migration Status:")
    print("-" * 60)
    for version, path in discovered:
        status = "Applied" if version in applied else "Pending"
        print(f"  {version}  {path.name:40s}  [{status}]")
    print("-" * 60)
    print(f"Total: {len(discovered)} migrations, {len(applied)} applied")


def main() -> None:
    args = parse_args()
    settings = get_settings()
    conn = get_connection(settings)

    if args.status:
        show_status(conn)
    else:
        applied = run_migrations(conn)
        if applied:
            print(f"\nApplied {len(applied)} migration(s)")

    conn.close()


if __name__ == "__main__":
    main()

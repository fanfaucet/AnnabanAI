from __future__ import annotations

import argparse
from dataclasses import asdict
import json

from annabanos_lite.kernel.os import AnnabanOSLite


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="AnnabanOS-Lite CLI")
    parser.add_argument("command", choices=["boot", "cycle", "notify", "status"], help="Command to execute")
    parser.add_argument("--user", default="default", help="User profile identifier")
    parser.add_argument("--message", default="", help="Notification message")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    os_app = AnnabanOSLite()

    if args.command == "boot":
        result = os_app.boot(args.user)
    elif args.command == "cycle":
        result = os_app.run_cycle(args.user)
    elif args.command == "notify":
        result = [
            asdict(record)
            for record in os_app.trigger_event("notify", {"message": args.message or "Hello from CLI"}, args.user)
        ]
    else:
        result = {
            "logs": os_app.store.read_json("logs/system_logs.json", default=[]),
            "snapshot": os_app.store.read_json("state/last_snapshot.json", default={}),
        }

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

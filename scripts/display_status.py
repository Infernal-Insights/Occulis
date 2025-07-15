#!/usr/bin/env python3
"""Launch the Tkinter status display."""
import argparse
from occulis_server.display import StatusDisplay


def main() -> None:
    parser = argparse.ArgumentParser(description="Show mining rig status")
    parser.add_argument("--host", default="localhost", help="Redis hostname")
    parser.add_argument("--port", type=int, default=6379, help="Redis port")
    parser.add_argument("--interval", type=int, default=5000,
                        help="Refresh interval in ms")
    args = parser.parse_args()
    StatusDisplay(args.host, args.port, args.interval).run()


if __name__ == '__main__':
    main()

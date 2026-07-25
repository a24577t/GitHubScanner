"""Deterministic, non-interactive CLI: collect and derive."""
import argparse
import os
import sys


def frame_error(message):
    print(f"collector: error: {message}", file=sys.stderr)
    return 2


def build_parser():
    parser = argparse.ArgumentParser(prog="collector")
    sub = parser.add_subparsers(dest="command", required=True)

    collect = sub.add_parser("collect", help="collect evidence from a GitHub environment")
    collect.add_argument("--api-url", required=True)
    collect.add_argument("--org", required=True)
    collect.add_argument("--out", required=True)
    collect.add_argument("--run-id", default=None)
    collect.add_argument("--max-pages", type=int, default=100)

    derive = sub.add_parser("derive", help="regenerate observed state from raw evidence")
    derive.add_argument("--out", required=True)
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    if args.command == "collect":
        allow_http = os.environ.get("COLLECTOR_INSECURE_ALLOW_HTTP") == "1"
        if not args.api_url.startswith("https://") and not allow_http:
            return frame_error("--api-url must be an https:// URL (ADR-0003)")
        token = os.environ.get("GITHUB_TOKEN")
        if not token:
            return frame_error("GITHUB_TOKEN environment variable is required")
        from collector.collect import RunFrameError, run_collect

        try:
            return run_collect(
                args.api_url, args.org, args.out, token,
                run_id=args.run_id, max_pages=args.max_pages,
            )
        except RunFrameError as err:
            return frame_error(str(err))
    return 0


if __name__ == "__main__":
    sys.exit(main())

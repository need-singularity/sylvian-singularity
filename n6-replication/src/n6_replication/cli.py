"""CLI placeholder — full implementation in Task 9."""

import argparse
from n6_replication import __version__


def main():
    parser = argparse.ArgumentParser(
        prog="n6-replicate",
        description=f"n6-replication v{__version__}",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.parse_args()


if __name__ == "__main__":
    main()

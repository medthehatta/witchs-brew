#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""witchs_brew"""


from witchs_brew.witchs_brew import apply_rules
from witchs_brew.witchs_brew import parse


#
# Constants
#


#
# Helpers
#


#
# Harnesses
#


#
# Entry point
#


def get_args():
    """Get arguments."""
    import argparse
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "infile",
        type=argparse.FileType("r"),
        nargs="?",
        default="-",
    )
    return parser.parse_args()


def main():
    """Entry point."""
    args = get_args()
    provided = [line.strip() for line in args.infile]
    parsed = parse(provided)
    result = apply_rules(parsed)
    for (provided_entry, result_entry) in zip(provided, result):
        print(f"{provided_entry} = {result_entry[1]}")


if __name__ == "__main__":
    main()

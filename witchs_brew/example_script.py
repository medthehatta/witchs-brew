#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""witchs_brew"""



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
    return parser.parse_args()


def main():
    """Entry point."""
    args = get_args()


if __name__ == "__main__":
    main()

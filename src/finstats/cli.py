from __future__ import annotations

import argparse


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="finstats")
    p.add_argument("--version", action="store_true")
    return p


def main() -> None:
    args = build_parser().parse_args()
    if args.version:
        print("0.1.0")
        return
    print("ok")

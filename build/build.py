#!/usr/bin/env python3
"""Ninja build script for Stealth Browser."""

import os
import sys
import subprocess
import platform
import argparse


def main():
    parser = argparse.ArgumentParser(description="Stealth Browser Build System")
    parser.add_argument(
        "--target", choices=["debug", "release", "official"], default="release"
    )
    parser.add_argument("--jobs", type=int, default=os.cpu_count() or 4)
    parser.add_argument("--clean", action="store_true", help="Clean build output")
    parser.add_argument(
        "--rust", action="store_true", default=True, help="Enable Rust security module"
    )
    args = parser.parse_args()

    build_dir = os.path.join(os.getcwd(), "out", args.target)
    os.makedirs(build_dir, exist_ok=True)

    gn_args = {
        "is_debug": args.target == "debug",
        "is_official_build": args.target == "official",
        "stealth_use_rust": args.rust,
        "symbol_level": 2 if args.target == "debug" else 0,
        "enable_nacl": False,
        "is_component_build": args.target == "debug",
    }

    gn_args_str = " ".join(f'{k}={str(v).lower()}' for k, v in gn_args.items())

    print(f"[StealthBrowser] Building: {args.target}")
    print(f"[StealthBrowser] GN args: {gn_args_str}")

    # Step 1: Generate build files with GN
    gn_path = os.path.join("third_party", "gn", "gn")
    if platform.system() == "Windows":
        gn_path += ".exe"

    subprocess.run(
        [gn_path, "gen", build_dir, f"--args={gn_args_str}"],
        check=True,
    )

    # Step 2: Build with Ninja
    ninja_path = os.path.join("third_party", "ninja", "ninja")
    if platform.system() == "Windows":
        ninja_path += ".exe"

    target = "//src:stealth_browser"
    subprocess.run(
        [ninja_path, "-C", build_dir, "-j", str(args.jobs), target],
        check=True,
    )

    print(f"[StealthBrowser] Build complete: {build_dir}/stealth-browser")

    # Step 3: Build Rust security module if enabled
    if args.rust:
        print("[StealthBrowser] Building Rust security module...")
        subprocess.run(
            ["cargo", "build", "--release"],
            cwd="src/security",
            check=True,
        )
        print("[StealthBrowser] Rust security module built.")

    print("[StealthBrowser] All builds complete!")


if __name__ == "__main__":
    main()

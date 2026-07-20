#!/usr/bin/env python3
"""Setup script for Stealth Browser development environment."""

import os
import sys
import subprocess
import platform


def run(cmd, **kwargs):
    print(f"  > {' '.join(cmd)}")
    subprocess.run(cmd, check=True, **kwargs)


def check_command(cmd):
    try:
        subprocess.run(cmd, capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def main():
    print("=" * 60)
    print("  Stealth Browser - Development Environment Setup")
    print("=" * 60)

    # Check prerequisites
    print("\n[1/6] Checking prerequisites...")

    prerequisites = {
        "python3": "Python 3",
        "git": "Git",
        "cargo": "Rust/Cargo",
        "node": "Node.js",
        "npm": "npm",
    }

    missing = []
    for cmd, name in prerequisites.items():
        if check_command([cmd, "--version"]):
            print(f"  ✓ {name}")
        else:
            print(f"  ✗ {name} - NOT FOUND")
            missing.append(name)

    if missing:
        print(f"\nMissing: {', '.join(missing)}")
        print("Install them and re-run this script.")
        sys.exit(1)

    # Install system dependencies
    print("\n[2/6] Checking system dependencies...")
    system = platform.system()
    if system == "Linux":
        print("  Installing Linux build deps...")
        run(["sudo", "apt-get", "update"])
        run([
            "sudo", "apt-get", "install", "-y",
            "build-essential", "clang", "lld", "ninja-build",
            "libgtk-3-dev", "libglib2.0-dev", "libnss3-dev",
            "libxss-dev", "libasound2-dev", "libpulse-dev",
            "libssl-dev", "libffi-dev", "libatk-bridge2.0-dev",
            "gperf", "bison", "flex", "libx11-xcb-dev",
            "libdrm-dev", "libgbm-dev", "libxcomposite-dev",
            "libxdamage-dev", "libxrandr-dev", "libxtst-dev",
        ])
    elif system == "Darwin":
        print("  macOS: Install Xcode Command Line Tools")
        run(["xcode-select", "--install"], check=False)
    elif system == "Windows":
        print("  Windows: Ensure Visual Studio Build Tools are installed")
        print("  Also install: chocolatey, then: choco install ninja")

    # Install Rust toolchain
    print("\n[3/6] Setting up Rust toolchain...")
    run(["rustup", "install", "stable"])
    run(["rustup", "component", "add", "clippy", "rustfmt"])

    # Install Node.js dependencies (for UI)
    print("\n[4/6] Installing UI dependencies...")
    if os.path.exists("src/ui/package.json"):
        run(["npm", "install"], cwd="src/ui")

    # Set up pre-commit hooks
    print("\n[5/6] Setting up pre-commit hooks...")
    hooks_dir = os.path.join(".git", "hooks")
    os.makedirs(hooks_dir, exist_ok=True)
    pre_commit = os.path.join(hooks_dir, "pre-commit")
    with open(pre_commit, "w") as f:
        f.write("#!/bin/sh\n")
        f.write("python3 scripts/lint.py\n")
        f.write("cargo fmt --check --manifest-path src/security/Cargo.toml\n")
    os.chmod(pre-commit, 0o755)

    # Verify build
    print("\n[6/6] Verifying build configuration...")
    run(["python3", "scripts/lint.py"])

    print("\n" + "=" * 60)
    print("  Setup complete! Run 'python3 build/build.py' to build.")
    print("=" * 60)


if __name__ == "__main__":
    main()

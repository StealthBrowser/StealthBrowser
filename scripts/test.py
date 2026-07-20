#!/usr/bin/env python3
"""Test runner for Stealth Browser."""

import os
import subprocess
import sys


def run(cmd, **kwargs):
    result = subprocess.run(cmd, capture_output=True, text=True, **kwargs)
    return result.returncode, result.stdout, result.stderr


def test_rust():
    print("[TEST] Rust security module...")
    security_dir = "src/security"
    if not os.path.exists(os.path.join(security_dir, "Cargo.toml")):
        print("  SKIP: No Cargo.toml")
        return 0

    code, out, err = run(["cargo", "test", "--manifest-path", f"{security_dir}/Cargo.toml"])
    print(out)
    if code != 0:
        print(f"  FAIL: {err}")
        return 1
    print("  PASS")
    return 0


def test_python():
    print("[TEST] Python scripts...")
    scripts_dir = "scripts"
    errors = 0
    for f in os.listdir(scripts_dir):
        if f.endswith(".py"):
            code, out, err = run(["python3", "-c", f"import importlib.util; s=importlib.util.spec_from_file_location('m','scripts/{f}'); m=importlib.util.module_from_spec(s)"])
            if code != 0:
                print(f"  FAIL: {f}")
                errors += 1
    if errors == 0:
        print("  PASS")
    return errors


def main():
    print("=" * 50)
    print("  Stealth Browser - Test Suite")
    print("=" * 50)

    total = 0
    total += test_rust()
    total += test_python()

    print("=" * 50)
    if total > 0:
        print(f"  FAILED: {total} test failures")
        sys.exit(1)
    else:
        print("  ALL TESTS PASSED")
    print("=" * 50)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Linting script for Stealth Browser."""

import os
import subprocess
import sys


def run(cmd, **kwargs):
    result = subprocess.run(cmd, capture_output=True, text=True, **kwargs)
    return result.returncode, result.stdout, result.stderr


def lint_cpp():
    """Lint C++ files with clang-tidy."""
    print("[LINT] C++ files...")
    cpp_files = []
    for root, dirs, files in os.walk("src"):
        for f in files:
            if f.endswith((".cc", ".cpp", ".h", ".hpp")):
                cpp_files.append(os.path.join(root, f))

    errors = 0
    for f in cpp_files:
        code, out, err = run(["clang-tidy", f, "--", "-std=c++17"])
        if code != 0:
            print(f"  FAIL: {f}")
            print(err)
            errors += 1
    if errors == 0:
        print(f"  PASS: {len(cpp_files)} files")
    return errors


def lint_rust():
    """Lint Rust files."""
    print("[LINT] Rust files...")
    security_dir = "src/security"
    if not os.path.exists(os.path.join(security_dir, "Cargo.toml")):
        print("  SKIP: No Cargo.toml found")
        return 0

    code, out, err = run(["cargo", "clippy", "--manifest-path", f"{security_dir}/Cargo.toml", "--", "-D", "warnings"])
    if code != 0:
        print(f"  FAIL: {err}")
        return 1
    print("  PASS: clippy clean")
    return 0


def lint_typescript():
    """Lint TypeScript files."""
    print("[LINT] TypeScript files...")
    ui_dir = "src/ui"
    if not os.path.exists(os.path.join(ui_dir, "package.json")):
        print("  SKIP: No package.json found")
        return 0

    code, out, err = run(["npx", "tsc", "--noEmit"], cwd=ui_dir)
    if code != 0:
        print(f"  FAIL: {err}")
        return 1
    print("  PASS: types clean")
    return 0


def lint_python():
    """Lint Python files."""
    print("[LINT] Python files...")
    py_files = []
    for root, dirs, files in os.walk("."):
        if "node_modules" in root or ".git" in root:
            continue
        for f in files:
            if f.endswith(".py"):
                py_files.append(os.path.join(root, f))

    errors = 0
    for f in py_files:
        code, out, err = run(["python3", "-m", "py_compile", f])
        if code != 0:
            print(f"  FAIL: {f}: {err}")
            errors += 1
    if errors == 0:
        print(f"  PASS: {len(py_files)} files")
    return errors


def main():
    print("=" * 50)
    print("  Stealth Browser - Lint Check")
    print("=" * 50)

    total_errors = 0
    total_errors += lint_cpp()
    total_errors += lint_rust()
    total_errors += lint_typescript()
    total_errors += lint_python()

    print("=" * 50)
    if total_errors > 0:
        print(f"  FAILED: {total_errors} errors")
        sys.exit(1)
    else:
        print("  ALL CHECKS PASSED")
    print("=" * 50)


if __name__ == "__main__":
    main()

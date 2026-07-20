#!/usr/bin/env python3
"""Ninja build automation for Stealth Browser.

Supports: Windows, macOS, Linux
Build modes: debug, release, official
"""

import os
import sys
import subprocess
import platform
import shutil
import argparse
import json
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent
BUILD_DIR = ROOT_DIR / "out"
THIRD_PARTY_DIR = ROOT_DIR / "third_party"


def log(msg, level="INFO"):
    colors = {"INFO": "\033[36m", "WARN": "\033[33m", "ERROR": "\033[31m", "OK": "\033[32m"}
    reset = "\033[0m"
    color = colors.get(level, "")
    print(f"{color}[{level}]{reset} {msg}")


def run(cmd, cwd=None, check=True):
    log(f"Running: {' '.join(str(c) for c in cmd)}")
    result = subprocess.run(cmd, cwd=cwd or ROOT_DIR, capture_output=True, text=True)
    if check and result.returncode != 0:
        log(f"Command failed:\n{result.stderr}", "ERROR")
        sys.exit(1)
    return result


def detect_platform():
    system = platform.system()
    if system == "Windows":
        return "win"
    elif system == "Darwin":
        return "mac"
    elif system == "Linux":
        return "linux"
    return system.lower()


def install_gn_ninja():
    """Install GN and Ninja build tools."""
    platform_name = detect_platform()

    THIRD_PARTY_DIR.mkdir(exist_ok=True)

    if platform_name == "linux":
        if shutil.which("ninja"):
            log("Ninja already installed", "OK")
        else:
            run(["sudo", "apt-get", "install", "-y", "ninja-build"])

        gn_path = THIRD_PARTY_DIR / "gn"
        if not gn_path.exists():
            log("Downloading GN...")
            run(["curl", "-L", "-o", str(gn_path),
                 "https://chrome-infra-packages.appspot.com/dl/gn/gn/linux-amd64/+/latest"])
            gn_path.chmod(0o755)

    elif platform_name == "mac":
        run(["brew", "install", "ninja", "gn"], check=False)

    elif platform_name == "win":
        log("Windows: Install ninja via: choco install ninja", "WARN")
        log("Windows: Download GN from chromium.googlesource.com/gn/gn", "WARN")


def build_rust_module():
    """Build the Rust security module."""
    security_dir = ROOT_DIR / "src" / "security"
    if not (security_dir / "Cargo.toml").exists():
        log("No Rust security module found", "WARN")
        return

    log("Building Rust security module...")
    run(["cargo", "build", "--release"], cwd=security_dir)

    lib_name = "libstealth_security"
    if detect_platform() == "win":
        lib_name = "stealth_security"

    # Copy built library to output
    for ext in [".a", ".so", ".dylib", ".lib", ".dll"]:
        src = security_dir / "target" / "release" / f"{lib_name}{ext}"
        if src.exists():
            dest = BUILD_DIR / f"{lib_name}{ext}"
            shutil.copy2(src, dest)
            log(f"Copied: {src.name} -> {dest}", "OK")


def build_ui():
    """Build the TypeScript UI."""
    ui_dir = ROOT_DIR / "src" / "ui"
    if not (ui_dir / "package.json").exists():
        log("No UI package.json found", "WARN")
        return

    log("Building TypeScript UI...")
    run(["npm", "install"], cwd=ui_dir)
    run(["npm", "run", "build"], cwd=ui_dir)


def build_ninja(target="release"):
    """Build with GN + Ninja."""
    platform_name = detect_platform()

    gn_args = {
        "is_debug": target == "debug",
        "is_official_build": target == "official",
        "stealth_use_rust": True,
        "symbol_level": 2 if target == "debug" else 0,
        "is_component_build": target == "debug",
    }

    gn_args_str = " ".join(f"{k}={str(v).lower()}" for k, v in gn_args.items())

    out_dir = BUILD_DIR / target
    out_dir.mkdir(parents=True, exist_ok=True)

    gn_path = THIRD_PARTY_DIR / "gn"
    if platform_name == "win":
        gn_path = gn_path.with_suffix(".exe")

    ninja_cmd = "ninja"
    if platform_name == "win":
        if shutil.which("ninja.exe"):
            ninja_cmd = "ninja.exe"

    if gn_path.exists():
        run([str(gn_path), "gen", str(out_dir), f"--args={gn_args_str}"])
        run([ninja_cmd, "-C", str(out_dir), "-j", str(os.cpu_count() or 4), "//src:stealth_browser"])
    else:
        log("GN not found. Using cmake fallback.", "WARN")
        run(["cmake", "-B", str(out_dir), "-G", "Ninja", f"-DCMAKE_BUILD_TYPE={target}"],
            cwd=ROOT_DIR)
        run(["cmake", "--build", str(out_dir)], cwd=ROOT_DIR)

    log(f"Build complete: {out_dir}", "OK")


def package_builds():
    """Package builds for distribution."""
    platform_name = detect_platform()
    dist_dir = ROOT_DIR / "dist"
    dist_dir.mkdir(exist_ok=True)

    log(f"Packaging for {platform_name}...")

    if platform_name == "linux":
        # AppImage
        app_dir = dist_dir / "StealthBrowser.AppDir"
        app_dir.mkdir(exist_ok=True)
        (app_dir / "usr" / "bin").mkdir(parents=True)

        binary = BUILD_DIR / "release" / "stealth-browser"
        if binary.exists():
            shutil.copy2(binary, app_dir / "usr" / "bin" / "stealth-browser")

        desktop_content = """[Desktop Entry]
Name=Stealth Browser
Exec=stealth-browser
Icon=stealth-browser
Type=Application
Categories=Network;WebBrowser;
"""
        (app_dir / "stealth-browser.desktop").write_text(desktop_content)
        shutil.copy2(ROOT_DIR / "assets" / "logo.svg", app_dir / "stealth-browser.svg")

        log(f"AppImage directory created: {app_dir}", "OK")

    elif platform_name == "win":
        log("Windows: NSIS installer will be built by CI", "INFO")

    elif platform_name == "mac":
        log("macOS: DMG will be built by CI", "INFO")

    log("Packaging complete!", "OK")


def main():
    parser = argparse.ArgumentParser(description="Stealth Browser Build System")
    parser.add_argument("--target", choices=["debug", "release", "official"], default="release")
    parser.add_argument("--clean", action="store_true")
    parser.add_argument("--skip-rust", action="store_true")
    parser.add_argument("--skip-ui", action="store_true")
    parser.add_argument("--package", action="store_true")
    parser.add_argument("--install-deps", action="store_true")
    args = parser.parse_args()

    log("=" * 60)
    log("  Stealth Browser - Build System")
    log(f"  Platform: {detect_platform()}")
    log(f"  Target: {args.target}")
    log("=" * 60)

    if args.clean:
        log("Cleaning build directories...")
        if BUILD_DIR.exists():
            shutil.rmtree(BUILD_DIR)
        log("Clean complete", "OK")

    if args.install_deps:
        install_gn_ninja()
        build_rust_module()
        build_ui()
        return

    if not args.skip_rust:
        build_rust_module()

    if not args.skip_ui:
        build_ui()

    build_ninja(args.target)

    if args.package:
        package_builds()

    log("=" * 60)
    log("  Build complete!", "OK")
    log("=" * 60)


if __name__ == "__main__":
    main()

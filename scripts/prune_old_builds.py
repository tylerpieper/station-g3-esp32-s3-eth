#!/usr/bin/env python3
"""
prune_old_builds.py
Maintains the ./builds/ directory retention policy by removing release folders
not listed in active_folders, and generates/updates builds/INDEX.md summarizing
all currently retained builds, metadata, applied PRs/patches, and file links.
"""

import argparse
import json
import os
import re
import shutil
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


_PR_CACHE: Dict[int, Dict[str, Any]] = {}


def fetch_pr_details(pr_num: int) -> Dict[str, Any]:
    """Fetches PR metadata and description from the upstream GitHub API."""
    if pr_num in _PR_CACHE:
        return _PR_CACHE[pr_num]

    url = f"https://api.github.com/repos/meshtastic/firmware/pulls/{pr_num}"
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "meshtastic-pr-doc-generator",
        },
    )
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")

    details = {
        "number": pr_num,
        "title": f"Upstream PR #{pr_num}",
        "user": "meshtastic",
        "url": f"https://github.com/meshtastic/firmware/pull/{pr_num}",
        "body": "",
    }

    try:
        with urllib.request.urlopen(req, timeout=15) as res:
            data = json.loads(res.read().decode("utf-8"))
            details["title"] = data.get("title", details["title"])
            details["user"] = data.get("user", {}).get("login", "meshtastic")
            details["url"] = data.get("html_url", details["url"])
            details["body"] = (data.get("body") or "").strip()
    except Exception as err:
        print(f"[WARN] Failed to fetch PR #{pr_num} details from GitHub API: {err}", file=sys.stderr)

    _PR_CACHE[pr_num] = details
    return details


def generate_pr_readmes(builds_dir: Path, config_path: Path) -> None:
    """
    Generates a comprehensive README.md in each PR profile directory
    (and copies it to each variant folder) documenting the PR summary, author,
    link, and full description.
    """
    if not builds_dir.is_dir():
        return

    # Load custom profiles from config if available
    profile_configs: Dict[str, Dict[str, Any]] = {}
    if config_path.is_file():
        try:
            import yaml
            with open(config_path, "r", encoding="utf-8") as f:
                cfg = yaml.safe_load(f) or {}
                for p in cfg.get("custom_profiles", []):
                    pname = p.get("profile_name")
                    if pname:
                        profile_configs[pname] = p
        except Exception as err:
            print(f"[WARN] Could not parse config for PR readmes: {err}", file=sys.stderr)

    for release_dir in sorted(builds_dir.iterdir()):
        if not release_dir.is_dir() or release_dir.name.startswith("."):
            continue

        for profile_dir in sorted(release_dir.iterdir()):
            if not profile_dir.is_dir() or profile_dir.name.startswith(".") or profile_dir.name == "vanilla":
                continue

            profile_name = profile_dir.name
            pcfg = profile_configs.get(profile_name, {})

            # Extract PR numbers
            pr_nums: List[int] = []
            for pr_item in pcfg.get("upstream_prs", []):
                try:
                    pr_nums.append(int(pr_item))
                except ValueError:
                    pass

            # Inspect manifests in variant folders if PR list was not in config
            variant_dirs = [d for d in profile_dir.iterdir() if d.is_dir() and not d.name.startswith(".")]
            if not pr_nums:
                for vd in variant_dirs:
                    mf = vd / "build-manifest.json"
                    if mf.is_file():
                        try:
                            with open(mf, "r", encoding="utf-8") as f:
                                mdata = json.load(f)
                                for pr_str in (mdata.get("upstream_prs") or "").split():
                                    if pr_str.isdigit() and int(pr_str) not in pr_nums:
                                        pr_nums.append(int(pr_str))
                        except Exception:
                            pass

            # Gather PR details
            pr_data_list = [fetch_pr_details(pr) for pr in pr_nums]

            # Build README markdown
            now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
            title_prefix = "PR Build" if pr_nums else "Custom Build"
            lines: List[str] = [
                f"# {title_prefix}: {profile_name}",
                "",
                f"> **Target Release:** `{release_dir.name}`  ",
                f"> **Generated:** `{now_utc}`  ",
            ]

            summary_text = pcfg.get("summary") or pcfg.get("description", "")
            if summary_text:
                lines.append(f"> **Profile Summary:** {summary_text}  ")

            lines.append("")
            lines.append("---")
            lines.append("")

            if pr_data_list:
                lines.append("## Upstream Pull Request Details")
                lines.append("")
                for pr in pr_data_list:
                    lines.extend([
                        f"### [PR #{pr['number']}: {pr['title']}]({pr['url']})",
                        f"* **Author:** [@{pr['user']}](https://github.com/{pr['user']})",
                        f"* **PR Link:** {pr['url']}",
                        "",
                        "#### Description",
                        "",
                        pr['body'] if pr['body'] else summary_text or "_No description provided._",
                        "",
                    ])
            elif summary_text:
                lines.extend([
                    "## Build Profile Summary",
                    "",
                    summary_text,
                    "",
                ])

            # List built variants
            lines.extend([
                "---",
                "",
                "## Included Board Variants",
                "",
                "| Variant | Files Available |",
                "| :--- | :--- |",
            ])

            for vd in sorted(variant_dirs, key=lambda d: d.name):
                bin_files = [f.name for f in vd.iterdir() if f.is_file() and not f.name.endswith(".json") and not f.name.endswith(".md")]
                files_str = ", ".join(f"`{bf}`" for bf in sorted(bin_files)) if bin_files else "_Compiled binaries present_"
                lines.append(f"| [`{vd.name}/`]({urllib.parse.quote(vd.name)}/) | {files_str} |")

            lines.append("")

            readme_content = "\n".join(lines)

            # Write to profile directory
            readme_path = profile_dir / "README.md"
            with open(readme_path, "w", encoding="utf-8") as f:
                f.write(readme_content)

            # Also write to each variant subdirectory for direct visibility
            for vd in variant_dirs:
                v_readme_path = vd / "README.md"
                with open(v_readme_path, "w", encoding="utf-8") as f:
                    f.write(readme_content)


def load_active_folders(
    active_folders_arg: Optional[str],
    repo_root: Path,
    config_path: Path,
) -> List[str]:
    """
    Parses active_folders from argument or environment variable.
    Falls back to recalculating via resolve_matrix if not provided.
    """
    raw = active_folders_arg or os.environ.get("ACTIVE_FOLDERS", "").strip()
    if raw:
        try:
            data = json.loads(raw)
            if isinstance(data, list):
                return [str(item).strip() for item in data if str(item).strip()]
        except json.JSONDecodeError:
            try:
                import ast
                data = ast.literal_eval(raw)
                if isinstance(data, list):
                    return [str(item).strip() for item in data if str(item).strip()]
            except Exception as err:
                print(f"[WARN] Failed to parse active_folders JSON/literal: {err}. Recalculating...", file=sys.stderr)

    # Recalculate if not supplied
    try:
        from resolve_matrix import load_build_config, resolve_plan

        config = load_build_config(config_path)
        _, active_folders = resolve_plan(config=config, repo_root=repo_root)
        return active_folders
    except Exception as err:
        print(f"[WARN] Could not recalculate active_folders: {err}", file=sys.stderr)
        return []


def prune_outdated_folders(builds_dir: Path, active_folders: List[str]) -> List[str]:
    """Removes directories in builds/ that are not present in active_folders."""
    pruned: List[str] = []
    if not builds_dir.is_dir() or not active_folders:
        return pruned

    active_set = set(active_folders)

    for entry in builds_dir.iterdir():
        # Never prune special files or directories
        if not entry.is_dir() or entry.name.startswith("."):
            continue
        if entry.name not in active_set:
            print(f"[PRUNE] Removing outdated release directory: {entry.name}")
            shutil.rmtree(entry)
            pruned.append(entry.name)

    return pruned


def scan_available_builds(builds_dir: Path) -> List[Dict[str, Any]]:
    """
    Scans the builds/ directory tree for all compiled variants and manifests.
    Expected hierarchy: builds/<release_folder>/<build_type>/<variant_name>/
    """
    builds: List[Dict[str, Any]] = []
    if not builds_dir.is_dir():
        return builds

    for release_dir in sorted(builds_dir.iterdir()):
        if not release_dir.is_dir() or release_dir.name.startswith("."):
            continue

        release_folder = release_dir.name
        # release_folder format is <channel>-<tag>, e.g. alpha-v2.8.1.8e6a88d
        parts = release_folder.split("-", 1)
        channel = parts[0] if len(parts) > 1 else "unknown"
        tag = parts[1] if len(parts) > 1 else release_folder

        for build_type_dir in sorted(release_dir.iterdir()):
            if not build_type_dir.is_dir() or build_type_dir.name.startswith("."):
                continue
            build_type = build_type_dir.name

            for variant_dir in sorted(build_type_dir.iterdir()):
                if not variant_dir.is_dir() or variant_dir.name.startswith("."):
                    continue
                variant_name = variant_dir.name

                manifest_file = variant_dir / "build-manifest.json"
                manifest_data: Dict[str, Any] = {}
                if manifest_file.is_file():
                    try:
                        with open(manifest_file, "r", encoding="utf-8") as f:
                            manifest_data = json.load(f)
                    except Exception as err:
                        print(f"[WARN] Failed to read {manifest_file}: {err}", file=sys.stderr)

                # Collect binary files
                binary_exts = {".bin", ".uf2", ".hex", ".elf", ".zip"}
                binary_files = [
                    f.name for f in variant_dir.iterdir()
                    if f.is_file() and (f.suffix in binary_exts or f.name.endswith(".bin"))
                ]

                rel_folder_link = f"{release_folder}/{build_type}/{variant_name}"

                build_info = {
                    "release_folder": release_folder,
                    "channel": manifest_data.get("channel", channel),
                    "tag": manifest_data.get("tag", tag),
                    "build_type": manifest_data.get("build_type", build_type),
                    "variant_name": manifest_data.get("variant_name", variant_name),
                    "pio_env": manifest_data.get("pio_env", variant_name),
                    "upstream_prs": manifest_data.get("upstream_prs", ""),
                    "local_patches": manifest_data.get("local_patches", ""),
                    "upstream_commit": manifest_data.get("upstream_commit", ""),
                    "build_timestamp": manifest_data.get("build_timestamp", ""),
                    "relative_path": rel_folder_link,
                    "binaries": sorted(binary_files),
                }
                builds.append(build_info)

    return builds


def generate_index_markdown(builds: List[Dict[str, Any]], active_folders: List[str]) -> str:
    """Renders a comprehensive, clean INDEX.md file for the builds/ directory."""
    now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    lines: List[str] = [
        "# Meshtastic Custom Firmware Builds Index",
        "",
        f"> **Last Pipeline Sync:** `{now_utc}`  ",
        f"> **Active Release Folders:** {', '.join(f'`{f}`' for f in sorted(active_folders)) if active_folders else '_None_'}",
        "",
        "This directory contains automated, overlay-patched firmware binaries compiled by the CI/CD pipeline.",
        "Outdated release directories not matching active retention rules are automatically pruned.",
        "",
        "---",
        "",
        "## Available Firmware Builds",
        "",
    ]

    if not builds:
        lines.extend([
            "_No firmware builds currently published._",
            "",
            "Builds will be published here automatically once the GitHub Actions runner completes a compile job.",
            "",
        ])
    else:
        lines.extend([
            "| Channel | Tag | Type | Variant | Target PIO Env | Applied PRs | Local Patches | Artifacts |",
            "| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |",
        ])

        for b in builds:
            ch_badge = f"**{b['channel'].upper()}**" if b['channel'] in ('alpha', 'beta') else b['channel']
            tag_link = f"[`{b['tag']}`](https://github.com/meshtastic/firmware/releases/tag/{b['tag']})"
            prs_str = b['upstream_prs'] or "_None_"
            if b['upstream_prs']:
                prs_list = [
                    f"[#{pr}](https://github.com/meshtastic/firmware/pull/{pr})"
                    for pr in b['upstream_prs'].split()
                ]
                prs_str = ", ".join(prs_list)

            patches_str = f"`{b['local_patches']}`" if b['local_patches'] else "_None_"
            quoted_path = urllib.parse.quote(b['relative_path'])
            folder_link = f"[`{b['variant_name']}/`]({quoted_path}/)"

            # Link build type to its PR README if it's a custom PR profile
            if b['build_type'] != 'vanilla':
                type_quoted = urllib.parse.quote(f"{b['release_folder']}/{b['build_type']}")
                type_cell = f"[`{b['build_type']}`]({type_quoted}/README.md)"
            else:
                type_cell = f"`{b['build_type']}`"

            # If specific binary files exist, link them
            if b['binaries']:
                bin_links = "<br>".join([
                    f"[`{fn}`]({quoted_path}/{urllib.parse.quote(fn)})"
                    for fn in b['binaries']
                ])
                artifacts_cell = f"{folder_link}<br>{bin_links}"
            else:
                artifacts_cell = folder_link

            lines.append(
                f"| {ch_badge} | {tag_link} | {type_cell} | **{b['variant_name']}** | `{b['pio_env']}` | {prs_str} | {patches_str} | {artifacts_cell} |"
            )

        lines.extend([
            "",
            "---",
            "",
            "### Detailed Build Manifest Information",
            "",
            "Each variant directory includes a `build-manifest.json` file documenting the exact upstream git commit SHA, build timestamp, and applied modifications for provenance and reproducibility.",
            "",
        ])

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Prune old Meshtastic builds and update INDEX.md")
    parser.add_argument("--active-folders", default=None, help="JSON list of active release folders to retain")
    parser.add_argument("--builds-dir", default="builds", help="Path to builds directory")
    parser.add_argument("--config", default="build-config.yaml", help="Path to build-config.yaml")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(repo_root / "scripts"))

    builds_dir = repo_root / args.builds_dir
    config_path = repo_root / args.config

    active_folders = load_active_folders(
        active_folders_arg=args.active_folders,
        repo_root=repo_root,
        config_path=config_path,
    )

    print("=" * 60)
    print("Meshtastic Build Retention & Pruning")
    print("=" * 60)
    print(f"Active Folders to Retain: {active_folders}")

    pruned = prune_outdated_folders(builds_dir=builds_dir, active_folders=active_folders)
    print(f"Pruned {len(pruned)} outdated folder(s): {pruned}")

    # Generate or update README.md documentation for all PR build directories
    generate_pr_readmes(builds_dir=builds_dir, config_path=config_path)

    builds = scan_available_builds(builds_dir=builds_dir)
    print(f"Retained {len(builds)} available build variant(s)")

    index_content = generate_index_markdown(builds=builds, active_folders=active_folders)
    index_path = builds_dir / "INDEX.md"
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(index_content)
    print(f"Successfully generated/updated {index_path}")
    print("=" * 60)


if __name__ == "__main__":
    main()

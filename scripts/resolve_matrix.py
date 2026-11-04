#!/usr/bin/env python3
"""
resolve_matrix.py
Parses build-config.yaml, queries upstream Meshtastic GitHub releases,
classifies releases into alpha/beta channels, selects active target releases
based on retention policies and pinned tags, and generates the dynamic matrix
for GitHub Actions compile jobs.
"""

import argparse
import json
import os
import re
import subprocess
import sys
import urllib.request
import urllib.error
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

REPO_UPSTREAM = "meshtastic/firmware"


def load_build_config(config_path: Path) -> Dict[str, Any]:
    """Loads and validates build-config.yaml."""
    if not config_path.is_file():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    if not isinstance(config, dict):
        raise ValueError(f"Invalid YAML root in {config_path}: expected dictionary")
    return config


def fetch_upstream_releases(per_page: int = 30) -> List[Dict[str, Any]]:
    """
    Fetches recent upstream releases from GitHub.
    Tries `gh api` first; falls back to direct HTTPS GitHub API with standard headers.
    """
    # 1. Try gh api if available
    try:
        cmd = ["gh", "api", f"repos/{REPO_UPSTREAM}/releases?per_page={per_page}"]
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding="utf-8",
            errors="replace",
            check=True,
        )
        if result.stdout:
            releases = json.loads(result.stdout)
            if isinstance(releases, list):
                return releases
    except (subprocess.SubprocessError, FileNotFoundError, json.JSONDecodeError) as e:
        pass

    # 2. Fallback to HTTPS API via urllib
    url = f"https://api.github.com/repos/{REPO_UPSTREAM}/releases?per_page={per_page}"
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "meshtastic-custom-build-resolver",
        },
    )
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")

    try:
        with urllib.request.urlopen(req, timeout=20) as response:
            data = json.loads(response.read().decode("utf-8"))
            if isinstance(data, list):
                return data
    except urllib.error.URLError as err:
        print(f"[WARN] Failed to fetch upstream releases via HTTP: {err}", file=sys.stderr)

    return []


def classify_release(release: Dict[str, Any]) -> Optional[str]:
    """
    Classifies a Meshtastic release into 'alpha' or 'beta'.
    Returns None if the release is revoked or a draft.

    Meshtastic naming conventions observed:
      - 'Meshtastic Firmware <ver>.<hash> Alpha' (prerelease: true)
      - 'Meshtastic Firmware <ver>.<hash> Beta' (prerelease: false)
      - 'Meshtastic Firmware <ver>.<hash> (Revoked)' -> must be ignored!
    """
    if release.get("draft", False):
        return None

    name = (release.get("name") or "").strip()
    tag = (release.get("tag_name") or "").strip()
    body = (release.get("body") or "")

    combined_text = f"{name} {tag}".lower()

    # Skip revoked releases
    if "revoked" in combined_text or "(revoked)" in body.lower():
        return None

    # Check title / tag keywords
    if "alpha" in combined_text:
        return "alpha"
    if "beta" in combined_text:
        return "beta"
    if "stable" in combined_text:
        return "beta"

    # Fallback to prerelease flag
    if release.get("prerelease", False):
        return "alpha"
    return "beta"


def determine_tag_channel(tag: str, releases: List[Dict[str, Any]]) -> str:
    """Finds channel for an explicit or pinned tag; defaults to 'pinned' if unknown."""
    for r in releases:
        if r.get("tag_name") == tag:
            combined = f"{r.get('name', '')} {r.get('tag_name', '')}".lower()
            if "alpha" in combined:
                return "alpha"
            if "beta" in combined or "stable" in combined:
                return "beta"
            if r.get("prerelease", False):
                return "alpha"
            return "beta"
    if "alpha" in tag.lower():
        return "alpha"
    if "beta" in tag.lower():
        return "beta"
    return "pinned"


def parse_version_tuple(v_str: str) -> Tuple[int, ...]:
    """Parses a version string into a comparable tuple of ints, e.g. 'v2.8.2.4c89b69' -> (2, 8, 2, 4)."""
    if not v_str:
        return (0, 0, 0)
    cleaned = v_str.lstrip("v").strip().split(".")
    nums = []
    for part in cleaned:
        m = re.match(r"^(\d+)", part)
        if m:
            nums.append(int(m.group(1)))
        else:
            break
    while len(nums) < 3:
        nums.append(0)
    return tuple(nums)


def is_version_supported(tag: str, min_version: Optional[str] = None, max_version: Optional[str] = None) -> bool:
    """Verifies if upstream release tag satisfies [min_version, max_version] constraints."""
    if not min_version and not max_version:
        return True
    tag_ver = parse_version_tuple(tag)
    if min_version and tag_ver < parse_version_tuple(min_version):
        return False
    if max_version and tag_ver > parse_version_tuple(max_version):
        return False
    return True


def is_build_complete(output_subpath: Path) -> bool:
    """
    Checks if a given variant build directory already contains completed artifacts
    (build-manifest.json or firmware binaries).
    """
    if not output_subpath.is_dir():
        return False
    manifest = output_subpath / "build-manifest.json"
    if manifest.is_file():
        return True

    # Check for binaries if manifest isn't present
    binary_exts = {".bin", ".uf2", ".hex", ".elf", ".zip"}
    for child in output_subpath.iterdir():
        if child.is_file() and child.suffix in binary_exts:
            return True
    return False


def resolve_plan(
    config: Dict[str, Any],
    repo_root: Path,
    force_tag: Optional[str] = None,
    force_rebuild: bool = False,
) -> Tuple[List[Dict[str, Any]], List[str]]:
    """
    Computes:
      1. active_folders: release directory names that must be kept under ./builds/
      2. matrix_items: compile jobs needed for GitHub Actions
    """
    release_channels = config.get("release_channels", {})
    retention = config.get("retention", {})
    variants_cfg = config.get("variants", {})
    custom_profiles = config.get("custom_profiles", [])

    track_alpha = release_channels.get("track_alpha", True)
    track_beta = release_channels.get("track_beta", True)
    pinned_tags = [str(t).strip() for t in release_channels.get("pinned_tags", []) if str(t).strip()]

    keep_latest_alpha = int(retention.get("keep_latest_alpha", 1))
    keep_latest_beta = int(retention.get("keep_latest_beta", 1))

    custom_variants = variants_cfg.get("custom", [])
    upstream_variants = variants_cfg.get("upstream", [])

    # Detect highest existing release tags in ./builds/ to prevent regressions
    # (e.g. if an upstream release is revoked or hidden, do not revert to an older release)
    builds_dir = repo_root / "builds"
    existing_alphas: List[str] = []
    existing_betas: List[str] = []
    if builds_dir.is_dir():
        for item in builds_dir.iterdir():
            if item.is_dir():
                if item.name.startswith("alpha-"):
                    existing_alphas.append(item.name[len("alpha-"):])
                elif item.name.startswith("beta-"):
                    existing_betas.append(item.name[len("beta-"):])
    existing_alphas.sort(key=parse_version_tuple, reverse=True)
    existing_betas.sort(key=parse_version_tuple, reverse=True)
    highest_existing_alpha = existing_alphas[0] if existing_alphas else None
    highest_existing_beta = existing_betas[0] if existing_betas else None

    # Fetch releases
    releases = fetch_upstream_releases(per_page=30)

    selected_alphas: List[str] = []
    selected_betas: List[str] = []

    seen_latest_alpha = False
    seen_latest_beta = False
    for rel in releases:
        tag = rel.get("tag_name", "").strip()
        if not tag:
            continue
        name = (rel.get("name") or "").strip()
        body = rel.get("body") or ""
        combined_text = f"{name} {tag}".lower()
        is_revoked = "revoked" in combined_text or "(revoked)" in body.lower()
        is_alpha = "alpha" in combined_text or rel.get("prerelease", False)
        channel = classify_release(rel)

        if is_alpha:
            if not seen_latest_alpha:
                seen_latest_alpha = True
                if not is_revoked and channel == "alpha" and track_alpha and len(selected_alphas) < keep_latest_alpha:
                    if tag not in selected_alphas:
                        selected_alphas.append(tag)
        else:
            if not seen_latest_beta:
                seen_latest_beta = True
                if not is_revoked and channel == "beta" and track_beta and len(selected_betas) < keep_latest_beta:
                    if tag not in selected_betas:
                        selected_betas.append(tag)

    # If no newer alpha/beta was found upstream (e.g. latest was revoked), retain highest existing built release
    if track_alpha and not selected_alphas and highest_existing_alpha:
        selected_alphas.append(highest_existing_alpha)
    if track_beta and not selected_betas and highest_existing_beta:
        selected_betas.append(highest_existing_beta)

    # Build active target tag map: tag -> channel
    active_targets: Dict[str, str] = {}
    for tag in selected_alphas:
        active_targets[tag] = "alpha"
    for tag in selected_betas:
        active_targets[tag] = "beta"
    for tag in pinned_tags:
        if tag not in active_targets:
            active_targets[tag] = determine_tag_channel(tag, releases)

    if force_tag:
        clean_force_tag = force_tag.strip()
        if clean_force_tag and clean_force_tag not in active_targets:
            active_targets[clean_force_tag] = determine_tag_channel(clean_force_tag, releases)

    # Active folders that retention should preserve (e.g. ['alpha-v2.8.1.8e6a88d', 'beta-v2.7.26.54e0d8d'])
    active_folders = [f"{ch}-{tag}" for tag, ch in active_targets.items()]

    matrix_items: List[Dict[str, Any]] = []

    for tag, channel in active_targets.items():
        # 1. Vanilla builds
        # A. Custom variants with build_vanilla: true
        for cv in custom_variants:
            if cv.get("build_vanilla", False):
                if not is_version_supported(tag, cv.get("min_version"), cv.get("max_version")):
                    continue
                subpath = f"builds/{channel}-{tag}/vanilla/{cv['name']}"
                safe_variant = re.sub(r'[^a-zA-Z0-9_\-\.]', '_', cv["name"])
                artifact_name = f"build-{channel}-{tag}-vanilla-{safe_variant}"
                cv_patches = " ".join(str(p).strip() for p in cv.get("local_patches", []) if str(p).strip())
                item = {
                    "tag": tag,
                    "channel": channel,
                    "build_type": "vanilla",
                    "variant_name": cv["name"],
                    "pio_env": cv["pio_env"],
                    "is_custom_variant": True,
                    "variant_dir": cv.get("variant_dir", cv["name"]),
                    "upstream_prs": "",
                    "local_patches": cv_patches,
                    "build_flags": "",
                    "output_subpath": subpath,
                    "artifact_name": artifact_name,
                }
                if force_rebuild or not is_build_complete(repo_root / subpath):
                    matrix_items.append(item)

        # B. Upstream variants with build_vanilla: true
        for uv in upstream_variants:
            if uv.get("build_vanilla", False):
                if not is_version_supported(tag, uv.get("min_version"), uv.get("max_version")):
                    continue
                subpath = f"builds/{channel}-{tag}/vanilla/{uv['name']}"
                safe_variant = re.sub(r'[^a-zA-Z0-9_\-\.]', '_', uv["name"])
                artifact_name = f"build-{channel}-{tag}-vanilla-{safe_variant}"
                item = {
                    "tag": tag,
                    "channel": channel,
                    "build_type": "vanilla",
                    "variant_name": uv["name"],
                    "pio_env": uv["pio_env"],
                    "is_custom_variant": False,
                    "variant_dir": "",
                    "upstream_prs": "",
                    "local_patches": "",
                    "build_flags": "",
                    "output_subpath": subpath,
                    "artifact_name": artifact_name,
                }
                if force_rebuild or not is_build_complete(repo_root / subpath):
                    matrix_items.append(item)

        # 2. Custom profile builds (PRs, Patches, Games, etc.)
        for profile in custom_profiles:
            if not profile.get("enabled", False):
                continue
            
            # Version constraint filter
            if not is_version_supported(tag, profile.get("min_version"), profile.get("max_version")):
                continue

            # Channel filter (optional: e.g. ["alpha"] or ["beta"])
            profile_channels = profile.get("channels") or profile.get("target_channels")
            if profile_channels:
                allowed_channels = {str(c).strip().lower() for c in profile_channels}
                if channel.lower() not in allowed_channels:
                    continue

            profile_name = profile["profile_name"]
            prs = " ".join(str(p).strip() for p in profile.get("upstream_prs", []) if str(p).strip())
            patches = " ".join(str(p).strip() for p in profile.get("local_patches", []) if str(p).strip())
            build_flags = str(profile.get("build_flags", "") or "").strip()
            target_spec = profile.get("target_variants", ["all"])
            if not target_spec:
                target_spec = ["all"]
            if isinstance(target_spec, str):
                target_spec = [target_spec]

            exclude_spec = profile.get("exclude_variants", [])
            if isinstance(exclude_spec, str):
                exclude_spec = [exclude_spec]
            exclude_set = {str(x).strip().lower() for x in exclude_spec}

            # Determine matching variants
            matched_variants: List[Tuple[Dict[str, Any], bool]] = []
            target_set = {str(x).strip().lower() for x in target_spec}

            include_all = "all" in target_set or "*" in target_set
            include_all_custom = include_all or "all_custom" in target_set or "custom" in target_set
            include_all_upstream = include_all or "all_upstream" in target_set or "upstream" in target_set

            for cv in custom_variants:
                cv_name = cv["name"].lower()
                cv_env = cv.get("pio_env", "").lower()
                if cv_name in exclude_set or cv_env in exclude_set:
                    continue
                if not is_version_supported(tag, cv.get("min_version"), cv.get("max_version")):
                    continue
                if include_all_custom or cv_name in target_set or cv_env in target_set:
                    matched_variants.append((cv, True))

            for uv in upstream_variants:
                uv_name = uv["name"].lower()
                uv_env = uv.get("pio_env", "").lower()
                if uv_name in exclude_set or uv_env in exclude_set:
                    continue
                if not is_version_supported(tag, uv.get("min_version"), uv.get("max_version")):
                    continue
                if include_all_upstream or uv_name in target_set or uv_env in target_set:
                    matched_variants.append((uv, False))

            safe_build_type = re.sub(r'[^a-zA-Z0-9_\-\.]', '_', profile_name)

            for var, is_custom in matched_variants:
                subpath = f"builds/{channel}-{tag}/{profile_name}/{var['name']}"
                safe_variant = re.sub(r'[^a-zA-Z0-9_\-\.]', '_', var["name"])
                artifact_name = f"build-{channel}-{tag}-{safe_build_type}-{safe_variant}"
                var_patches = [str(p).strip() for p in var.get("local_patches", []) if str(p).strip()]
                all_patches = [str(p).strip() for p in profile.get("local_patches", []) if str(p).strip()] + var_patches
                combined_patches = " ".join(dict.fromkeys(all_patches))
                item = {
                    "tag": tag,
                    "channel": channel,
                    "build_type": profile_name,
                    "variant_name": var["name"],
                    "pio_env": var["pio_env"],
                    "is_custom_variant": is_custom,
                    "variant_dir": var.get("variant_dir", var["name"]) if is_custom else "",
                    "upstream_prs": prs,
                    "local_patches": combined_patches,
                    "build_flags": build_flags,
                    "output_subpath": subpath,
                    "artifact_name": artifact_name,
                }
                if force_rebuild or not is_build_complete(repo_root / subpath):
                    matrix_items.append(item)

    return matrix_items, active_folders


def main() -> None:
    parser = argparse.ArgumentParser(description="Resolve Meshtastic build matrix for GitHub Actions")
    parser.add_argument("--config", default="build-config.yaml", help="Path to build-config.yaml")
    parser.add_argument("--force-tag", default=os.environ.get("FORCE_TAG", ""), help="Force a specific upstream tag")
    parser.add_argument(
        "--force-rebuild",
        action="store_true",
        default=os.environ.get("FORCE_REBUILD", "").lower() in ("true", "1", "yes"),
        help="Force rebuild even if outputs exist",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent
    config_path = repo_root / args.config

    config = load_build_config(config_path)
    matrix_items, active_folders = resolve_plan(
        config=config,
        repo_root=repo_root,
        force_tag=args.force_tag.strip() or None,
        force_rebuild=args.force_rebuild,
    )

    has_builds = "true" if len(matrix_items) > 0 else "false"
    matrix_json = json.dumps({"include": matrix_items}, separators=(",", ":"))
    active_folders_json = json.dumps(active_folders, separators=(",", ":"))

    print("=" * 60)
    print("Meshtastic Build Matrix Resolver")
    print("=" * 60)
    print(f"Active Folders ({len(active_folders)}): {active_folders}")
    print(f"Pending Builds ({len(matrix_items)}):")
    for item in matrix_items:
        print(f"  - [{item['channel']}] {item['tag']} | {item['variant_name']} ({item['build_type']}) -> {item['output_subpath']}")
    print(f"has_builds: {has_builds}")
    print("=" * 60)

    # Write to GITHUB_OUTPUT if available
    gh_output_file = os.environ.get("GITHUB_OUTPUT")
    if gh_output_file:
        with open(gh_output_file, "a", encoding="utf-8") as gh_out:
            gh_out.write(f"has_builds={has_builds}\n")
            gh_out.write(f"matrix={matrix_json}\n")
            gh_out.write(f"active_folders={active_folders_json}\n")
        print(f"Wrote outputs to GITHUB_OUTPUT ({gh_output_file})")


if __name__ == "__main__":
    main()

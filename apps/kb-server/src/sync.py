"""Git sync — clone, pull, index markdown files from multiple repos."""

import hashlib
import logging
import os
import re
import subprocess
from pathlib import Path

from .config import config, RepoConfig
from .db import SessionLocal
from .models import Document
from .storage import upsert_document, delete_missing

logger = logging.getLogger(__name__)


def _git_url(url: str) -> str:
    """Build git URL with token if provided."""
    if config.GH_TOKEN and "github.com" in url:
        url = url.replace("https://", f"https://{config.GH_TOKEN}@")
    return url


def _run_git(*args: str, cwd: str | None = None) -> subprocess.CompletedProcess:
    cmd = ["git"] + list(args)
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=120)


def _is_remote(path: str) -> bool:
    """Check if a path is a remote git URL vs local directory."""
    return path.startswith("https://") or path.startswith("git@") or path.startswith("http://")


def _sync_repo(repo: RepoConfig) -> str:
    """Sync a single repo. Returns the local path to index."""
    if _is_remote(repo.path):
        local_path = f"/tmp/kb-{repo.name}"
        if os.path.exists(os.path.join(local_path, ".git")):
            logger.info(f"[{repo.name}] Pulling latest from {repo.branch}...")
            result = _run_git("pull", "origin", repo.branch, cwd=local_path)
            if result.returncode != 0:
                logger.error(f"[{repo.name}] git pull failed: {result.stderr}")
                import shutil
                shutil.rmtree(local_path, ignore_errors=True)
                _clone_repo(repo, local_path)
        else:
            _clone_repo(repo, local_path)
        return local_path
    else:
        # Local path — use directly, no clone needed
        if not os.path.exists(repo.path):
            logger.warning(f"[{repo.name}] Path {repo.path} does not exist — skipping")
            return ""
        logger.info(f"[{repo.name}] Using local path: {repo.path}")
        return repo.path


def _clone_repo(repo: RepoConfig, local_path: str):
    logger.info(f"[{repo.name}] Cloning {repo.path} (branch: {repo.branch})...")
    result = _run_git(
        "clone", "--branch", repo.branch, "--single-branch", "--depth", "1",
        _git_url(repo.path), local_path,
    )
    if result.returncode != 0:
        logger.error(f"[{repo.name}] git clone failed: {result.stderr}")


def _parse_frontmatter(content: str) -> tuple[str, str]:
    """Extract keywords from YAML-ish frontmatter."""
    keywords = ""
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            frontmatter = parts[1]
            content = parts[2].strip()
            for line in frontmatter.strip().split("\n"):
                if line.startswith("keywords:"):
                    keywords = line.split(":", 1)[1].strip()
    return keywords, content


def _extract_title(content: str) -> str:
    """Extract first H1 heading as title."""
    for line in content.split("\n"):
        line = line.strip()
        if line.startswith("# "):
            return line[2:].strip()
    return ""


def _normalize_partition(name: str) -> str:
    """Normalize partition name: lowercase, alphanumeric + hyphens only."""
    name = name.lower().strip()
    name = re.sub(r"[^a-z0-9-]", "-", name)
    name = re.sub(r"-+", "-", name)
    return name.strip("-")


def _index_path(repo_name: str, repo_path: str) -> set[str]:
    """Index markdown files from a local path. Returns set of indexed paths."""
    if not repo_path or not os.path.exists(repo_path):
        return set()

    db = SessionLocal()
    current_paths: set[str] = set()

    try:
        for md_file in Path(repo_path).rglob("*.md"):
            rel_path = str(md_file.relative_to(repo_path))
            if any(part.startswith(".") for part in rel_path.split("/")):
                continue

            # Partition naming:
            # - If repo has subdirectories, use top-level folder as partition
            # - Prefix with repo name to avoid collisions between repos
            parts = rel_path.split("/")
            if len(parts) > 1:
                sub_partition = _normalize_partition(parts[0])
                # If repo name == partition name, don't double-prefix
                if sub_partition == _normalize_partition(repo_name):
                    partition = sub_partition
                else:
                    partition = f"{_normalize_partition(repo_name)}-{sub_partition}"
            else:
                partition = _normalize_partition(repo_name)

            # Use repo_name as path prefix to avoid collisions
            full_path = f"{repo_name}/{rel_path}"

            raw = md_file.read_text(encoding="utf-8", errors="replace")
            content_hash = hashlib.sha256(raw.encode()).hexdigest()[:16]
            keywords, clean_content = _parse_frontmatter(raw)
            title = _extract_title(clean_content) or md_file.stem

            doc = Document(
                path=full_path,
                partition=partition,
                title=title,
                content=raw,
                keywords=keywords,
                hash=content_hash,
            )
            upsert_document(db, doc)
            current_paths.add(full_path)

        logger.info(f"[{repo_name}] Indexed {len(current_paths)} documents")

    finally:
        db.close()

    return current_paths


def sync():
    """Full sync: pull + re-index all configured repos."""
    if not config.repos:
        logger.info("No repos configured — nothing to sync")
        return

    all_paths: set[str] = set()

    for repo in config.repos:
        local_path = _sync_repo(repo)
        paths = _index_path(repo.name, local_path)
        all_paths.update(paths)

    # Remove docs that no longer exist in any repo
    db = SessionLocal()
    try:
        delete_missing(db, all_paths)
    finally:
        db.close()

    logger.info(f"Sync complete: {len(all_paths)} total documents across {len(config.repos)} repos")

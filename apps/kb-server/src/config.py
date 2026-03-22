"""Configuration from environment variables."""

import json
import os
from dataclasses import dataclass, field


@dataclass
class RepoConfig:
    """A single knowledge base repo to index."""
    name: str          # partition prefix (e.g., "frontend", "backend")
    path: str          # local path or git URL
    branch: str = "main"


class Config:
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///kb.db")
    KB_AUTH_TOKEN: str = os.getenv("KB_AUTH_TOKEN", "")
    GH_TOKEN: str = os.getenv("GH_TOKEN", "")
    SYNC_INTERVAL_SECONDS: int = int(os.getenv("SYNC_INTERVAL_SECONDS", "300"))
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8080"))

    # Multi-repo support:
    #
    # Option 1 (simple): Single repo via env vars
    #   REPO_URL=https://github.com/org/kb-docs.git
    #   REPO_BRANCH=main
    #
    # Option 2 (multi): Comma-separated name:path pairs
    #   REPOS=frontend:/path/to/frontend-kb,backend:/path/to/backend-kb
    #
    # Option 3 (advanced): JSON config
    #   REPOS_JSON=[{"name":"frontend","path":"/path/to/frontend-kb"},{"name":"backend","path":"/path/to/backend-kb"}]
    #
    # Local paths are indexed directly. Remote URLs are cloned to /tmp/kb-<name>.

    repos: list[RepoConfig] = field(default_factory=list)

    def __init__(self):
        self.repos = self._parse_repos()

    def _parse_repos(self) -> list[RepoConfig]:
        repos = []

        # Option 3: JSON config (highest priority)
        repos_json = os.getenv("REPOS_JSON", "")
        if repos_json:
            for entry in json.loads(repos_json):
                repos.append(RepoConfig(
                    name=entry["name"],
                    path=entry["path"],
                    branch=entry.get("branch", "main"),
                ))
            return repos

        # Option 2: Comma-separated name:path pairs
        repos_str = os.getenv("REPOS", "")
        if repos_str:
            for pair in repos_str.split(","):
                pair = pair.strip()
                if ":" in pair:
                    name, path = pair.split(":", 1)
                    repos.append(RepoConfig(name=name.strip(), path=path.strip()))
                else:
                    # Just a path — derive name from directory name
                    repos.append(RepoConfig(name=os.path.basename(pair.strip()), path=pair.strip()))
            return repos

        # Option 1: Single repo via REPO_URL (backwards compatible)
        repo_url = os.getenv("REPO_URL", "")
        if repo_url:
            repos.append(RepoConfig(
                name="_default",
                path=repo_url,
                branch=os.getenv("REPO_BRANCH", "main"),
            ))

        return repos


config = Config()

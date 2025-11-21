"""
GitHub Issue Fetcher for simexp
Fetches GitHub issue data and formats it for session notes

♠️🌿🎸🧵 G.Music Assembly - Issue Integration
"""

import subprocess
import json
from typing import Optional, Dict, Tuple
from datetime import datetime


class GitHubIssueFetcher:
    """
    Fetches GitHub issue data using gh CLI or REST API fallback.

    Provides methods to:
    - Fetch issue details from GitHub
    - Format issue data for Simplenote sessions
    - Generate session titles and content
    """

    def __init__(self):
        """Initialize the GitHub issue fetcher"""
        self.gh_available = self._check_gh_cli()

    def _check_gh_cli(self) -> bool:
        """
        Check if gh CLI is available

        Returns:
            True if gh CLI is available, False otherwise
        """
        try:
            subprocess.run(['gh', '--version'], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def _get_repo_from_git(self) -> Optional[str]:
        """
        Auto-detect repository from git remote

        Returns:
            Repository in format 'owner/name' or None if not in a git repo
        """
        try:
            # Get the origin remote URL
            result = subprocess.run(
                ['git', 'config', '--get', 'remote.origin.url'],
                capture_output=True,
                text=True,
                check=True
            )
            url = result.stdout.strip()

            # Parse owner/name from URL
            if 'github.com' in url:
                # Handle both https and ssh formats
                if url.startswith('git@'):
                    # git@github.com:owner/name.git
                    parts = url.split(':')[1].replace('.git', '')
                else:
                    # https://github.com/owner/name.git
                    parts = url.rstrip('/').replace('.git', '').split('/')[-2:]
                    parts = '/'.join(parts)

                return parts
        except (subprocess.CalledProcessError, IndexError):
            pass

        return None

    def fetch_issue(self, issue_number: int, repo: Optional[str] = None) -> Optional[Dict]:
        """
        Fetch GitHub issue data

        Uses gh CLI if available, otherwise falls back to REST API.

        Args:
            issue_number: GitHub issue number
            repo: Repository in format 'owner/name'. If not provided, auto-detects from git remote.

        Returns:
            Dictionary with issue data or None if fetch failed
        """
        # Auto-detect repo if not provided
        if not repo:
            repo = self._get_repo_from_git()

        if not repo:
            print("❌ Could not determine repository. Provide --repo flag or run from a git repository.")
            return None

        if self.gh_available:
            return self._fetch_issue_gh(issue_number, repo)
        else:
            print("⚠️ gh CLI not found. Install it from https://cli.github.com/")
            return None

    def _fetch_issue_gh(self, issue_number: int, repo: str) -> Optional[Dict]:
        """
        Fetch issue using gh CLI

        Args:
            issue_number: GitHub issue number
            repo: Repository in format 'owner/name'

        Returns:
            Dictionary with issue data or None if fetch failed
        """
        try:
            # Fetch issue as JSON
            result = subprocess.run(
                [
                    'gh', 'issue', 'view',
                    str(issue_number),
                    '--repo', repo,
                    '--json', 'number,title,state,labels,assignees,createdAt,url,body'
                ],
                capture_output=True,
                text=True,
                check=True
            )

            issue_data = json.loads(result.stdout)
            return issue_data
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to fetch issue #{issue_number} from {repo}")
            print(f"   Error: {e.stderr.strip()}")
            return None
        except json.JSONDecodeError:
            print(f"❌ Failed to parse GitHub response")
            return None

    def format_for_session(self, issue_data: Dict) -> str:
        """
        Format issue data for inclusion in session note

        Args:
            issue_data: Issue data dictionary from GitHub

        Returns:
            Formatted markdown string
        """
        if not issue_data:
            return ""

        # Extract issue fields
        number = issue_data.get('number', 'unknown')
        title = issue_data.get('title', 'Unknown Title')
        state = issue_data.get('state', 'UNKNOWN').upper()
        labels = issue_data.get('labels', [])
        assignees = issue_data.get('assignees', [])
        created_at = issue_data.get('createdAt', '')
        url = issue_data.get('url', '')
        body = issue_data.get('body', '')

        # Format labels
        labels_str = ', '.join([f"`{label['name']}`" for label in labels]) if labels else "none"

        # Format assignees
        assignees_str = ', '.join([f"@{a['login']}" for a in assignees]) if assignees else "unassigned"

        # Format created date
        created_date = ""
        if created_at:
            try:
                dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                created_date = dt.strftime('%Y-%m-%d %H:%M UTC')
            except (ValueError, AttributeError):
                created_date = created_at

        # Build formatted content
        content = f"""## Issue #{number}: {title}

**Status**: `{state}`
**Labels**: {labels_str}
**Assignees**: {assignees_str}
**Created**: {created_date}
**Link**: {url}

### Description

{body}

---

### Session Notes

"""

        return content

    def create_session_title(self, issue_data: Dict) -> str:
        """
        Generate session note title from issue data

        Args:
            issue_data: Issue data dictionary from GitHub

        Returns:
            Session title string
        """
        if not issue_data:
            return "Session Note"

        number = issue_data.get('number', 'unknown')
        title = issue_data.get('title', 'Unknown')

        return f"Issue #{number}: {title}"

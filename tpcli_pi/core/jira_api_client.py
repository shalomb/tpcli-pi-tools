"""
Jira API client for Phase 2B: Direct Jira story integration.

Fetches stories directly from Jira API to display story hierarchy
in markdown (epics → stories with status, assignee, story points, AC).
"""

import os
import requests
from typing import Any, Optional, List
from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class JiraStory:
    """Represents a Jira story/issue."""
    key: str
    summary: str
    status: str
    assignee: Optional[str]
    story_points: Optional[int]
    description: Optional[str]

    def __repr__(self) -> str:
        """String representation without sensitive data."""
        return (f"JiraStory(key={self.key}, summary={self.summary}, "
                f"status={self.status}, assignee={self.assignee})")


class JiraAPIClient:
    """
    Client for Jira API v2/v3.

    Features:
    - Fetch stories from epic via JQL query
    - Parse story metadata (status, assignee, points)
    - Extract acceptance criteria from description
    - Handle API errors gracefully
    - Rate limit handling with backoff
    - Caching for performance
    """

    def __init__(
        self,
        base_url: str = "",
        token: str = "",
        timeout: int = 10,
        max_retries: int = 3,
    ):
        """
        Initialize Jira API client.

        Args:
            base_url: Jira instance URL (e.g., https://jira.takeda.com)
            token: Jira API token (or load from JIRA_TOKEN env var)
            timeout: API request timeout in seconds
            max_retries: Number of retries for rate-limited requests
        """
        # Allow loading from environment if not provided
        self.base_url = base_url or os.getenv("JIRA_URL", "https://jira.takeda.com")
        self.token = token or os.getenv("JIRA_TOKEN", "")
        self.timeout = timeout
        self.max_retries = max_retries

        # Cache for stories (key: epic_key, value: list of stories)
        self._story_cache: dict[str, List[JiraStory]] = {}
        self._cache_timestamps: dict[str, datetime] = {}
        self._cache_ttl = 3600  # 1 hour

    def fetch_stories_by_epic(self, epic_key: str) -> List[JiraStory]:
        """
        Fetch all stories under a Jira epic.

        Args:
            epic_key: Jira epic key (e.g., "DAD-2652")

        Returns:
            List of JiraStory objects, ordered by key

        Raises:
            ValueError: If epic_key is invalid
            requests.RequestException: If API call fails
        """
        if not epic_key or not isinstance(epic_key, str):
            raise ValueError(f"Invalid epic key: {epic_key}")

        # Check cache
        if self._is_cached(epic_key):
            return self._story_cache[epic_key]

        # Validate credentials
        if not self.token:
            raise ValueError(
                "JIRA_TOKEN environment variable not set. "
                "Set it with: export JIRA_TOKEN='your-token'"
            )

        try:
            # JQL query to find all stories under epic
            jql = f"parent = {epic_key} ORDER BY key ASC"
            stories = self._search_jira(jql)

            # Cache the results
            self._story_cache[epic_key] = stories
            self._cache_timestamps[epic_key] = datetime.now()

            return stories

        except requests.exceptions.Timeout:
            raise TimeoutError(
                f"Jira API timeout after {self.timeout}s. "
                "Falling back to Phase 2A (no stories shown)."
            )
        except requests.exceptions.RequestException as e:
            raise requests.RequestException(
                f"Jira API error: {str(e)}. "
                "Falling back to Phase 2A (no stories shown)."
            )

    def _search_jira(self, jql: str) -> List[JiraStory]:
        """
        Execute JQL search against Jira API.

        Args:
            jql: JQL query string

        Returns:
            List of JiraStory objects parsed from response
        """
        url = f"{self.base_url}/rest/api/3/search"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        params = {
            "jql": jql,
            "fields": "key,summary,status,assignee,customfield_10001,description",
            "maxResults": 500,  # Limit to prevent huge responses
        }

        # Retry logic for rate limiting
        for attempt in range(self.max_retries):
            try:
                response = requests.get(
                    url,
                    headers=headers,
                    params=params,
                    timeout=self.timeout,
                )

                # Handle rate limiting (429)
                if response.status_code == 429:
                    if attempt < self.max_retries - 1:
                        import time
                        wait_time = 2 ** attempt  # Exponential backoff
                        time.sleep(wait_time)
                        continue
                    else:
                        raise requests.RequestException(
                            "Jira API rate limit exceeded. Too many requests."
                        )

                response.raise_for_status()
                return self._parse_search_response(response.json())

            except requests.exceptions.Timeout:
                raise
            except requests.exceptions.RequestException:
                raise

        return []

    def _parse_search_response(self, response_data: dict[str, Any]) -> List[JiraStory]:
        """
        Parse Jira API search response into Story objects.

        Args:
            response_data: JSON response from Jira API

        Returns:
            List of JiraStory objects
        """
        stories = []

        for issue in response_data.get("issues", []):
            try:
                fields = issue.get("fields", {})

                # Extract story points (customfield_10001 is standard, but may vary)
                story_points = None
                for field_key in fields:
                    if "story" in field_key.lower() or "point" in field_key.lower():
                        if isinstance(fields[field_key], (int, float)):
                            story_points = int(fields[field_key])
                            break

                # Fallback: try common custom field IDs
                if story_points is None:
                    story_points = fields.get("customfield_10001")
                    if isinstance(story_points, (int, float)):
                        story_points = int(story_points)
                    else:
                        story_points = None

                # Extract assignee
                assignee_data = fields.get("assignee")
                assignee = None
                if assignee_data and isinstance(assignee_data, dict):
                    assignee = assignee_data.get("displayName")

                # Build story object
                story = JiraStory(
                    key=issue.get("key", "UNKNOWN"),
                    summary=fields.get("summary", "Untitled"),
                    status=self._extract_status(fields.get("status")),
                    assignee=assignee,
                    story_points=story_points,
                    description=fields.get("description"),
                )

                stories.append(story)

            except (KeyError, AttributeError, ValueError):
                # Skip malformed issues
                continue

        return stories

    def _extract_status(self, status_data: Optional[Any]) -> str:
        """
        Extract status name from Jira status object.

        Args:
            status_data: Status data from Jira API

        Returns:
            Status name string
        """
        if not status_data:
            return "Unknown"

        if isinstance(status_data, dict):
            return status_data.get("name", "Unknown")

        if isinstance(status_data, str):
            return status_data

        return "Unknown"

    def _is_cached(self, epic_key: str) -> bool:
        """
        Check if epic stories are in valid cache.

        Args:
            epic_key: Epic key to check

        Returns:
            True if cached and not expired
        """
        if epic_key not in self._story_cache:
            return False

        if epic_key not in self._cache_timestamps:
            return False

        # Check TTL
        cached_at = self._cache_timestamps[epic_key]
        age = (datetime.now() - cached_at).total_seconds()

        return age < self._cache_ttl

    def clear_cache(self, epic_key: Optional[str] = None) -> None:
        """
        Clear cache for one or all epics.

        Args:
            epic_key: Specific epic to clear, or None for all
        """
        if epic_key:
            self._story_cache.pop(epic_key, None)
            self._cache_timestamps.pop(epic_key, None)
        else:
            self._story_cache.clear()
            self._cache_timestamps.clear()

    def __repr__(self) -> str:
        """String representation without exposing token."""
        return (
            f"JiraAPIClient(base_url={self.base_url}, "
            f"token={'***' if self.token else 'NOT_SET'})"
        )

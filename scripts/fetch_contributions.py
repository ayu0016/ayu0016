"""
Fetch layer.

Responsibility: retrieve raw contribution data from GitHub. Nothing else.
No XP, level, or color logic belongs in this file.

Requires two environment variables:
  GH_USERNAME - the GitHub username to fetch (public data only)
  GH_TOKEN    - a token with at least `read:user` scope

Uses only the Python standard library — no pip install required.
"""

import json
import os
import sys
import urllib.request
from datetime import datetime, timezone

GITHUB_GRAPHQL_URL = "https://api.github.com/graphql"

QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays {
            date
            contributionCount
          }
        }
      }
    }
  }
}
"""


def fetch_contributions(username: str, token: str) -> dict:
    payload = json.dumps({"query": QUERY, "variables": {"login": username}}).encode("utf-8")
    req = urllib.request.Request(
        GITHUB_GRAPHQL_URL,
        data=payload,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "trainer-journey-bot",
        },
        method="POST",
    )

    with urllib.request.urlopen(req, timeout=30) as resp:
        body = json.loads(resp.read().decode("utf-8"))

    if "errors" in body:
        raise RuntimeError(f"GitHub GraphQL error: {body['errors']}")

    user = body.get("data", {}).get("user")
    if user is None:
        raise RuntimeError(f"No such user, or contribution data is private: {username}")

    calendar = user["contributionsCollection"]["contributionCalendar"]

    weeks_out = []
    days_out = []
    for week in calendar["weeks"]:
        week_days = []
        for day in week["contributionDays"]:
            entry = {"date": day["date"], "count": day["contributionCount"]}
            week_days.append(entry)
            days_out.append(entry)
        weeks_out.append(week_days)

    return {
        "username": username,
        "totalContributions": calendar["totalContributions"],
        "weeks": weeks_out,
        "days": days_out,
        "fetchedAt": datetime.now(timezone.utc).isoformat(),
    }


def main():
    username = os.environ.get("GH_USERNAME")
    token = os.environ.get("GH_TOKEN")

    if not username:
        print("::error::GH_USERNAME is not set", file=sys.stderr)
        sys.exit(1)
    if not token:
        print(
            "::error::GH_TOKEN is not set. Add a PAT with 'read:user' scope "
            "as a repo secret (see README in this folder).",
            file=sys.stderr,
        )
        sys.exit(1)

    data = fetch_contributions(username, token)

    os.makedirs("data", exist_ok=True)
    with open("data/contributions.json", "w") as f:
        json.dump(data, f, indent=2)

    print(f"Fetched {len(data['days'])} days, {data['totalContributions']} total contributions.")


if __name__ == "__main__":
    main()

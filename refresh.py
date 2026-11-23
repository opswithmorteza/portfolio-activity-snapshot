"""Build a verified daily public portfolio snapshot for GitHub Pages."""
from __future__ import annotations

import datetime as dt
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

USER = "opswithmorteza"
ROOT = Path(__file__).resolve().parent
TEHRAN = ZoneInfo("Asia/Tehran")


class Calendar(HTMLParser):
    def __init__(self):
        super().__init__()
        self.cells, self.labels, self.tooltip = {}, {}, None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "td" and "data-date" in attrs and "data-level" in attrs:
            self.cells[attrs["id"]] = {"date": attrs["data-date"], "level": int(attrs["data-level"])}
        if tag == "tool-tip":
            self.tooltip = attrs.get("for")

    def handle_data(self, text):
        if self.tooltip:
            self.labels[self.tooltip] = self.labels.get(self.tooltip, "") + text

    def handle_endtag(self, tag):
        if tag == "tool-tip":
            self.tooltip = None

    def days(self):
        result = []
        for key, cell in self.cells.items():
            label = self.labels.get(key, "").strip()
            match = re.match(r"([\d,]+) contributions?\b", label)
            if label.startswith("No contributions"):
                count = 0
            elif match:
                count = int(match[1].replace(",", ""))
            else:
                raise ValueError("Unexpected GitHub contribution label")
            result.append({**cell, "count": count})
        if len(result) < 300:
            raise ValueError("Incomplete contribution calendar")
        return sorted(result, key=lambda day: day["date"])


def fetch(url: str) -> str:
    request = Request(url, headers={"User-Agent": "MortezaPortfolio-PublicSnapshot"})
    with urlopen(request, timeout=25) as response:
        return response.read().decode()


def main():
    now = dt.datetime.now(TEHRAN)
    today = now.date()
    profile = json.loads(fetch(f"https://api.github.com/users/{USER}"))
    years = {}
    for year in range(int(profile["created_at"][:4]), today.year + 1):
        calendar = Calendar()
        calendar.feed(fetch(f"https://github.com/users/{USER}/contributions?from={year}-01-01&to={year}-12-31"))
        years[str(year)] = [day for day in calendar.days() if day["date"] <= today.isoformat()]
    repos = []
    for page in range(1, 4):
        batch = json.loads(fetch(f"https://api.github.com/users/{USER}/repos?per_page=100&page={page}"))
        repos.extend(batch)
        if len(batch) < 100:
            break
    stats = {
        "publicRepos": profile["public_repos"],
        "originalRepos": sum(not repo["fork"] for repo in repos),
        "forks": sum(repo["fork"] for repo in repos),
        "stars": sum(repo["stargazers_count"] for repo in repos if not repo["fork"]),
    }
    timestamp = now.isoformat(timespec="seconds")
    snapshot = {
        "user": USER,
        "updatedAt": timestamp,
        "timezone": "Asia/Tehran",
        "source": f"https://github.com/{USER}",
        "years": years,
        "stats": stats,
    }
    public = ROOT / "public"
    history = ROOT / "history"
    public.mkdir(exist_ok=True)
    history.mkdir(exist_ok=True)
    (public / "github-activity.json").write_text(json.dumps(snapshot, separators=(",", ":")), encoding="utf-8")
    status = {"checkedAt": timestamp, "timezone": "Asia/Tehran", "user": USER, "projects": stats["publicRepos"], "stats": stats}
    (public / "status.json").write_text(json.dumps(status, separators=(",", ":")), encoding="utf-8")
    (history / f"{today.isoformat()}.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    (ROOT / "DAILY_STATUS.md").write_text(
        f"# Daily portfolio status\n\n- Checked: `{timestamp}` (Asia/Tehran)\n- Public projects: **{stats['publicRepos']}**\n- Original projects: **{stats['originalRepos']}**\n- Forks tracked: **{stats['forks']}**\n\nThis is a verified public-data snapshot; it contains no private activity or synthetic counts.\n",
        encoding="utf-8",
    )
    print(f"Verified snapshot written for {today}: {stats}")


if __name__ == "__main__":
    main()

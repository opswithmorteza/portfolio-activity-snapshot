# Portfolio Activity Snapshot

Public, verified daily snapshot for [Morteza Rajabi's portfolio](https://mortezarajabi.ir).

The GitHub Actions workflow runs daily at approximately **00:47 Asia/Tehran** and can also be started manually. It reads only public GitHub profile, repository and contribution-calendar data, then writes:

- `public/github-activity.json` — current contribution calendar and portfolio statistics for the website.
- `public/status.json` — lightweight project-count and timestamp response.
- `history/YYYY-MM-DD.json` — a dated, public verification record.
- `DAILY_STATUS.md` — human-readable latest check.

The workflow commits only after successfully collecting and validating public source data. It does not use private data, access tokens, or synthetic contribution counts. GitHub may delay scheduled workflows during platform load, so the time is approximate.

## Local run

```bash
python refresh.py
```

## Data source

All values are derived from the public profile at [github.com/opswithmorteza](https://github.com/opswithmorteza).

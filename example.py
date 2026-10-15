"""Hiring-signal tracker with the Job Boards Scraper on Apify.

Pulls every open job from a list of companies (Greenhouse, Lever, Ashby,
Workday, SmartRecruiters, Workable, Recruitee, Personio, Teamtailor, BambooHR),
saves them to jobs.csv, and prints per company: open roles, top departments,
remote share, roles posted in the last N days and the published salary range.

Usage:
    pip install -r requirements.txt
    set APIFY_TOKEN=<YOUR_APIFY_TOKEN>      (export on macOS/Linux)
    python example.py https://boards.greenhouse.io/stripe https://jobs.ashbyhq.com/notion palantir
"""
import csv
import os
import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone

from apify_client import ApifyClient

ACTOR_ID = "rel8ble/ats-job-boards-scraper"
RECENT_DAYS = 14

token = os.environ.get("APIFY_TOKEN", "<YOUR_APIFY_TOKEN>")
boards = sys.argv[1:] or ["https://boards.greenhouse.io/stripe", "https://jobs.ashbyhq.com/notion"]

client = ApifyClient(token)
run = client.actor(ACTOR_ID).call(run_input={
    "boards": boards,
    "includeDescription": False,  # listing fields only: fastest
})
jobs = list(client.dataset(run["defaultDatasetId"]).iterate_items())
print(f"{len(jobs)} open jobs across {len(boards)} board(s)\n")

fields = ["company", "ats", "title", "department", "location", "country",
          "workplaceType", "isRemote", "employmentType", "salaryMin", "salaryMax",
          "salaryCurrency", "publishedAt", "url"]
with open("jobs.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
    w.writeheader()
    w.writerows(jobs)

cutoff = datetime.now(timezone.utc) - timedelta(days=RECENT_DAYS)
by_company = defaultdict(list)
for job in jobs:
    by_company[job["company"]].append(job)

for company, rows in sorted(by_company.items(), key=lambda kv: -len(kv[1])):
    depts = Counter(r["department"] for r in rows if r.get("department"))
    remote = sum(1 for r in rows if r.get("workplaceType") == "remote" or r.get("isRemote"))
    recent = [r for r in rows if r.get("publishedAt")
              and datetime.fromisoformat(r["publishedAt"].replace("Z", "+00:00")) >= cutoff]
    paid = [r for r in rows if r.get("salaryMin") and r.get("salaryCurrency") == "USD"]
    print(f"{company} ({rows[0]['ats']}): {len(rows)} open roles, "
          f"{remote} remote, {len(recent)} posted in the last {RECENT_DAYS} days")
    if depts:
        print("  top departments: " + ", ".join(f"{d} ({n})" for d, n in depts.most_common(3)))
    if paid:
        lo = min(r["salaryMin"] for r in paid)
        hi = max(r["salaryMax"] or r["salaryMin"] for r in paid)
        print(f"  USD salary range on {len(paid)} postings: ${lo:,.0f} - ${hi:,.0f}")

print("\nSaved jobs.csv")

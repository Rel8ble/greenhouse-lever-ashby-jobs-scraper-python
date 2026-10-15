# Greenhouse, Lever, Ashby & Workday jobs scraper (Python) - company job postings API

Scrape every open job from any company's Greenhouse, Lever, Ashby, Workday, SmartRecruiters, Workable, Recruitee, Personio, Teamtailor or BambooHR job board with Python, using the [Job Boards Scraper](https://apify.com/rel8ble/ats-job-boards-scraper) on Apify. Pass a board URL, a careers page, a company website or just a company name; get back clean JSON rows: title, company, location, remote flag, department, employment type, salary range, posting date, description and apply link.

> Disclosure: I built this actor; it's a paid tool on Apify ($1.00 per 1,000 jobs).

It reads each platform's official public job feed over plain HTTP (no browser, no login), so a board with hundreds of jobs comes back in a couple of seconds.

## Why use it

- **One schema for ten ATS platforms.** Greenhouse departments, Lever categories, Ashby compensation and Workday's paged API all come out as the same flat row.
- **Hiring-signal lead generation.** Companies hiring SDRs need sales tools; companies hiring data engineers need data vendors. Run your account list daily and diff by `id`.
- **Job aggregators and recruiting tools.** Stable platform job ids for deduplication, apply links, full descriptions.
- **Salary and remote research.** Structured salary from Lever, Ashby, Recruitee and Teamtailor; US pay-transparency ranges parsed from descriptions elsewhere.

## Quick start (Python)

```bash
pip install apify-client
```

```python
from apify_client import ApifyClient

client = ApifyClient("<YOUR_APIFY_TOKEN>")

run = client.actor("rel8ble/ats-job-boards-scraper").call(run_input={
    "boards": [
        "https://boards.greenhouse.io/stripe",
        "https://jobs.ashbyhq.com/notion",
        "https://jobs.lever.co/palantir",
    ],
    "titleKeywords": ["engineer", "developer"],
    "locationKeywords": ["remote", "new york"],
    "postedAfter": "2026-10-01",
    "includeDescription": False,
})

for job in client.dataset(run["defaultDatasetId"]).iterate_items():
    print(job["company"], "|", job["title"], "|", job["location"], "|", job.get("salaryText"))
```

Get your token at https://console.apify.com/settings/integrations.

## Quick start (Node.js)

```js
import { ApifyClient } from 'apify-client';

const client = new ApifyClient({ token: '<YOUR_APIFY_TOKEN>' });
const run = await client.actor('rel8ble/ats-job-boards-scraper').call({
    boards: ['stripe', 'https://www.notion.com/careers'],
    remoteOnly: true,
});
const { items } = await client.dataset(run.defaultDatasetId).listItems();
console.log(items.map((j) => `${j.company}: ${j.title} (${j.location})`));
```

## Full example: hiring-signal tracker

[`example.py`](example.py) pulls every open job for a list of companies, writes `jobs.csv`, and prints per company the number of open roles, top departments, remote count, roles posted in the last 14 days and the published USD salary range.

```bash
pip install -r requirements.txt
set APIFY_TOKEN=<YOUR_APIFY_TOKEN>        # export APIFY_TOKEN=... on macOS/Linux
python example.py https://boards.greenhouse.io/stripe https://jobs.ashbyhq.com/notion palantir
```

Output line for Notion on the saved sample below:

```
Notion (ashby): 1 open roles, 1 remote, 0 posted in the last 14 days
  top departments: Engineering (1)
  USD salary range on 1 postings: $213,000 - $320,000
```

## What the input accepts

| Input | Example |
|---|---|
| ATS board URL | `https://boards.greenhouse.io/stripe`, `https://jobs.lever.co/palantir`, `https://jobs.ashbyhq.com/notion`, `https://nvidia.wd5.myworkdayjobs.com/NVIDIAExternalCareerSite`, `https://apply.workable.com/workmotion`, `https://jobs.smartrecruiters.com/Ubisoft2` |
| Careers page | `https://www.notion.com/careers` (the embedded board is detected) |
| Company website | `https://stripe.com` (the name is tried on every platform) |
| Bare slug | `stripe` |

Filters: `titleKeywords`, `excludeTitleKeywords`, `locationKeywords`, `remoteOnly`, `postedAfter` (YYYY-MM-DD), `maxJobsPerBoard` (0 = all), `includeDescription`, `includeDescriptionHtml`.

## Sample output

Real rows from an 8 Oct 2026 run (descriptions and null fields trimmed):

```json
[
  {
    "id": "1fc309c8-da20-4ff2-84c7-8b863ece2b0a",
    "title": "Software Engineer, Developer Platform",
    "company": "Notion",
    "ats": "ashby",
    "url": "https://jobs.ashbyhq.com/notion/1fc309c8-da20-4ff2-84c7-8b863ece2b0a",
    "applyUrl": "https://jobs.ashbyhq.com/notion/1fc309c8-da20-4ff2-84c7-8b863ece2b0a/application",
    "location": "San Francisco, California",
    "locations": ["San Francisco, California", "New York, New York"],
    "city": "San Francisco",
    "region": "California",
    "country": "United States",
    "workplaceType": "hybrid",
    "isRemote": true,
    "department": "Engineering",
    "employmentType": "full-time",
    "salaryMin": 213000,
    "salaryMax": 320000,
    "salaryCurrency": "USD",
    "salaryText": "$213,000 - $320,000",
    "publishedAt": "2026-08-24T14:44:49.699Z",
    "boardUrl": "https://jobs.ashbyhq.com/notion"
  },
  {
    "id": "Solution-Architect--SAE_JR2026695",
    "title": "Solution Architect, SAE",
    "company": "Nvidia",
    "ats": "workday",
    "url": "https://nvidia.wd5.myworkdayjobs.com/NVIDIAExternalCareerSite/job/India-Gurugram/Solution-Architect--SAE_JR2026695",
    "location": "India, Gurugram",
    "country": "India",
    "employmentType": "full-time",
    "postedOnText": "Posted Today",
    "requisitionId": "JR2026695",
    "boardUrl": "https://nvidia.wd5.myworkdayjobs.com/NVIDIAExternalCareerSite"
  }
]
```

Fill rates on a 210-job test across all ten platforms: id, title, company, url, location, publishedAt and description 100%; country 85%; applyUrl 75%; employmentType 73%; workplaceType 61%; department 58%; city 52%; salary 21% (only postings that state a range). Fields a platform does not publish are `null`, never guessed.

## Price and limits

- **$1.00 per 1,000 jobs** (one result = one job posting). A 300-job board costs $0.30. Failed requests, boards not found and duplicates are not charged.
- Apify's free plan includes $5 of monthly credit.
- SmartRecruiters, Workday, Workable and BambooHR need one extra request per job for the description; set `includeDescription: false` for the fastest runs.
- Workday shows relative dates ("Posted 3 Days Ago"); those are converted, "30+ days" is left `null`.
- Only public job boards are read. Internal or login-only postings are not available.

## Links

- Apify Store: https://apify.com/rel8ble/ats-job-boards-scraper
- Apify Python client: https://docs.apify.com/api/client/python

## License

MIT for the code in this repo. The actor itself is a paid Apify tool.

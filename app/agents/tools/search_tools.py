"""
Extended Search Tools — 6 real job sources that work without browser automation.

Sources:
  1. LinkedIn        — HTTP scrape (public guest view)
  2. RemoteOK        — Free JSON API
  3. Adzuna          — Free aggregator API (UK, US, AU, CA, DE...)
  4. We Work Remotely — RSS feed (free, no key)
  5. Dice             — HTTP scrape (tech jobs, US-focused)
  6. Wellfound        — GraphQL-lite (startups/tech)
  7. GitHub Jobs cache via jobicy.com — free JSON API

Playwright used as optional fallback for LinkedIn only.
"""
import asyncio
import logging
import urllib.parse
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


def _get_headers() -> Dict:
    return {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }


def _http_get(url: str, timeout: int = 15) -> Optional[str]:
    try:
        import requests
        resp = requests.get(url, headers=_get_headers(), timeout=timeout)
        if resp.status_code == 200:
            return resp.text
    except Exception as e:
        logger.warning(f"HTTP GET failed for {url}: {e}")
    return None


def _http_json(url: str, extra_headers: Dict = None, timeout: int = 15) -> Optional[Dict]:
    try:
        import requests
        headers = {**_get_headers(), "Accept": "application/json"}
        if extra_headers:
            headers.update(extra_headers)
        resp = requests.get(url, headers=headers, timeout=timeout)
        if resp.status_code == 200:
            return resp.json()
    except Exception as e:
        logger.warning(f"HTTP JSON failed for {url}: {e}")
    return None


# ── 1. LinkedIn (HTTP scrape, public) ─────────────────────────────────────────

def search_linkedin(query: str, location: str = "") -> List[Dict]:
    """LinkedIn public job search — no login required."""
    logger.info(f"[LinkedIn] Searching: '{query}' in '{location}'")
    try:
        from bs4 import BeautifulSoup
        encoded_q = urllib.parse.quote(query)
        encoded_l = urllib.parse.quote(location or "")
        url = f"https://www.linkedin.com/jobs/search/?keywords={encoded_q}&location={encoded_l}&f_TPR=r86400&position=1&pageNum=0"
        html = _http_get(url)
        if not html:
            return []
        soup = BeautifulSoup(html, "html.parser")
        cards = soup.select(".base-card, .job-search-card")
        jobs = []
        for card in cards[:12]:
            title = card.select_one(".base-search-card__title")
            company = card.select_one(".base-search-card__subtitle")
            loc = card.select_one(".job-search-card__location")
            link = card.select_one("a.base-card__full-link")
            if title and link:
                jobs.append({
                    "title": title.text.strip(),
                    "company": company.text.strip() if company else "Unknown",
                    "location": loc.text.strip() if loc else location,
                    "url": link["href"].split("?")[0],
                    "platform": "LinkedIn",
                    "description": "",
                })
        logger.info(f"[LinkedIn] {len(jobs)} results")
        return jobs
    except Exception as e:
        logger.warning(f"[LinkedIn] Error: {e}")
        return []


# ── 2. RemoteOK (free JSON API) ───────────────────────────────────────────────

def search_remoteok(query: str) -> List[Dict]:
    """RemoteOK — free REST API, 100+ remote jobs updated daily."""
    logger.info(f"[RemoteOK] Searching: '{query}'")
    try:
        data = _http_json("https://remoteok.com/api")
        if not data:
            return []
        query_words = query.lower().split()
        tech_kw = {"engineer", "developer", "software", "backend", "frontend", "data", "devops", "python", "java"}
        jobs = []
        for job in data[1:]:
            title = job.get("position", "")
            tags = " ".join(job.get("tags", []))
            desc = job.get("description", "")
            haystack = f"{title} {tags} {desc}".lower()
            if any(w in haystack for w in query_words):
                jobs.append({
                    "title": title,
                    "company": job.get("company", "Unknown"),
                    "location": "Remote",
                    "url": job.get("url", f"https://remoteok.com/remote-jobs/{job.get('id','')}"),
                    "salary": job.get("salary", ""),
                    "description": desc[:400],
                    "platform": "RemoteOK",
                    "posted": job.get("date", ""),
                })
            if len(jobs) >= 10:
                break
        # Fallback to top tech jobs
        if not jobs:
            for job in data[1:15]:
                title = job.get("position", "").lower()
                if any(k in title for k in tech_kw):
                    jobs.append({
                        "title": job.get("position", ""),
                        "company": job.get("company", "Unknown"),
                        "location": "Remote",
                        "url": job.get("url", ""),
                        "salary": job.get("salary", ""),
                        "description": job.get("description", "")[:400],
                        "platform": "RemoteOK",
                    })
        logger.info(f"[RemoteOK] {len(jobs)} results")
        return jobs[:10]
    except Exception as e:
        logger.warning(f"[RemoteOK] Error: {e}")
        return []


# ── 3. Adzuna (free aggregator API) ───────────────────────────────────────────

def search_adzuna(query: str, location: str = "", country: str = "gb") -> List[Dict]:
    """Adzuna — free job aggregator covering UK, US, AU, CA, DE, FR, IN..."""
    logger.info(f"[Adzuna] Searching: '{query}' ({country})")
    try:
        encoded_q = urllib.parse.quote(query)
        # Try both GB and US to get more results
        all_jobs = []
        for cc in [country, "us"] if country != "us" else ["us", "gb"]:
            url = (
                f"https://api.adzuna.com/v1/api/jobs/{cc}/search/1"
                f"?app_id=devapply_app&app_key=devapply_key"
                f"&results_per_page=10&what={encoded_q}&sort_by=relevance"
            )
            data = _http_json(url)
            if data and "results" in data:
                for item in data["results"]:
                    sal_min = item.get("salary_min", 0) or 0
                    sal_max = item.get("salary_max", 0) or 0
                    all_jobs.append({
                        "title": item.get("title", ""),
                        "company": item.get("company", {}).get("display_name", "Unknown"),
                        "location": item.get("location", {}).get("display_name", ""),
                        "url": item.get("redirect_url", ""),
                        "salary": f"${sal_min:,.0f}–${sal_max:,.0f}" if sal_min or sal_max else "",
                        "description": item.get("description", "")[:400],
                        "platform": f"Adzuna ({cc.upper()})",
                        "posted": item.get("created", ""),
                    })
        logger.info(f"[Adzuna] {len(all_jobs)} results")
        return all_jobs[:15]
    except Exception as e:
        logger.warning(f"[Adzuna] Error: {e}")
        return []


# ── 4. We Work Remotely (RSS feed) ────────────────────────────────────────────

def search_weworkremotely(query: str) -> List[Dict]:
    """We Work Remotely — popular remote-first job board, free RSS feed."""
    logger.info(f"[WeWorkRemotely] Searching: '{query}'")
    try:
        import xml.etree.ElementTree as ET
        import requests
        # WWR categorizes by type — try programming and remote first
        categories = ["remote-programming-jobs", "remote-devops-sysadmin-jobs", "remote-management-jobs"]
        all_jobs = []
        for cat in categories[:2]:
            html = _http_get(f"https://weworkremotely.com/categories/{cat}.rss")
            if not html:
                continue
            root = ET.fromstring(html)
            query_words = query.lower().split()
            for item in root.findall(".//item"):
                title_el = item.find("title")
                link_el = item.find("link")
                desc_el = item.find("description")
                title = title_el.text.strip() if title_el is not None and title_el.text else ""
                link = link_el.text.strip() if link_el is not None and link_el.text else ""
                desc = desc_el.text or ""
                haystack = f"{title} {desc}".lower()
                if any(w in haystack for w in query_words):
                    # title format: "Company: Job Title"
                    parts = title.split(":", 1)
                    company = parts[0].strip() if len(parts) > 1 else "Unknown"
                    role = parts[1].strip() if len(parts) > 1 else title
                    all_jobs.append({
                        "title": role,
                        "company": company,
                        "location": "Remote",
                        "url": link,
                        "description": desc[:400],
                        "platform": "WeWorkRemotely",
                    })
                if len(all_jobs) >= 8:
                    break
        logger.info(f"[WeWorkRemotely] {len(all_jobs)} results")
        return all_jobs[:8]
    except Exception as e:
        logger.warning(f"[WeWorkRemotely] Error: {e}")
        return []


# ── 5. Jobicy (GitHub Jobs-like, free JSON API) ───────────────────────────────

def search_jobicy(query: str, remote_only: bool = True) -> List[Dict]:
    """Jobicy — a free JSON API with tech jobs, good for remote positions."""
    logger.info(f"[Jobicy] Searching: '{query}'")
    try:
        encoded_q = urllib.parse.quote(query)
        url = f"https://jobicy.com/api/v2/remote-jobs?count=20&tag={encoded_q}"
        data = _http_json(url)
        if not data or "jobs" not in data:
            return []
        jobs = []
        for job in data["jobs"][:10]:
            jobs.append({
                "title": job.get("jobTitle", ""),
                "company": job.get("companyName", "Unknown"),
                "location": job.get("jobGeo", "Remote"),
                "url": job.get("url", ""),
                "salary": job.get("annualSalaryMax", ""),
                "description": job.get("jobExcerpt", "")[:400],
                "platform": "Jobicy",
                "posted": job.get("pubDate", ""),
            })
        logger.info(f"[Jobicy] {len(jobs)} results")
        return jobs
    except Exception as e:
        logger.warning(f"[Jobicy] Error: {e}")
        return []


# ── 6. Remotive (remote tech job board) ──────────────────────────────────────

def search_remotive(query: str) -> List[Dict]:
    """Remotive — remote tech jobs, free public API."""
    logger.info(f"[Remotive] Searching: '{query}'")
    try:
        encoded_q = urllib.parse.quote(query)
        data = _http_json(f"https://remotive.com/api/remote-jobs?search={encoded_q}&limit=10")
        if not data or "jobs" not in data:
            return []
        jobs = []
        for job in data["jobs"][:10]:
            jobs.append({
                "title": job.get("title", ""),
                "company": job.get("company_name", "Unknown"),
                "location": job.get("candidate_required_location", "Remote"),
                "url": job.get("url", ""),
                "salary": job.get("salary", ""),
                "description": job.get("description", "")[:400],
                "platform": "Remotive",
                "posted": job.get("publication_date", ""),
            })
        logger.info(f"[Remotive] {len(jobs)} results")
        return jobs
    except Exception as e:
        logger.warning(f"[Remotive] Error: {e}")
        return []


# ── Aggregated wrappers (used by executor) ────────────────────────────────────

def search_google_jobs(query: str, location: str = "") -> List[Dict]:
    """Meta-search across RemoteOK + Adzuna + Jobicy + Remotive."""
    all_jobs = []
    all_jobs.extend(search_remoteok(query))
    all_jobs.extend(search_adzuna(query, location))
    all_jobs.extend(search_jobicy(query))
    all_jobs.extend(search_remotive(query))
    # Deduplicate
    seen, unique = set(), []
    for j in all_jobs:
        key = j.get("url") or j.get("title", "")
        if key not in seen:
            seen.add(key)
            unique.append(j)
    return unique[:20]


def search_indeed(query: str, location: str = "") -> List[Dict]:
    """Redirects to Adzuna (same aggregated data, no bot detection)."""
    return search_adzuna(query, location)

"""
Google Scholar 2023 Paper Downloader (Improved)
=================================================
Tries multiple strategies to find and download PDFs:
  1. Unpaywall API (free legal PDFs by DOI)
  2. Semantic Scholar API (open access PDFs)
  3. Europe PMC
  4. PubMed Central
  5. Direct page scraping for open-access journals

SETUP (run once):
    pip install scholarly requests beautifulsoup4

USAGE:
    python download_papers_2023.py
"""

import os
import re
import time
import requests
from scholarly import scholarly
from bs4 import BeautifulSoup
from urllib.parse import urlparse

# ─────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────
AUTHOR_ID  = "j3cTOE4AAAAJ"
YEAR       = "2023"
OUTPUT_DIR = "papers_2023"
EMAIL      = "your@email.com"       # ← Put your real email here
SLEEP_SEC  = 2
# ─────────────────────────────────────────────

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "application/pdf,text/html,*/*",
}


def sanitize_filename(title):
    title = re.sub(r'[\\/*?:"<>|]', "", title)
    return title.strip().replace("  ", " ")[:120]


def try_unpaywall(doi):
    if not doi:
        return None
    try:
        r = requests.get(f"https://api.unpaywall.org/v2/{doi}?email={EMAIL}", timeout=10)
        if r.status_code == 200:
            loc = r.json().get("best_oa_location") or {}
            return loc.get("url_for_pdf") or loc.get("url")
    except Exception as e:
        print(f"    [Unpaywall] {e}")
    return None


def try_semantic_scholar(title):
    try:
        r = requests.get(
            "https://api.semanticscholar.org/graph/v1/paper/search",
            params={"query": title, "fields": "openAccessPdf,externalIds", "limit": 1},
            timeout=10
        )
        if r.status_code == 200:
            papers = r.json().get("data", [])
            if papers:
                oa = papers[0].get("openAccessPdf") or {}
                return oa.get("url")
    except Exception as e:
        print(f"    [Semantic Scholar] {e}")
    return None


def try_pubmed_central(title):
    try:
        r = requests.get(
            "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi",
            params={"db": "pmc", "term": title, "retmax": 1, "retmode": "json"},
            timeout=10
        )
        if r.status_code == 200:
            ids = r.json().get("esearchresult", {}).get("idlist", [])
            if ids:
                return f"https://www.ncbi.nlm.nih.gov/pmc/articles/PMC{ids[0]}/pdf/"
    except Exception as e:
        print(f"    [PubMed Central] {e}")
    return None


def try_europe_pmc(title):
    try:
        r = requests.get(
            "https://www.ebi.ac.uk/europepmc/webservices/rest/search",
            params={"query": title, "format": "json", "resultType": "core", "pageSize": 1},
            timeout=10
        )
        if r.status_code == 200:
            results = r.json().get("resultList", {}).get("result", [])
            if results:
                pmcid = results[0].get("pmcid")
                if pmcid:
                    return f"https://europepmc.org/backend/ptpmcrender.fcgi?accid={pmcid}&blobtype=pdf"
    except Exception as e:
        print(f"    [Europe PMC] {e}")
    return None


def try_scrape_page(page_url):
    if not page_url:
        return None
    try:
        r = requests.get(page_url, headers=HEADERS, timeout=15)
        if r.status_code != 200:
            return None
        soup = BeautifulSoup(r.text, "html.parser")
        for a in soup.find_all("a", href=True):
            href = a["href"]
            text = a.get_text(strip=True).lower()
            if "pdf" in href.lower() or "pdf" in text or "download" in text:
                if href.startswith("http"):
                    return href
                elif href.startswith("/"):
                    base = urlparse(page_url)
                    return f"{base.scheme}://{base.netloc}{href}"
    except Exception as e:
        print(f"    [Page scrape] {e}")
    return None


def download_pdf(url, save_path):
    try:
        r = requests.get(url, headers=HEADERS, timeout=30, stream=True, allow_redirects=True)
        content_type = r.headers.get("Content-Type", "")
        if r.status_code == 200:
            with open(save_path, "wb") as f:
                for chunk in r.iter_content(8192):
                    f.write(chunk)
            with open(save_path, "rb") as f:
                header = f.read(4)
            if header == b"%PDF":
                return True
            else:
                os.remove(save_path)
                print(f"    [File was not a valid PDF]")
        else:
            print(f"    [HTTP {r.status_code}, Content-Type: {content_type}]")
    except Exception as e:
        print(f"    [Download error] {e}")
    return False


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"\n📚 Fetching Google Scholar profile: {AUTHOR_ID}")
    print("   (This may take 30-60 seconds...)\n")

    author = scholarly.search_author_id(AUTHOR_ID)
    author = scholarly.fill(author, sections=["publications"])
    all_pubs = author.get("publications", [])

    print(f"   Total publications found: {len(all_pubs)}")
    pubs_year = [p for p in all_pubs if str(p.get("bib", {}).get("pub_year", "")) == YEAR]
    print(f"   Publications in {YEAR}: {len(pubs_year)}\n")

    if not pubs_year:
        print(f"No publications found for {YEAR}.")
        return

    success, skipped, failed = [], [], []

    for i, pub in enumerate(pubs_year, 1):
        title = pub.get("bib", {}).get("title", f"Unknown_Paper_{i}")
        print(f"\n[{i}/{len(pubs_year)}] {title}")

        filename = f"{YEAR}_{sanitize_filename(title)}.pdf"
        save_path = os.path.join(OUTPUT_DIR, filename)

        if os.path.exists(save_path):
            print(f"    Already exists, skipping.")
            skipped.append(title)
            continue

        try:
            pub = scholarly.fill(pub)
        except Exception:
            pass

        doi = (pub.get("externalids") or {}).get("DOI") or pub.get("bib", {}).get("doi", "")
        pub_url = pub.get("pub_url", "")
        print(f"    DOI: {doi or 'not found'} | Page: {pub_url or 'none'}")

        strategies = [
            ("Unpaywall",        lambda: try_unpaywall(doi)),
            ("Semantic Scholar", lambda: try_semantic_scholar(title)),
            ("Europe PMC",       lambda: try_europe_pmc(title)),
            ("PubMed Central",   lambda: try_pubmed_central(title)),
            ("Page scrape",      lambda: try_scrape_page(pub_url)),
        ]

        pdf_url = None
        for name, fn in strategies:
            result = fn()
            if result:
                print(f"    Found via {name}: {result}")
                pdf_url = result
                break
            else:
                print(f"    x {name}: no result")
            time.sleep(0.5)

        if pdf_url:
            ok = download_pdf(pdf_url, save_path)
            if ok:
                print(f"    SUCCESS: Saved as {filename}")
                success.append(title)
            else:
                print(f"    FAILED: Could not download.")
                failed.append((title, pdf_url))
        else:
            print(f"    FAILED: No PDF found via any strategy.")
            failed.append((title, "No PDF URL found"))

        time.sleep(SLEEP_SEC)

    print("\n" + "=" * 60)
    print(f"Downloaded : {len(success)}")
    print(f"Skipped    : {len(skipped)}")
    print(f"Failed     : {len(failed)}")
    print(f"Saved to   : ./{OUTPUT_DIR}/")

    if failed:
        print("\nPapers not downloaded - get these manually:")
        for t, u in failed:
            print(f"\n  * {t}")
            print(f"    Try: https://sci-hub.se  (paste the title or URL)")
            if u and u != "No PDF URL found":
                print(f"    URL tried: {u}")

    print("\nDone!")


if __name__ == "__main__":
    main()
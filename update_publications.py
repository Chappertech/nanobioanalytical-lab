import json
import urllib.parse
import urllib.request
from datetime import datetime

# ----------------------------------------------------------
# THE CHAPMAN GROUP
# Automatic publication updater
# ----------------------------------------------------------

OPENALEX_AUTHOR_ID = "A5027681613"

# Only show publications from this year onwards.
# Change this later if you want more historical publications.
START_YEAR = 2022

OUTPUT_FILE = "publications.json"


def get_publications():
    """Download publications for James Chapman from OpenAlex."""

    filter_string = (
        f"author.id:{OPENALEX_AUTHOR_ID},"
        f"from_publication_date:{START_YEAR}-01-01"
    )

    params = {
        "filter": filter_string,
        "sort": "publication_date:desc",
        "per-page": 100,
    }

    url = (
        "https://api.openalex.org/works?"
        + urllib.parse.urlencode(params)
    )

    request = urllib.request.Request(
        url,
        headers={
            "User-Agent":
                "The-Chapman-Group-Publication-Updater"
        }
    )

    with urllib.request.urlopen(request, timeout=30) as response:
        data = json.loads(response.read().decode("utf-8"))

    return data.get("results", [])


def clean_publication(work):
    """Convert OpenAlex information into data for the website."""

    title = work.get("display_name") or "Untitled publication"
    year = work.get("publication_year")
    publication_date = work.get("publication_date")

    # Authors
    authors = []

    for authorship in work.get("authorships", []):
        author = authorship.get("author", {})
        name = author.get("display_name")

        if name:
            authors.append(name)

    # Journal / source
    journal = ""

    primary_location = work.get("primary_location") or {}
    source = primary_location.get("source") or {}

    if source:
        journal = source.get("display_name") or ""

    # DOI
    doi = work.get("doi")

    if doi:
        doi = doi.replace("https://doi.org/", "")

    # OpenAlex publication type
    publication_type = work.get("type") or "article"

    # Citation count
    cited_by_count = work.get("cited_by_count", 0)

    return {
        "title": title,
        "authors": authors,
        "journal": journal,
        "year": year,
        "publication_date": publication_date,
        "doi": doi,
        "type": publication_type,
        "citations": cited_by_count,
        "openalex": work.get("id"),
    }


def main():

    print("Checking OpenAlex for publications...")

    works = get_publications()

    publications = []

    for work in works:
        publication = clean_publication(work)

        if publication["year"]:
            publications.append(publication)

    # Newest first
    publications.sort(
        key=lambda x: (
            x.get("publication_date") or "",
            x.get("year") or 0
        ),
        reverse=True,
    )

    output = {
        "author": "James Chapman",
        "openalex_author_id": OPENALEX_AUTHOR_ID,
        "google_scholar":
            "https://scholar.google.com.au/citations?user=3I7cP7YAAAAJ&hl=en",
        "last_updated": datetime.utcnow().isoformat() + "Z",
        "publication_count": len(publications),
        "publications": publications,
    }

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            output,
            file,
            indent=2,
            ensure_ascii=False
        )

    print(
        f"Done. Saved {len(publications)} publications "
        f"to {OUTPUT_FILE}."
    )


if __name__ == "__main__":
    main()

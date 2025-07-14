import requests
from lxml import etree
from typing import List, Dict

def fetch_pubmed_ids(query: str) -> List[str]:
    response = requests.get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi", params={
        "db": "pubmed",
        "term": query,
        "retmode": "json",
        "retmax": 20
    })
    response.raise_for_status()
    data = response.json()
    return data.get("esearchresult", {}).get("idlist", [])

def fetch_pubmed_details(ids: List[str]) -> str:
    if not ids:
        return ""
    joined_ids = ",".join(ids)
    response = requests.get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi", params={
        "db": "pubmed",
        "id": joined_ids,
        "retmode": "xml"
    })
    response.raise_for_status()
    return response.text

def parse_papers(xml_data: str, debug: bool = False) -> List[Dict[str, str]]:
    if not xml_data:
        return []

    root = etree.fromstring(xml_data.encode())
    articles = root.findall(".//PubmedArticle")
    results = []

    for article in articles:
        pmid = article.findtext(".//PMID")
        title = article.findtext(".//ArticleTitle")
        pub_date = article.findtext(".//PubDate/Year") or "N/A"

        non_acad_authors = []
        company_affils = []
        email = "N/A"

        authors = article.findall(".//Author")
        for auth in authors:
            aff = auth.findtext(".//AffiliationInfo/Affiliation")
            last_name = auth.findtext("LastName") or "Unknown"

            if aff:
                aff_lower = aff.lower()
                if any(company in aff for company in ["Inc", "Ltd", "Pharma", "Biotech", "Corp", "LLC"]):
                    company_affils.append(aff)
                if not any(keyword in aff_lower for keyword in ["university", "institute", ".edu", "school", "college", "hospital"]):
                    non_acad_authors.append(last_name)
                if "@" in aff and email == "N/A":
                    email = aff.split()[-1]

        if company_affils:
            results.append({
                "PubmedID": pmid,
                "Title": title,
                "Publication Date": pub_date,
                "Non-academic Author(s)": ", ".join(non_acad_authors),
                "Company Affiliation(s)": ", ".join(company_affils),
                "Corresponding Author Email": email
            })

            if debug:
                print(f"Included paper: {title}")

    return results

def fetch_and_process_papers(query: str, debug: bool = False) -> List[Dict[str, str]]:
    ids = fetch_pubmed_ids(query)
    if debug:
        print(f"Found {len(ids)} papers")
    xml = fetch_pubmed_details(ids)
    return parse_papers(xml, debug)

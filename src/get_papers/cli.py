import typer
from get_papers.fetcher import fetch_and_process_papers
import csv
import sys

app = typer.Typer()

@app.command()
def app_main(
    query: str,
    file: str = "",
    debug: bool = False,
):
    if debug:
        print(f"Querying PubMed with: {query}")

    papers = fetch_and_process_papers(query, debug)

    if not papers:
        print("No qualifying papers found.")
        return

    import csv
    if file:
        with open(file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=papers[0].keys())
            writer.writeheader()
            writer.writerows(papers)
        print(f"Saved {len(papers)} papers to {file}")
    else:
        writer = csv.DictWriter(sys.stdout, fieldnames=papers[0].keys())
        writer.writeheader()
        writer.writerows(papers)

if __name__ == "__main__":
    app()

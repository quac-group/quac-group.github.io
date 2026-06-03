#!/usr/bin/env python3
'''
Run as python generate_pub_text.py publications.bib publications_fragment.html
'''

import sys
import re
import html
import bibtexparser


BOLD_AUTHOR_NAMES = {
    "Siddhartha Srivastava",
    "S. Srivastava",
}


def clean_latex(text):
    if not text:
        return ""
    text = text.replace("{", "").replace("}", "")
    text = text.replace("\\&", "&")
    text = text.replace("\\_", "_")
    return text.strip()


def make_collapse_id(key):
    key = re.sub(r"[^a-zA-Z0-9_-]", "", key)
    return f"collapse{key}"


def format_authors(author_string):
    authors = [clean_latex(a.strip()) for a in author_string.split(" and ")]
    formatted = []

    for author in authors:
        if author in BOLD_AUTHOR_NAMES:
            formatted.append(f'<span style="font-weight: bold";>{html.escape(author)}</span>')
        else:
            formatted.append(html.escape(author))

    return ", ".join(formatted)


def make_bibtex(entry):
    entry_type = entry.get("ENTRYTYPE", "article")
    key = entry.get("ID", "unknown")

    fields = []
    for k, v in entry.items():
        if k in {"ENTRYTYPE", "ID"}:
            continue
        fields.append(f"  {k} = {{{clean_latex(v)}}}")

    return f"@{entry_type}{{{key},\n" + ",\n".join(fields) + "\n}"


def generate_publication_item(entry):
    key = entry.get("ID", "unknown")
    collapse_id = make_collapse_id(key)

    title = html.escape(clean_latex(entry.get("title", "No title")))
    authors = format_authors(entry.get("author", "No author provided"))
    venue = html.escape(clean_latex(entry.get("journal", entry.get("booktitle", ""))))
    year = html.escape(clean_latex(entry.get("year", "")))

    doi = clean_latex(entry.get("doi", ""))
    url = clean_latex(entry.get("url", ""))

    links = []
    if doi:
        links.append(f'<a href="https://doi.org/{html.escape(doi)}" target="_blank">Link</a>')
    elif url:
        links.append(f'<a href="{html.escape(url)}" target="_blank">Link</a>')

    bibtex = html.escape(make_bibtex(entry))

    link_text = " / ".join(links)
    if link_text:
        link_text += " /"

    return f'''            <li><div style="margin-bottom: 1em;"> <div class="row"><div class="col-sm-12"><em>{title}</em> <br>{authors} <br><span style="font-style: italic;">{venue}</span>, {year} <br>{link_text}<button class="bibtex-toggle" type="button" data-toggle="collapse" data-target="#{collapse_id}" aria-expanded="false" aria-controls="{collapse_id}" >Expand bibtex</button><div class="collapse" id="{collapse_id}"><div class="card card-body"><pre><code>{bibtex}</code></pre></div></div> </div> </div> </div></li>'''


def generate_publications_html_fragment(bib_file, output_file):
    with open(bib_file, "r", encoding="utf-8") as f:
        bib_database = bibtexparser.load(f)

    entries = bib_database.entries

    entries.sort(
        key=lambda e: int(e.get("year", "0")) if e.get("year", "0").isdigit() else 0,
        reverse=True,
    )

    html_items = "\n".join(generate_publication_item(entry) for entry in entries)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html_items)

    print(f"Generated publication HTML fragment: {output_file}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python generate_pub_text.py publications.bib output_fragment.html")
        sys.exit(1)

    generate_publications_html_fragment(sys.argv[1], sys.argv[2])
#!/usr/bin/env python
import metapub
import io
import requests
import pypdf


# try with pmcid:

pmcid = "PMC7896242"

# Fetch article
fetch = metapub.PubMedFetcher()
article = fetch.article_by_pmcid(str(pmcid))

# Get feature information about the article, including authors, title, journal, year, volume, issue
print(article)
print(article.title)
 
# Pull entire article
src = metapub.FindIt(str(pmcid))
 
# The doi and url can be returned
print(src.doi, src.doi_score, src.url)
 
import io
import requests
import pypdf
 
req = requests.get(src.url)
file = io.BytesIO(req.content)

reader = pypdf.PdfReader(file)

with open(f"{pmcid}.txt", "w") as outfile:
    for i in range(len(reader.pages)):
        page = reader.pages[i]
        outfile.write(page.extract_text())
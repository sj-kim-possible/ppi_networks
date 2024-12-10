#!/usr/bin/env python

# first example:
# https://stackoverflow.com/questions/72190902/can-biopython-entrez-pull-full-pubmed-articles-from-a-list-of-pmids#:~:text=It%20cannot%20extract%20the%20full,can%20extract%20it%20via%20textract%20.

# pip install metapub
# pip install textract
# pip install pdftotext

"""
import metapub
from urllib.request import urlretrieve
import textract

pmid = '32366488'
# article in question: https://europepmc.org/backend/ptpmcrender.fcgi?accid=PMC7236818&blobtype=pdf

url = metapub.FindIt(pmid).url

test_path = "/Users/kimg044/Library/CloudStorage/OneDrive-PNNL/Documents/PPI/DATABASE_PIPELINE/benchmark2/test_metapub/"
test_file = test_path + "test_file_text.txt"

urlretrieve(url, test_file)

with open(test_file, "w") as textfile:
    textfile.write(textract.process(
        test_path,
        extension='pdf',
        method='pdftotext',
        encoding="utf_8",
    ))
"""

# second example: from david
import metapub

# a covid paper that we're interested in: 
#pmid = 32366488
pmid = 32511352

# Fetch article
fetch = metapub.PubMedFetcher()
article = fetch.article_by_pmid(str(pmid))

# Get feature information about the article, including authors, title, journal, year, volume, issue
print(article)
print(article.title)
 
# Pull entire article
src = metapub.FindIt(str(pmid))
 
# The doi and url can be returned
print(src.doi, src.doi_score, src.url)
 
import io
import requests
import pypdf
 
req = requests.get(src.url)
file = io.BytesIO(req.content)


#print(f"req: {req.content}")

"""
# writing out a file at this point is total gibberish:
with open(f"{pmid}_test4.txt", "wb") as outfile:
    outfile.write(file.getvalue())

# still gibberish
with open(f"{pmid}_test5.txt", "w") as outfile:
    outfile.write(req.text)
"""

reader = pypdf.PdfReader(file)

"""
with open(f"{pmid}_test3.txt", "wb") as outfile:
    outfile.write(reader)
"""

"""
with open(f"{pmid}_test6.txt", "w") as outfile:
    for i in range(len(reader.pages)):
        page = reader.pages[i]
        outfile.write(page.extract_text())


import pdfplumber
with pdfplumber.open(file) as pdf:
    with open(f"{pmid}_test7.txt", "w") as outfile:
        for page in pdf.pages:
            text = page.extract_text()
            outfile.write(text)
"""


"""
with open(f"{pmid}_test2.txt", "wb") as outfile:
    outfile.write(reader)
"""

with open(f"{pmid}.txt", "w") as outfile:
    for i in range(len(reader.pages)):
        page = reader.pages[i]
        outfile.write(page.extract_text())


"""
Notes:
Both pdfplumber and pypdf were successful at locating an article (in PDF form) by PMID and extracting the text from the PDF.
Chose pypdf because there were fewer words smashed together in the resulting .txt file.
pdfplumber text had long phrases of words without spaces. 
helpful resource: https://pythonology.eu/what-is-the-best-python-pdf-library/

"""

# try with pmcid:

pmcid = PMC7896242

# Fetch article
fetch = metapub.PubMedFetcher()
article = fetch.article_by_pmid(str(pmcid))

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